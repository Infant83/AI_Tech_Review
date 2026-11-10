"""Build the reviewed supplement index and a deterministic public resource ZIP.

The original private input is verified and read in memory. Only the explicitly
listed educational files can enter the public resource package. No notebook or
external program is executed by this builder.
"""
import argparse
import csv
import hashlib
import html
import io
import json
from pathlib import Path, PurePosixPath
import re
import stat
import zipfile

ROOT = Path(__file__).resolve().parents[1]
SOURCE_SHA256 = '25d4b4a184c32f64519d6853d3302d4cf9a3f81c5d22e690df8ee9cbdd1a2e40'
BOOK_COMMIT = '22954602b59d586c0727cf6110292b7000659db2'
QAOA_COMMIT = '438b205b9bfd072038f4d342cf6adb89b1bdbb02'
PREFIX = 'faryad-qml-supplement-v1/'
COURSE = 'https://infant83.io/AI_Tech_Review/lectures/quantum-machine-learning/'
CANONICAL = COURSE + 'supplements/faryad-qml-v1/'
NOTEBOOKS = (
    '06a_grover.ipynb', '06b_quantum_counting.ipynb',
    '06c_amplitude_amplification.ipynb', '06d_search_by_hamiltonian_simulation.ipynb',
    '07a_trotter_suzuki.ipynb', '07b_sparse_hamiltonian.ipynb',
    '07c_lcu.ipynb', '07d_pauli_string_simulation.ipynb',
    '08_chemistry_pipeline.ipynb', '09a_qaoa.ipynb', '09b_hhl.ipynb',
    '10a_mlae.ipynb', '10b_qubitization_simulation.ipynb', '10c_qsvt_linear_solver.ipynb',
)
DATA_NAMES = ('6assets', '8assets', '10assets', '12assets', 'depth_scan', 'replicates_8assets')
UNCHANGED = (
    *('notebooks/' + name for name in NOTEBOOKS),
    'notebooks/requirements-upstream.txt',
    *('data/qaoa_jobs_' + name + '_ibm_fez.json' for name in DATA_NAMES),
    'licenses/book-notebooks-MIT.txt', 'licenses/qaoa-code-MIT.txt',
    'licenses/qaoa-data-CC-BY-4.0.txt', 'notebook-catalog.csv',
    'labs/audit_notebooks.py', 'labs/audit_qaoa.py',
    'labs/notebook_audit_results.json', 'labs/qaoa_audit_results.json',
)
CHAPTERS = {
    '02': 'qubits-gates-and-measurement', '03': 'entanglement-and-circuits',
    '04': 'data-encoding-and-loading', '07': 'gradients-and-training',
    '10': 'generalization-and-benchmarking', '11': 'hardware-and-resources',
    '12': 'noise-and-mitigation', '14': 'advantage-and-dequantization',
    '16': 'symmetry-and-scientific-learning', '17': 'fault-tolerant-qml',
}


def sha256(blob):
    return hashlib.sha256(blob).hexdigest()


def resource_zip(files):
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name, data in sorted(files.items()):
            info = zipfile.ZipInfo(PREFIX + name, date_time=(2026, 11, 10, 0, 0, 0))
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, data, compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
    return buffer.getvalue()


