"""Legacy cover URLs survive selected review publication without registration."""
from __future__ import annotations

from contextlib import contextmanager
import hashlib
import json
import os
from pathlib import Path
import stat
import tempfile
import unittest
from unittest.mock import patch

from scripts import publish_public_site as publisher
from scripts import reader_engagement_publish as reader
import test_reader_engagement_publish as reader_fixtures


class LegacyCoverRetentionTests(unittest.TestCase):
    @contextmanager
    def fixture(self, *, dist_pins: bool = True):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            site, frontend = reader_fixtures.ReaderEnrichmentTests().fixture(root)
            review = publisher.PublicReview(
                folder="example", title="Example", subtitle="A retained cover",
                date="2026-10-23", updated="2026-10-23", category="Quantum",
                tags=("Fixture",), summary="Publication preservation fixture.",
                translations=(publisher.PublicTranslation("en", "en", "English"),),
            )
            dist = root / review.folder / "dist"
            public = site / "reviews" / review.folder
            pins: dict[str, bytes] = {}
            current: dict[str, bytes] = {}
            for language, subdir in (("ko", ""), ("en", "en")):
                source = dist / subdir
                destination = public / subdir
                source.mkdir(parents=True, exist_ok=True)
                destination.mkdir(parents=True, exist_ok=True)
                page = (
                    f'<html lang="{language}"><head><title>Example</title></head>'
                    '<body><main><h1>Example</h1><img src="hero-v4.webp" '
                    'alt="Current cover"><p>Original scientific content.</p>'
                    '</main></body></html>'
                )
                (source / "index.html").write_text(page, encoding="utf-8")
                (destination / "index.html").write_text(page, encoding="utf-8")
                payload = ("RIFFxxxxWEBPcurrent-v4-" + language).encode()
                current[subdir] = payload
                (source / "hero-v4.webp").write_bytes(payload)
                (destination / "hero-v4.webp").write_bytes(payload)
                for version in (2, 3):
                    name = f"legacy-v{version}.webp"
                    payload = f"RIFFxxxxWEBPreviewed-v{version}-{language}".encode()
                    relative = (Path("reviews/example") / subdir / name).as_posix()
                    pins[relative] = payload
                    (destination / name).write_bytes(payload)
                    if dist_pins:
                        (source / name).write_bytes(payload)
            manifest_path = site / "manifest.json"
            entry = json.loads(manifest_path.read_text(encoding="utf-8"))[0]
            entry.update(
                assets=["hero-v4.webp"], thumbnail="reviews/example/hero-v4.webp",
                translations=[{"language": "en", "label": "English",
                               "href": "reviews/example/en/index.html",
                               "assets": ["hero-v4.webp"]}],
            )
            manifest_path.write_text(json.dumps([entry]), encoding="utf-8")
            exceptions = root / "legacy-pins.json"
            exceptions.write_text(json.dumps({
                name: hashlib.sha256(payload).hexdigest() for name, payload in pins.items()
            }), encoding="utf-8")
            with patch.multiple(publisher, ROOT=root, SITE_DIR=site,
                                REVIEWS_DIR=site / "reviews", REVIEWS=(review,)), \
                    patch.object(reader, "ASSET_EXCEPTIONS", exceptions):
                yield {"root": root, "site": site, "frontend": frontend,
                       "review": review, "dist": dist, "public": public,
                       "pins": pins, "current": current, "entry": entry,
                       "exceptions": exceptions}

    @staticmethod
    def snapshot(root: Path):
        result = {}
        for path in root.rglob("*"):
            relative = path.relative_to(root).as_posix()
            if path.is_symlink():
                result[relative] = ("symlink", os.readlink(path))
            elif path.is_file():
                result[relative] = ("file", hashlib.sha256(path.read_bytes()).hexdigest())
            elif path.is_dir():
                result[relative] = ("directory",)
        return result

    def assert_retained(self, case, destination: Path, subdir: str):
        prefix = Path("reviews/example") / subdir
        for name, payload in case["pins"].items():
            if Path(name).parent == prefix:
                self.assertEqual((destination / Path(name).name).read_bytes(), payload)
        self.assertEqual((destination / "hero-v4.webp").read_bytes(), case["current"][subdir])

    def enrich(self, case):
        reader.enrich_site(case["site"], revision=reader_fixtures.REVISION,
                           frontend_dir=case["frontend"])

    def test_selected_publish_preserves_both_variants_without_registering_legacy(self):
        with self.fixture() as case:
            for directory in (case["dist"], case["dist"] / "en", case["public"]):
                (directory / "unregistered.webp").write_bytes(b"unlisted image")
                (directory / "private-notes.json").write_text('{"draft":true}')
                (directory / ".env").write_text("synthetic local setting")
            original_dist = self.snapshot(case["dist"])
            unrelated = case["site"] / "reviews/unrelated/index.html"
            unrelated.parent.mkdir()
            unrelated.write_bytes(b"Existing unrelated article")
            entry = publisher.publish_review(case["review"], case["entry"])
            for subdir in ("", "en"):
                destination = case["public"] / subdir
                self.assert_retained(case, destination, subdir)
                for name in ("unregistered.webp", "private-notes.json", ".env"):
                    self.assertFalse((destination / name).exists())
                html = (destination / "index.html").read_text(encoding="utf-8")
                self.assertIn('src="hero-v4.webp"', html)
                self.assertNotIn("legacy-v2.webp", html)
                self.assertNotIn("legacy-v3.webp", html)
            self.assertEqual(entry["assets"], ["hero-v4.webp"])
            self.assertEqual(entry["translations"][0]["assets"], ["hero-v4.webp"])
            self.assertEqual(entry["thumbnail"], "reviews/example/hero-v4.webp")
            for field in ("folder", "title", "date", "href"):
                self.assertEqual(entry[field], case["entry"][field])
            self.assertEqual(entry["updated"], case["review"].updated)
            self.assertEqual(unrelated.read_bytes(), b"Existing unrelated article")
            self.assertEqual(self.snapshot(case["dist"]), original_dist)

    def test_variant_fresh_staging_falls_back_only_to_exact_previous_pins(self):
        with self.fixture(dist_pins=False) as case:
            (case["public"] / "unregistered.webp").write_bytes(b"unlisted image")
            (case["public"] / "private-notes.json").write_text('{"draft":true}')
            previous = self.snapshot(case["public"])
            for language, subdir in (("ko", ""), ("en", "en")):
                staging = case["root"] / ("staging-" + language)
                _html, assets = publisher.publish_dist_variant(
                    case["dist"] / subdir / "index.html", staging,
                    case["review"], language, case["public"] / subdir,
                )
                self.assert_retained(case, staging, subdir)
                self.assertEqual(assets, ["hero-v4.webp"])
                self.assertFalse((staging / "unregistered.webp").exists())
                self.assertFalse((staging / "private-notes.json").exists())
            self.assertEqual(self.snapshot(case["public"]), previous)

    def test_missing_changed_or_symlinked_sources_refuse_before_replacing_public(self):
        for failure in ("missing", "changed", "dist-symlink", "previous-symlink"):
            with self.subTest(failure=failure), self.fixture() as case:
                source = case["dist"] / "legacy-v2.webp"
                previous = case["public"] / "legacy-v2.webp"
                payload = previous.read_bytes()
                source.unlink()
                previous.unlink()
                if failure == "changed":
                    source.write_bytes(b"unapproved replacement")
                    previous.write_bytes(b"another unapproved replacement")
                elif failure.endswith("symlink"):
                    outside = case["root"] / "outside.webp"
                    outside.write_bytes(payload)
                    (source if failure == "dist-symlink" else previous).symlink_to(outside)
                before = self.snapshot(case["public"])
                with self.assertRaises((ValueError, FileNotFoundError)):
                    publisher.publish_review(case["review"], case["entry"])
                self.assertEqual(self.snapshot(case["public"]), before)

    def test_payload_guards_require_published_owner_pin_and_ignore_unpublished_owner(self):
        with self.fixture() as case:
            pins = json.loads(case["exceptions"].read_text())
            pins["reviews/not-published/legacy.webp"] = hashlib.sha256(b"never published").hexdigest()
            case["exceptions"].write_text(json.dumps(pins))
            self.enrich(case)
            catalog = (case["site"] / reader.CATALOG_NAME).read_bytes()
            updates = (case["site"] / reader.UPDATES_NAME).read_bytes()
            target = case["public"] / "legacy-v2.webp"
            expected = target.read_bytes()
            for verify_reader_source in (True, False):
                with self.subTest(verify_reader_source=verify_reader_source):
                    reader.validate_public_artifact(case["site"], verify_reader_source=verify_reader_source)
                    target.unlink()
                    with self.assertRaises(ValueError):
                        reader.validate_public_artifact(case["site"], verify_reader_source=verify_reader_source)
                    target.write_bytes(expected)
            self.assertEqual((case["site"] / reader.CATALOG_NAME).read_bytes(), catalog)
            self.assertEqual((case["site"] / reader.UPDATES_NAME).read_bytes(), updates)
            self.assertEqual(reader.build_updates(case["site"], json.loads(updates)), json.loads(updates))

    def test_payload_guard_rejects_corrupt_links_private_and_unregistered_extras(self):
        for failure in ("changed", "symlink", "private", "unregistered"):
            with self.subTest(failure=failure), self.fixture() as case:
                self.enrich(case)
                reader.validate_public_artifact(case["site"])
                target = case["public"] / "legacy-v3.webp"
                if failure == "changed":
                    target.write_bytes(b"unapproved pixels")
                elif failure == "symlink":
                    outside = case["root"] / "outside.webp"
                    outside.write_bytes(target.read_bytes())
                    target.unlink()
                    target.symlink_to(outside)
                elif failure == "private":
                    (case["public"] / ".env").write_text("synthetic setting")
                else:
                    (case["public"] / "unregistered.webp").write_bytes(b"unapproved image")
                with self.assertRaises(ValueError):
                    reader.validate_public_artifact(case["site"])

    def test_explicitly_registered_current_image_is_not_forced_to_old_pin(self):
        with self.fixture() as case:
            source = case["dist"] / "index.html"
            source.write_text(source.read_text().replace("hero-v4.webp", "legacy-v2.webp"))
            new_current = b"RIFFxxxxWEBPexplicitly reviewed current revision"
            (case["dist"] / "legacy-v2.webp").write_bytes(new_current)
            entry = publisher.publish_review(case["review"], case["entry"])
            self.assertEqual(entry["assets"], ["legacy-v2.webp"])
            self.assertEqual(entry["thumbnail"], "reviews/example/legacy-v2.webp")
            self.assertEqual((case["public"] / "legacy-v2.webp").read_bytes(), new_current)
            self.assertFalse((case["public"] / "hero-v4.webp").exists())
            self.assertNotEqual(hashlib.sha256(new_current).hexdigest(),
                                json.loads(case["exceptions"].read_text())["reviews/example/legacy-v2.webp"])
            (case["site"] / "manifest.json").write_text(json.dumps([entry]))
            self.enrich(case)
            reader.validate_public_artifact(case["site"])

    def test_pin_registry_and_growing_image_are_bounded_before_payload_acceptance(self):
        with self.fixture() as case:
            self.enrich(case)
            reader.validate_public_artifact(case["site"])
            registry = case["exceptions"]
            original_pins = registry.read_bytes()
            pins = json.loads(original_pins)
            first = next(iter(pins))
            duplicate = (original_pins[:-1] + b", " + json.dumps(first).encode()
                         + b": " + json.dumps(pins[first]).encode() + b"}")
            unsafe_path = json.dumps({**pins, "reviews/example/../outside.webp": "a" * 64}).encode()
            oversized = original_pins + b" " * (65_537 - len(original_pins))
            for failure, payload in (("duplicate", duplicate), ("path", unsafe_path),
                                     ("oversized", oversized)):
                with self.subTest(registry=failure):
                    registry.write_bytes(payload)
                    with self.assertRaises(ValueError):
                        reader.validate_public_artifact(case["site"])
            registry.write_bytes(original_pins)
            reader.validate_public_artifact(case["site"])

            target = case["public"] / "legacy-v2.webp"
            maximum = target.stat().st_size
            target_inode = target.stat().st_ino
            original_read = os.read
            grew = False
            requests, actual_counts = [], []

            def grow_after_fstat(fd, requested):
                nonlocal grew
                if os.fstat(fd).st_ino != target_inode:
                    return original_read(fd, requested)
                if not grew:
                    with target.open("ab") as handle:
                        handle.write(b"x" * (maximum + 10))
                    grew = True
                requests.append(requested)
                result = original_read(fd, requested)
                actual_counts.append(len(result))
                return result

            with patch.object(reader, "MAX_LEGACY_IMAGE_BYTES", maximum, create=True), \
                    patch.object(reader.os, "read", grow_after_fstat):
                with self.assertRaises(ValueError):
                    reader.validate_public_artifact(case["site"])
            self.assertTrue(grew)
            self.assertTrue(requests)
            self.assertTrue(all(requested <= maximum + 1 for requested in requests))
            self.assertLessEqual(sum(actual_counts), maximum + 1)
            self.assertGreater(target.stat().st_size, maximum)

    @unittest.skipUnless(hasattr(os, "mkfifo"), "FIFO checks require POSIX")
    def test_fifo_image_and_registry_refuse_nonblocking_before_any_payload_read(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            image, registry = root / "cover.webp", root / "pins.json"
            for path in (image, registry):
                os.mkfifo(path, 0o600)
            before = {path.name: path.stat() for path in (image, registry)}
            original_open = os.open
            observed = []

            def nonblocking_open(path, flags, *args, **kwargs):
                # Fail before opening if this regresses, rather than hanging
                # this test on a FIFO with no writer.
                self.assertTrue(flags & os.O_NONBLOCK)
                observed.append(Path(path).name)
                return original_open(path, flags, *args, **kwargs)

            with patch.object(reader.os, "open", nonblocking_open), \
                    patch.object(reader.os, "read", side_effect=AssertionError("FIFO payload must not be read")):
                with self.assertRaises(ValueError):
                    reader.legacy_image_bytes(image)
                with patch.object(reader, "ASSET_EXCEPTIONS", registry), self.assertRaises(ValueError):
                    reader.reviewed_legacy_image_pins()
            self.assertEqual(observed, [image.name, registry.name])
            self.assertEqual({path.name for path in root.iterdir()}, {image.name, registry.name})
            for path in (image, registry):
                after = path.stat()
                self.assertTrue(stat.S_ISFIFO(after.st_mode))
                self.assertEqual((after.st_dev, after.st_ino, after.st_mode, after.st_size),
                                 (before[path.name].st_dev, before[path.name].st_ino,
                                  before[path.name].st_mode, before[path.name].st_size))


if __name__ == "__main__":
    unittest.main()
