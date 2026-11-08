"""Shared publication mark for the public catalog headers."""
from html import escape


ICON_ASSET_VERSION = "20261022-prompt-brace"
SITE_STYLES_VERSION = "20261022-header-brand"
BRAND_TITLE = "Agentic Tech Review"
SITE_NAME = f"{BRAND_TITLE} Letters"
SITE_SHORT_NAME = "ATRL"


def render_brand_link(asset_prefix: str = "", *, stacked: bool = False) -> str:
    prefix = escape(asset_prefix, quote=True)
    name = f'<b>{BRAND_TITLE}</b> <small>LETTERS</small>' if stacked else SITE_NAME
    return (
        f'<a class="brand" href="{prefix}index.html">'
        f'<img class="brand-icon" src="{prefix}assets/apple-touch-icon.png?v={ICON_ASSET_VERSION}" '
        'width="44" height="44" alt="" aria-hidden="true">'
        f'<span class="brand-name">{name}</span></a>'
    )