def public_readme():
    return '''Faryad 실습 보충: 알고리즘 노트북과 QAOA 실행 예산
2026-11-10 · 한국어 공개판 · PDF 8쪽
Agentic Tech Review Letters (ATRL)

index.html 또는 supplement.pdf를 열어 읽습니다.
기존 QML 18강: ''' + COURSE + '''
이 보충은 별도의 독립 편집 자료이며 기존 147쪽 PDF를 교체하지 않습니다.

내용
- notebooks/: 원저자의 알고리즘 노트북 14개와 저장 출력, 변경 없음.
- notebook-catalog.csv: 기존 강의 연결 제안과 원출처·해시.
- data/: 공개 QAOA 장부 JSON 6개, 변경 없음.
- labs/: 보충 제작자의 오프라인 검산 코드 두 개와 기존 실행 결과.
- licenses/: 원저자 코드의 MIT 고지, 공개 데이터의 CC-BY-4.0 고지.
- sources.json: 확인한 원출처·판본·검토 범위.
- SHA256SUMS.txt: 이 파일을 제외한 공개 묶음의 SHA-256.

검산 실행 (이 폴더에서)
python3 labs/audit_qaoa.py --data-dir data --output qaoa-audit-rerun.json
python3 labs/audit_notebooks.py --source-dir . --output notebook-audit-rerun.json
첫 명령은 Python 표준 라이브러리만, 둘째는 NumPy를 사용합니다.
두 코드는 원저자 노트북을 실행하거나 장치에 작업을 제출하지 않습니다.
작은 모형의 이번 공개 검토 재실행에는 NumPy 2.0.2를 사용했습니다.

원저자 노트북을 별도로 실행할 때는 별도 환경과 실제 버전 기록이 필요합니다.
requirements-upstream.txt는 잠금 파일이 아닙니다.
QAOA 장치 노트북 6개는 아래 원출처에서 별도로 제공합니다. NB16a는
DRY_RUN=False가 기본이므로 로컬 모의실험을 원하면 실행 전 True로 바꿉니다.
이 묶음은 원저자 노트북 전체나 실제 QPU 실험의 재현 성공을 보증하지 않습니다.

공개 장부: 193작업, QPU 시간 추정 합계 약 33.6143분,
측정 제출-결과 wall time 합계 약 142.9255분.
논문의 metrics-key fallback 설명에 따라 QPU 시간 필드는 계측값으로 쓰지 않습니다.
95% 문턱은 각 방법 자신의 최종 무잡음 근사비 누적최댓값을 기준으로 합니다.

원출처·권리
Muhammad Faryad, Quantum Algorithms from First Principles companion notebooks:
https://github.com/muf148/quantum-algorithms-first-principles/tree/''' + BOOK_COMMIT + '''
노트북·코드의 MIT 고지를 보존합니다. 책 본문은 재배포하지 않습니다.
Muhammad Faryad, qaoa-job-budget:
https://github.com/muf148/qaoa-job-budget/tree/''' + QAOA_COMMIT + '''
여섯 데이터 파일은 CC-BY-4.0, 저작자 Muhammad Faryad이며 변경하지 않았습니다.
논문: https://arxiv.org/html/2609.13669v1
편집한 보충 설명에 원자료의 라이선스를 일괄 적용하지 않습니다.

책임 편집자 김현중 · AI 보조 OpenAI Codex.
faryad_science_package: 원출처·라이선스·검산 대조, 웹 안내와 자료 묶음 편집.
faryad_pdf_review: PDF 정제·내용 보존·링크·전체 8쪽 조판 검수.
root: 기존 강의 연결·등록·발행 통합. 사람의 원고 감수는 수행하지 않았습니다.
'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--package', type=Path, required=True)
    args = parser.parse_args()
    source = args.package.read_bytes()
    assert sha256(source) == SOURCE_SHA256, 'Unexpected source package edition'
    archive = zipfile.ZipFile(io.BytesIO(source))
    assert len(archive.namelist()) == len(set(archive.namelist())), 'Duplicate ZIP entry'
    for info in archive.infolist():
        name = PurePosixPath(info.filename)
        assert not name.is_absolute() and '..' not in name.parts
        assert not stat.S_ISLNK(info.external_attr >> 16)
        assert info.filename.startswith(PREFIX)
    files = {name: archive.read(PREFIX + name) for name in UNCHANGED}
    original_manifest = archive.read(PREFIX + 'SHA256SUMS.txt').decode()
    recorded = {line.split(maxsplit=1)[1].lstrip('*'): line.split(maxsplit=1)[0]
                for line in original_manifest.splitlines()}
    assert all(sha256(data) == recorded[name] for name, data in files.items())
    dist = ROOT / 'dist'
    pdf = (dist / 'supplement.pdf').read_bytes()
    pdf_qa = json.loads((ROOT / 'reports/pdf-publication-qa.json').read_text())
    assert sha256(pdf) == pdf_qa['public_sha256'] and pdf_qa['public_pages'] == 8
    rows = list(csv.DictReader(io.StringIO(files['notebook-catalog.csv'].decode('utf-8-sig'))))
    assert len(rows) == 14 and {r['filename'] for r in rows} == set(NOTEBOOKS)
    table = []
    for row in rows:
        assert sha256(files['notebooks/' + row['filename']]) == row['sha256']
        expected = 'https://github.com/muf148/quantum-algorithms-first-principles/blob/' + BOOK_COMMIT + '/notebooks/' + row['filename']
        assert row['pinned_source'] == expected
        short = row['filename'].split('_', 1)[0]
        chapters = []
        for chapter in row['suggested_existing_lecture'].split(','):
            name = chapter.strip().zfill(2)
            chapters.append('<a href="' + COURSE + 'lectures-' + name + '-' + CHAPTERS[name] + '.html">' + name + '강</a>')
        table.append('<tr><th scope="row"><a href="' + html.escape(expected, quote=True) + '">' + html.escape(short) + '</a></th><td>' + html.escape(row['topic_ko']) + '</td><td>' + ' · '.join(chapters) + '</td></tr>')
    page = (ROOT / 'content/index.html').read_text().replace('{{NOTEBOOK_ROWS}}', '\n'.join(table)).replace('{{PDF_SHA256}}', sha256(pdf))
    assert '{{' not in page and not re.search(r'/Users/|file://|utm_|mailto:', page)
    css = (ROOT / 'content/style.css').read_bytes()
    (dist / 'index.html').write_text(page)
    (dist / 'style.css').write_bytes(css)
    (dist / 'notebook-catalog.csv').write_bytes(files['notebook-catalog.csv'])
    sources = json.loads(archive.read(PREFIX + 'sources.json'))
    sources['publication_status'] = 'public-edition'
    sources['public_pdf_sha256'] = sha256(pdf)
    sources['publication_preparation'] = {'date': '2026-11-10', 'privacy': 'Private delivery context and internal publishing instructions excluded.', 'current_offline_audit_numpy': '2.0.2', 'original_notebooks_executed': 0, 'QPU_submissions': 0}
    files.update({'supplement.pdf': pdf, 'index.html': page.replace('href="resources.zip"', 'href="' + CANONICAL + 'resources.zip"').encode(), 'style.css': css,
                  'README.txt': public_readme().encode(), 'sources.json': (json.dumps(sources, ensure_ascii=False, indent=2) + '\n').encode()})
    forbidden = re.compile(r'/Users/|file://|mailto:|utm_|[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}')
    for name, data in files.items():
        if name.endswith('.pdf'):
            continue
        assert not forbidden.search(data.decode('utf-8-sig')), 'Private marker in ' + name
    assert all(name not in files for name in ['INTEGRATION.txt', 'source/supplement.tex'])
    sums = ''.join(sha256(data) + '  ' + name + '\n' for name, data in sorted(files.items()))
    files['SHA256SUMS.txt'] = sums.encode()
    bundle = resource_zip(files)
    assert resource_zip(files) == bundle, 'Nondeterministic resource ZIP'
    (dist / 'resources.zip').write_bytes(bundle)
    report = {'date': '2026-11-10', 'source_package_sha256': SOURCE_SHA256,
              'public_pdf_sha256': sha256(pdf), 'public_pages': 8,
              'resources_sha256': sha256(bundle), 'resources_bytes': len(bundle),
              'web_sha256': sha256(page.encode()), 'css_sha256': sha256(css),
              'csv_sha256': sha256(files['notebook-catalog.csv']),
              'unchanged_source_files': {name: sha256(files[name]) for name in UNCHANGED},
              'zip_entries': sorted(files), 'deterministic_zip_rebuild_equal': True,
              'notebooks': 14, 'data_files': 6, 'licenses': 3,
              'private_markers_found': 0, 'original_notebooks_executed': 0, 'QPU_submissions': 0,
              'publication_scope': 'Reviewed source and licenses, rerun offline small-model/ledger audits; preserve original notebook/data bytes and prior 147-page course PDF.',
              'excluded_source_files': ['Original PDF', 'Original HTML', 'Original README', 'INTEGRATION.txt', 'source/supplement.tex'],
              'render_status': 'Requires separate browser verification before publication.'}
    (ROOT / 'reports/package-publication-qa.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({name: report[name] for name in ['public_pdf_sha256', 'resources_sha256', 'resources_bytes', 'notebooks', 'data_files']}))


if __name__ == '__main__':
    main()
