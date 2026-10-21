from __future__ import annotations

from dataclasses import replace
from pathlib import Path
import tempfile
import unittest

from scripts.publish_public_site import (
    NOETHER_VIDEO_ASSETS,
    NOETHER_VIDEO_FOLDER,
    REVIEWS,
    SITE_DIR,
    copy_public_file,
    prune_public_support_files,
    public_asset_names,
    sanitize_for_public,
    validate_local_references,
    validate_public_support_files,
    validate_video_binary,
    validate_video_embed,
)


def mp4_box(kind: bytes, payload: bytes = b"") -> bytes:
    return (len(payload) + 8).to_bytes(4, "big") + kind + payload


def metadata_mp4(*, user_metadata: bytes = b"", handler: bytes = b"VideoHandler\0") -> bytes:
    # Minimal box fixtures exercise publication metadata checks, not decoding.
    # Actual master decoding is the renderer's separate acceptance gate.
    track = mp4_box(b"trak", mp4_box(b"mdia", mp4_box(b"hdlr", bytes(24) + handler)))
    return (
        mp4_box(b"ftyp", b"isom\0\0\2\0isomiso2avc1mp41")
        + mp4_box(b"moov", track + user_metadata)
        + mp4_box(b"mdat", b"encoded-frame-placeholder")
    )


def webp_chunk(kind: bytes, payload: bytes = b"pixels") -> bytes:
    return kind + len(payload).to_bytes(4, "little") + payload + (b"\0" if len(payload) % 2 else b"")


def metadata_webp(extra: bytes = b"") -> bytes:
    body = b"WEBP" + webp_chunk(b"VP8 ") + extra
    return b"RIFF" + len(body).to_bytes(4, "little") + body


class PublicSiteVideoTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)
        self.dist = self.directory / "dist"
        self.public = self.directory / "public"
        self.dist.mkdir()
        self.public.mkdir()
        self.review = next(r for r in REVIEWS if r.folder == NOETHER_VIDEO_FOLDER)

    def bundle(self, language: str = "ko", *, direct_src: bool = False) -> str:
        names = NOETHER_VIDEO_ASSETS[language]
        (self.dist / names["video"]).write_bytes(metadata_mp4())
        (self.dist / names["poster"]).write_bytes(metadata_webp())
        (self.dist / names["captions"]).write_text(
            "WEBVTT\n\n00:00:00.000 --> 00:00:02.000\nEnergy is compared with its initial value.\n",
            encoding="utf-8",
        )
        (self.dist / names["transcript"]).write_text(
            "Machine-generated narration. Visual: the energy ratio is compared with one.\n",
            encoding="utf-8",
        )
        src = f' src="{names["video"]}"' if direct_src else ""
        source = "" if direct_src else f'<source src="{names["video"]}" type="video/mp4">'
        return (
            f'<html lang="{language}"><head><title>Review</title></head><body><main>'
            f'<h1>{self.review.title}</h1><video controls playsinline preload="none"'
            f' poster="{names["poster"]}"{src}>{source}'
            f'<track kind="captions" srclang="{language}" src="{names["captions"]}" default>'
            '</video>'
            f'<a href="{names["video"]}" download>MP4</a>'
            f'<a href="{names["transcript"]}">Visual transcript</a>'
            f'<img src="{names["poster"]}" alt="Static alternative">'
            '</main></body></html>'
        )

    def publish(self, source: str, language: str = "ko", review=None):
        return sanitize_for_public(
            source, self.dist, self.public, review or self.review, language,
            SITE_DIR / "reviews" / self.review.folder / ("en" if language == "en" else ""),
        )

    def test_real_embed_collects_all_four_assets_in_both_languages(self) -> None:
        for language in ("ko", "en"):
            with self.subTest(language=language):
                self.public = self.directory / f"public-{language}"
                self.public.mkdir()
                source = self.bundle(language, direct_src=language == "en")
                # Unreferenced work products must never be discovered/copied.
                (self.dist / "video-abstract-manifest.json").write_text('{"private":true}')
                (self.dist / "draft.mp4").write_bytes(b"not public")
                (self.dist / "private-notes.txt").write_text("Private e-mail subject and timestamp")
                public_html, assets = self.publish(source, language)
                expected = set(NOETHER_VIDEO_ASSETS[language].values())
                self.assertEqual(set(assets), expected)
                self.assertEqual({p.name for p in self.public.iterdir()}, expected)
                self.assertEqual(set(public_asset_names(assets, review=self.review, language=language)), expected)
                self.assertIn(f'href="{NOETHER_VIDEO_ASSETS[language]["transcript"]}"', public_html)
                self.assertNotIn("data-local-ref", public_html)
                self.assertEqual(validate_video_embed(public_html, self.public, self.review, language), expected)
                for name in expected:
                    self.assertEqual((self.public / name).read_bytes(), (self.dist / name).read_bytes())
                for name in ("video-abstract-manifest.json", "draft.mp4", "private-notes.txt"):
                    self.assertFalse((self.public / name).exists())

    def test_nonallowlisted_names_traversal_and_other_language_are_rejected(self) -> None:
        source = self.bundle()
        for replacement in (
            "draft.mp4", "../noether-abstract-ko.mp4", "%2e%2e/noether-abstract-ko.mp4",
            "subdir/noether-abstract-ko.mp4", NOETHER_VIDEO_ASSETS["en"]["video"],
        ):
            with self.subTest(reference=replacement), self.assertRaises(ValueError):
                self.publish(source.replace(NOETHER_VIDEO_ASSETS["ko"]["video"], replacement))
        with self.assertRaises(ValueError):
            self.publish(source.replace(NOETHER_VIDEO_ASSETS["ko"]["poster"], "unapproved-poster.webp"))

    def test_video_approval_does_not_extend_to_other_reviews(self) -> None:
        source = self.bundle()
        other = replace(self.review, folder="another-review")
        with self.assertRaises(ValueError):
            self.publish(source, review=other)
        extras = [NOETHER_VIDEO_ASSETS["ko"][role] for role in ("video", "captions", "transcript")]
        self.assertEqual(public_asset_names(extras), [])
        self.assertEqual(public_asset_names(extras, review=other), [])

    def test_private_caption_text_is_rejected_without_silent_rewriting(self) -> None:
        source = self.bundle()
        caption = self.dist / NOETHER_VIDEO_ASSETS["ko"]["captions"]
        header = "WEBVTT\n\n00:00:00.000 --> 00:00:02.000\n"
        for private in ("/Users/private/research.txt", "Private e-mail subject and timestamp", "http://intranet.local/draft"):
            with self.subTest(private_kind=private.split()[0]):
                caption.write_text(header + private + "\n", encoding="utf-8")
                with self.assertRaisesRegex(ValueError, "Unsafe video text"):
                    self.publish(source)
                self.assertEqual(caption.read_text(encoding="utf-8"), header + private + "\n")
                self.assertEqual(list(self.public.iterdir()), [])
        caption.write_bytes(b"WEBVTT\n\n\xff")
        with self.assertRaisesRegex(ValueError, "not UTF-8"):
            copy_public_file(caption, self.public / caption.name)

    def test_private_transcript_and_wrong_caption_timing_are_rejected(self) -> None:
        source = self.bundle()
        transcript = self.dist / NOETHER_VIDEO_ASSETS["ko"]["transcript"]
        transcript.write_text("Visual: /Users/private/source.png", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "Unsafe video text"):
            self.publish(source)
        source = self.bundle()
        caption = self.dist / NOETHER_VIDEO_ASSETS["ko"]["captions"]
        caption.write_text("WEBVTT\n\n00:00:02.000 --> 00:00:01.000\nWrong order\n", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "Unordered video captions"):
            self.publish(source)
        self.bundle()
        with self.assertRaisesRegex(ValueError, "own language"):
            self.publish(source.replace('srclang="ko"', 'srclang="en"'))

    def test_poster_references_are_validated(self) -> None:
        source = self.bundle()
        (self.dist / NOETHER_VIDEO_ASSETS["ko"]["poster"]).unlink()
        errors = validate_local_references(self.dist / "index.html", source)
        self.assertTrue(any("noether-abstract-poster-ko.webp" in error for error in errors))
        with self.assertRaisesRegex(ValueError, "Missing or nonlocal"):
            self.publish(source)

    def test_private_or_unapproved_binary_metadata_is_rejected(self) -> None:
        self.bundle()
        names = NOETHER_VIDEO_ASSETS["ko"]
        mp4 = self.dist / names["video"]
        mp4.write_bytes(metadata_mp4(handler=b"/Users/private/source\0"))
        with self.assertRaisesRegex(ValueError, "Unsafe MP4 track metadata"):
            validate_video_binary(mp4)
        title = mp4_box(b"data", bytes(8) + b"private recording name")
        meta = mp4_box(b"udta", mp4_box(b"meta", bytes(4) + mp4_box(b"ilst", mp4_box(b"\xa9nam", title))))
        mp4.write_bytes(metadata_mp4(user_metadata=meta))
        with self.assertRaisesRegex(ValueError, "Unapproved MP4 metadata field"):
            validate_video_binary(mp4)
        poster = self.dist / names["poster"]
        poster.write_bytes(metadata_webp(webp_chunk(b"EXIF", b"private camera name")))
        with self.assertRaisesRegex(ValueError, "Unapproved WebP metadata"):
            validate_video_binary(poster)

    def test_refresh_preserves_only_named_video_files_and_checks_their_text(self) -> None:
        self.bundle()
        for source in self.dist.iterdir():
            (self.public / source.name).write_bytes(source.read_bytes())
        (self.public / "working-notes.txt").write_text("private draft", encoding="utf-8")
        prune_public_support_files(self.public, review=self.review, language="ko")
        self.assertEqual({p.name for p in self.public.iterdir()}, set(NOETHER_VIDEO_ASSETS["ko"].values()))
        self.assertEqual(validate_public_support_files(self.public, review=self.review), [])
        (self.public / NOETHER_VIDEO_ASSETS["ko"]["captions"]).write_text("/Users/private/source", encoding="utf-8")
        self.assertTrue(any("Unsafe video text" in error for error in validate_public_support_files(self.public, review=self.review)))

    def test_mp4_requires_faststart_and_self_contained_media_references(self) -> None:
        self.bundle()
        movie = self.dist / NOETHER_VIDEO_ASSETS["ko"]["video"]
        movie.write_bytes(mp4_box(b"ftyp", b"isom") + mp4_box(b"mdat", b"frame") + mp4_box(b"moov"))
        with self.assertRaisesRegex(ValueError, "fast start"):
            validate_video_binary(movie)
        url = mp4_box(b"url ", bytes(4) + b"file:///Users/private/source\0")
        reference = mp4_box(b"dref", bytes(4) + (1).to_bytes(4, "big") + url)
        external_track = mp4_box(b"trak", mp4_box(b"mdia", mp4_box(b"minf", mp4_box(b"dinf", reference))))
        movie.write_bytes(metadata_mp4(user_metadata=external_track))
        with self.assertRaisesRegex(ValueError, "external data references"):
            validate_video_binary(movie)

    def test_existing_nonvideo_review_keeps_figure_and_private_link_behavior(self) -> None:
        (self.dist / "figure.svg").write_text('<svg xmlns="http://www.w3.org/2000/svg"></svg>', encoding="utf-8")
        source = '<html><head><title>Review</title></head><body><main><h1>Review</h1><img src="figure.svg"><a href="runlog.txt">note</a></main></body></html>'
        public_html, assets = self.publish(source, review=replace(self.review, folder="another-review"))
        self.assertEqual(assets, ["figure.svg"])
        self.assertNotIn('href="runlog.txt"', public_html)


if __name__ == "__main__":
    unittest.main()
