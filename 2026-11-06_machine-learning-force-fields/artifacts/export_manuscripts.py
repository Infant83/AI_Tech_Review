"""Export the curated bilingual article JSON to the repository's Markdown format.

Only authored text and explicitly approved local illustrations are accepted.
The nine equations are typeset from equivalent TeX rather than Unicode facsimiles.
"""
from pathlib import Path
import argparse
import html
import json
import re

ROOT = Path(__file__).resolve().parents[1]
ASSETS = {
    'figures-v2/hero-v2.png': 'hero.webp',
    'figures-v2/lj_energy_force.png': 'lj_energy_force.svg',
    'figures-v2/lj_md_energy.png': 'lj_md_energy.svg',
    'figures/simulation_workflow.png': 'simulation_workflow.svg',
    'figures/barrier_accuracy.png': 'barrier_accuracy.svg',
}
EQUATIONS = [
    r'U(\mathbf R)=U_{\mathrm{bond}}+U_{\mathrm{angle}}+U_{\mathrm{torsion}}+U_{\mathrm{nonbonded}}',
    r'U^{\mathrm{LJ}}(r)=4\epsilon\left[\left(\frac{\sigma}{r}\right)^{12}-\left(\frac{\sigma}{r}\right)^6\right]',
    r'\mathbf F_i(\mathbf R)=-\nabla_i U(\mathbf R),\qquad m_i\frac{d^2\mathbf R_i}{dt^2}=\mathbf F_i(\mathbf R)',
    r'f_r(r)=-\frac{dU^{\mathrm{LJ}}}{dr}=\frac{24\epsilon}{r}\left[2\left(\frac{\sigma}{r}\right)^{12}-\left(\frac{\sigma}{r}\right)^6\right]',
    r'\begin{aligned}\mathbf v_i(t+\Delta t/2)&=\mathbf v_i(t)+\frac{\Delta t}{2m_i}\mathbf F_i(t)\\\mathbf R_i(t+\Delta t)&=\mathbf R_i(t)+\Delta t\,\mathbf v_i(t+\Delta t/2)\\\mathbf v_i(t+\Delta t)&=\mathbf v_i(t+\Delta t/2)+\frac{\Delta t}{2m_i}\mathbf F_i(t+\Delta t)\end{aligned}',
    r'\begin{aligned}U_\theta(\mathbf R)&=\sum_i e_\theta\bigl(D_i(\mathbf R)\bigr)+U_{\mathrm{explicit}}(\mathbf R)\\\mathbf F_{\theta,i}(\mathbf R)&=-\nabla_i U_\theta(\mathbf R)\end{aligned}',
    r'\begin{aligned}\mathcal L(\theta)={}&w_E\,\operatorname{MSE}(U_\theta,U_{\mathrm{ref}})\\&+w_F\,\operatorname{MSE}(-\nabla_{\mathbf R}U_\theta,\mathbf F_{\mathrm{ref}})\\&+w_W\,\operatorname{MSE}(W_\theta,W_{\mathrm{ref}})\end{aligned}',
    r'\frac{k_{\mathrm{ML}}}{k_{\mathrm{ref}}}=\exp\!\left[-\frac{\delta\Delta G^\ddagger}{RT}\right]',
    None,
]


def safe_text(value):
    text = str(value)
    if re.search(r'/Users/|archive/private|file://|(?i:access_token|session_cookie|password)', text):
        raise ValueError('Nonpublic source material cannot be exported.')
    return text


def figure(block, language):
    asset = ASSETS[block['src']]
    caption, alt = safe_text(block['caption']), safe_text(block['alt'])
    attr = ' class="hero"' if block.get('role') == 'hero' else ''
    image = f'<img src="{asset}" alt="{html.escape(alt, quote=True)}">'
    if asset.endswith('.svg'):
        # The public absolute URL also keeps PDF annotations free of host paths.
        url = f'https://infant83.io/AI_Tech_Review/reviews/{ROOT.name}/{"en/" if language == "en" else ""}{asset}'
        image = f'<a class="figure-zoom" href="{url}">{image}</a>'
    return f'<figure{attr}>{image}<figcaption>{caption}</figcaption></figure>'


def export(language):
    source = ROOT / 'artifacts' / f'article-{language}.json'
    data = json.loads(source.read_text(encoding='utf-8'))
    safe_text(json.dumps(data, ensure_ascii=False))
    assert [r['id'] for r in data['references']] == list(range(1, 31))
    ko = language == 'ko'
    parts = [f'# {data["title"]}', f'<p class="dek">{html.escape(data["subtitle"])}</p>']
    # Keep the introductory artwork beside the title, ahead of the numbered prose.
    heroes = [b for s in data['sections'] for b in s['blocks'] if b.get('role') == 'hero']
    assert len(heroes) == 1
    parts.append(figure(heroes[0], language))
    equation_index = 0
    disclosure = []
    for section in data['sections']:
        if section['title'] in ['작성·검증 정보', 'Production and verification', 'How this review was made', 'Writing and verification disclosure']:
            disclosure = section['blocks']
            continue
        parts.append('## ' + section['title'])
        for block in section['blocks']:
            kind = block['type']
            if block.get('role') == 'hero':
                continue
            if kind == 'paragraph':
                parts.append(block['text'])
            elif kind == 'figure':
                parts.append(figure(block, language))
            elif kind == 'equation':
                tex = EQUATIONS[equation_index]
                equation_index += 1
                if tex:
                    parts.append('$$\n' + tex + '\n$$')
                else:
                    # Cost accounting is a prose relation, with no fictitious variables.
                    parts.append('<p class="cost-relation">' + html.escape(block['text']) + '</p>')
            elif kind == 'table':
                def cell(value):
                    return safe_text(value).replace('|', '\\|').replace('\n', '<br>')
                parts.append('\n'.join(['| ' + ' | '.join(map(cell, block['columns'])) + ' |',
                              '| ' + ' | '.join('---' for _ in block['columns']) + ' |',
                              *['| ' + ' | '.join(map(cell, row)) + ' |' for row in block['rows']]]))
            elif kind == 'numbered':
                parts.append('\n'.join(f'{i}. {item}' for i, item in enumerate(block['items'], 1)))
            else:
                raise ValueError(f'Unsupported block type: {kind}')
    assert equation_index == 9, equation_index
    parts.append('## ' + ('참고문헌' if ko else 'References'))
    parts.append('\n'.join(f'{r["id"]}. {r["label"]} [{"doi:" + r["url"].split("doi.org/")[1] if "doi.org/" in r["url"] else r["url"]}]({r["url"]})' for r in data['references']))
    assert len(disclosure) >= 2, 'Preserve the source and authoring disclosure.'
    parts.append('<!-- AI Tech Review Authoring Disclosure -->\n<section class="authoring-disclosure" id="authoring-disclosure" aria-labelledby="disclosure-heading">\n<h2 id="disclosure-heading">' + ('작성·검증 정보' if ko else 'How this review was made') + '</h2>\n' + '\n'.join('<p>' + html.escape(b['text']) + '</p>' for b in disclosure) + '\n</section>\n<!-- End AI Tech Review Authoring Disclosure -->')
    output = ROOT / 'reports' / f'review_{language}.md'
    output.write_text('\n\n'.join(parts) + '\n', encoding='utf-8')
    print(json.dumps({'language': language, 'references': 30, 'equations': equation_index, 'figures': 5, 'file': str(output.relative_to(ROOT))}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--language', choices=['ko', 'en'])
    args = parser.parse_args()
    for language in [args.language] if args.language else ['ko', 'en']:
        export(language)
