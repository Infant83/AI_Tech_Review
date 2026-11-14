"""Build the existing bilingual web editions from their canonical manuscripts."""
from pathlib import Path
import html
import json
import re
import sys
from html.parser import HTMLParser
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[2]
TOPIC = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from markdown_to_html import LinkItem, build_context, render_final_review_template
from html_to_dist import package_html


class EvidenceLinks(HTMLParser):
    """Read actual body anchors without promoting historical plain-text URLs."""

    def __init__(self):
        super().__init__()
        self.items = []
        self.seen = set()
        self.current = None
        self.label = []

    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            self.current = dict(attrs).get('href', '')
            self.label = []

    def handle_data(self, data):
        if self.current is not None:
            self.label.append(data)

    def handle_endtag(self, tag):
        if tag != 'a' or self.current is None:
            return
        href = self.current
        parsed = urlparse(href)
        external = parsed.scheme in {'https', 'http'}
        if href not in self.seen and (external or parsed.path.endswith('.pdf')):
            label = parsed.netloc if external else ''.join(self.label).strip()
            self.items.append(LinkItem(label=label or href, href=href, external=external))
            self.seen.add(href)
        self.current = None


def main():
    settings = json.loads(Path(__file__).with_name('rendering-settings.json').read_text())
    for language, suffix, subdir in [('ko', '', ''), ('en', '_en', 'en')]:
        source = TOPIC / 'reports' / f'{TOPIC.name}_final_review{suffix}.md'
        context = build_context(source, 'final-review')
        context.generated_at = settings['original_generated_at'][language]
        context.issue_label = settings['original_issue_label'][language]
        context.source_modified_at = context.modified_date
        evidence = EvidenceLinks()
        evidence.feed(context.body_html)
        context.links = evidence.items
        aliases = settings['legacy_anchors'][language]

        def heading(match):
            level, identifier, content = match.groups()
            title = html.unescape(re.sub('<[^>]+>', '', content))
            anchors = ''.join(f'<span class="legacy-anchor" id="{old}" aria-hidden="true"></span>'
                              for old in aliases.get(title, []))
            return anchors + f'<h{level} id="section-{identifier}">{content}</h{level}>'

        context.body_html = re.sub(r'<h([2-4]) id="([^"]+)">(.*?)</h\1>', heading, context.body_html, flags=re.S)
        context.toc_html = context.toc_html.replace('href="#', 'href="#section-')
        label = '표 좌우로 보기' if language == 'ko' else 'Scroll table horizontally'
        context.body_html = context.body_html.replace('<table>', f'<div class="table-scroll" tabindex="0" role="region" aria-label="{label}"><table>').replace('</table>', '</table></div>')
        if context.body_html.count('<figure ') != 2:
            raise ValueError(f'Expected the two existing figures in {language}')
        output = render_final_review_template(context)
        # The source manuscript is not part of the public article allowlist.
        old_labels = ('생성 시각:', '원본 파일 최종 수정 시각:') if language == 'ko' else ('Generated:', 'Source last modified:')
        new_labels = ('원 발행본 생성 시각:', '편집 개정:') if language == 'ko' else ('Original edition generated:', 'Editorial revision:')
        for old, new in zip(old_labels, new_labels):
            output = output.replace(old, new)
        output = output.replace('  </style>', '''
    .final-article, .content-grid > *, .hero-inner > * { min-width: 0; }
    .table-scroll { max-width: 100%; overflow-x: auto; }
    .table-scroll:focus-visible { outline: 2px solid var(--teal); outline-offset: 4px; }
    mjx-container[display="true"] { overflow-x: auto; overflow-y: hidden; max-width: 100%; }
    .reference-list { overflow-wrap: anywhere; }
    .reference-list li { margin-bottom: 1rem; }
    .citation { white-space: nowrap; }
    code { overflow-wrap: anywhere; white-space: normal; }
  </style>''')
        source.with_suffix('.html').write_text('\n'.join(line.rstrip() for line in output.splitlines()) + '\n')
        result = package_html(source.with_suffix('.html'), TOPIC / 'dist' / subdir)
        if result.missing_refs:
            raise ValueError(result.missing_refs)
        # Package the linked manuscript first, then omit its non-public navigation.
        for path in [source.with_suffix('.html'), result.html_output, result.index_output]:
            if path is None:
                continue
            text = path.read_text()
            text = re.sub(r'\s*<a href="[^"<>]+\.md">[^<]+</a>', '', text)
            path.write_text(text)
    print('Built both existing web editions with two figures and the linked historical briefing')


if __name__ == '__main__':
    main()
