import base64
import importlib.util
from io import BytesIO
from pathlib import Path
import re
import tempfile
import unittest

from PIL import Image


class BrowserIconTests(unittest.TestCase):
    def test_browser_exports_keep_reviewed_art_and_correct_small_slots(self):
        root = Path(__file__).resolve().parents[1]
        script = root / ".automation/assets/ai-tech-review-icon/build_favicon.py"
        spec = importlib.util.spec_from_file_location("browser_icon_build", script)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        original_source = module.ARTWORK_SOURCE.read_bytes()
        original_home = (module.GENERATED / "apple-touch-icon.png").read_bytes()
        original_512 = (module.GENERATED / "ai-tech-review-icon-512.png").read_bytes()
        with tempfile.TemporaryDirectory() as name:
            module.GENERATED = Path(name)
            module.main()
            svg = (module.GENERATED / "ai-tech-review-icon.svg").read_text()
            embedded = base64.b64decode(re.search(r"base64,([^\"]+)", svg).group(1))
            self.assertEqual(embedded, (module.GENERATED / "favicon-64x64.png").read_bytes())
            with Image.open(BytesIO(embedded)) as png:
                self.assertEqual(png.size, (64, 64))
            with Image.open(module.GENERATED / "favicon.ico") as ico:
                self.assertEqual(ico.ico.sizes(), {(16, 16), (32, 32), (48, 48), (64, 64)})
            self.assertLess((module.GENERATED / "favicon.ico").stat().st_size, 20_000)
            self.assertLess((module.GENERATED / "ai-tech-review-icon.svg").stat().st_size, 12_000)
            for name, original in [("apple-touch-icon.png", original_home), ("ai-tech-review-icon-512.png", original_512)]:
                # PNG compression can differ between OS zlib builds. Artwork
                # pixels and dimensions, rather than encoder bytes, must match.
                with Image.open(BytesIO(original)) as before, Image.open(module.GENERATED / name) as after:
                    self.assertEqual(after.size, before.size)
                    self.assertEqual(after.convert("RGB").tobytes(), before.convert("RGB").tobytes())
        self.assertEqual(module.ARTWORK_SOURCE.read_bytes(), original_source)
