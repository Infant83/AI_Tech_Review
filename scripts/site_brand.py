"""Shared publication mark for the public catalog headers."""
from html import escape


ICON_ASSET_VERSION = "20261022-prompt-brace"
SITE_STYLES_VERSION = "20261022-header-brand"


def render_brand_link(asset_prefix: str = "") -> str:
    prefix = escape(asset_prefix, quote=True)
    return (
        f'<a class="brand" href="{prefix}index.html">'
        f'<img class="brand-icon" src="{prefix}assets/apple-touch-icon.png?v={ICON_ASSET_VERSION}" '
        'width="44" height="44" alt="" aria-hidden="true">'
        '<span class="brand-name">AI Tech Review Letters</span></a>'
    )
