# Federlicht favicon assets

Source reference: https://github.com/Infant83/Federlicht/blob/main/src/federnett/logo.png

The original logo contains the feather, book light, lettering, and many small surrounding icons.
Those details become muddy at favicon sizes, so `build_favicon.py` creates a simplified icon-only
mark: dark rounded background, blue/gold feather, white quill, and a small light/book cue.

Regenerate:

```powershell
python .automation\assets\federlicht-icon\build_favicon.py
```

