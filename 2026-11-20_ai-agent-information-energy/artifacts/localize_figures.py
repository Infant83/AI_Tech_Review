"""Translate reviewed Korean figure labels without altering the scientific geometry."""
from pathlib import Path
import json
import re
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'figures'
NS = 'http://www.w3.org/2000/svg'
ET.register_namespace('', NS)
PAIRS = '''1,110회 성공===1,110 successful
11회 목표 미달 종료  ·  1회 판정 불가===11 goal unreached · 1 ungraded
11회 목표 미달 종료 · 1회 판정 불가===11 goal unreached · 1 ungraded
34.4% — 나머지 실행===34.4% — other runs
65.6% — 78회의 제한 중단 실행===65.6% — 78 censored runs
78회 제한 중단  ·  전체 실행의 6.5%===78 censored · 6.5% of all runs
78회 제한 중단 · 6.5%===78 censored · 6.5%
78회의 제한 중단 실행이===78 censored runs used
A  전체 실행 1,200회===A  All 1,200 runs
B  전체 출력 토큰===B  All output tokens
B  전체 출력 토큰의 사용처===B  Where all output tokens went
C  성공 실행의 출력 토큰===C  Output tokens in successful runs
C  성공 실행의 출력 토큰 분류===C  Successful-run output tokens
Gemini Apps · 2025년 5월 중앙값 텍스트 프롬프트===Gemini Apps · Median text prompt, May 2025
Q환경 ≥ kBT ln 2===Qenv ≥ kBT ln 2
T는 절대온도, kB는 Boltzmann 상수===T: absolute temperature · kB: Boltzmann constant
heat에는 읽기·검색·테스트가 포함된다. 분류 단위는 호출이며 비용은 출력 토큰이다.===Heat includes reading, search and tests. Calls are classified; output tokens are counted.
q가 변한 호출: work===Calls changing q: work
ΔS환경 ≥ kB ln 2===ΔSenv ≥ kB ln 2
가속기와 호스트===Accelerator and host
같은 탐색의 반복을 감지===Detect repeated searches
개념도 · 정보의 가치와 물리 에너지는 별도량===Concept · Information value and energy are distinct
개념도 · 출력의 의미와 품질은 과제 기준으로, 에너지는 물리적 경계 안에서 평가한다===Concept · Assess output by task criteria and energy within a physical boundary
검색·계산===Search · run
검색한 증거===New evidence
검증 결과에 따라 다시 계획===Replan from verification
검증 기록 검색·수식 계산===Retrieve records · calculate
검증한 출력===Verified output
검증한 출력과 보존할 기록===Verified output and records
계산·메모리·호스트===Compute · memory · host
관찰===Logs
관찰 보존===Save evidence
교육 모형 · T는 절대온도, kB는 Boltzmann 상수 · 대칭 메모리의 등온 초기화===Model · T: absolute temperature; kB: Boltzmann constant · Symmetric isothermal reset
교육 모형 · 대칭 메모리의 등온 초기화===Model · Symmetric isothermal reset
규칙 개정과 기간별 총량 평가===Revise rules and assess totals
근거 있으면 수정===Revise with evidence
기억===Memory
기억·도구 사용===Use memory and tools
기획자가 정하는 조건===Conditions defined by the planner
나머지 1,122회의 실행===The other 1,122 runs
냉각===Cooling
냉각 등 부대설비===Cooling and overhead
냉각과 열 전달===Heat exchange
냉각에도===Cooling also
냉각에도 추가 전력이 든다===Cooling also needs power
논리 상태의 불확실성 감소===Less logical-state uncertainty
논문·검증 기록===Papers · verified records
다음 작업에 재사용===Reuse in the next task
다음 행동===Next action
대기===Idle
대기 용량===Idle capacity
대칭인 두 논리 상태 · 단일 온도 T의 환경===Symmetric states · One environment at T
데이터센터===Data centre
데이터센터 부대설비===Data-centre overhead
도구===Tools
독립 판정===Independent check
독립 판정으로 품질 확인===Independent quality check
등===overhead
매개변수에 담긴 관계===Learned relationships
메모리===Memory
목적===Purpose
목표 진행 q가 그대로인 호출: heat===Calls leaving q unchanged: heat
문헌·도구의 새 관찰===New source and tool evidence
물리적 에너지 흐름===Physical energy flow
미완료 상태를 인계===Hand over unfinished work
방출 열===Heat released
보존할 기록===Records to retain
부대설비===Overhead
분류 단위는 호출이며 비용은 출력 토큰===Classify calls; count output tokens
사용자 기기·외부 네트워크===User devices · external networks
서로 다른 화살표로 읽는 하나의 에이전트 실행===Two kinds of arrows for one agent run
서비스를 제공하는===Energy used
서비스를 제공하는 운영 에너지===Operational energy for serving
설계 제안 · 근거를 검증하는 리뷰 작성의 경우===Proposed design · Writing an evidence-checked review
성공===successful
성공 뒤에 가려진 토큰의 비용===Token costs behind success
실패·재시도·검증을 포함한 토큰·에너지·시간·오류===Tokens · energy · time · errors, including failures, retries and checks
실패와 검증 비용도 관찰에 포함===Observe failures and verification too
실행 수와 토큰 사용의 다른 분포===Different distributions of runs and token use
실행 수와 토큰 수는 서로 다른 분모다===Different denominators for runs and tokens
실행을 조절하는 하네스===Harness controlling execution
약 20%===About 20%
약 20%  work===About 20% work
약 80%===About 80%
약 80%  heat — 목표 진행 q가 그대로인 호출===About 80% heat — calls leaving q unchanged
엔트로피 생성===Entropy production
열===Heat
예산===Budget
예산 부족·진전 없음===Low budget · no progress
예산이 부족하거나 진전이 없으면===If budget or progress is insufficient
완료한 결과===Completed result
완료한 결과와 검증 기록===Completed result and checks
운영 에너지===for serving
운영 에너지의 구성===Operational energy components
운영 에너지의 측정 경계===Operational energy boundary
이 에너지 값의 범위 밖: 학습·칩 제조===Outside this value: training · chip manufacture
이 에너지 값의 범위 밖: 학습·칩 제조·사용자 기기·외부 네트워크===Outside this value: training · chip manufacture · user devices · external networks
이상적인 준정적 한계: Σ → 0===Ideal quasistatic limit: Σ → 0
이상적인 준정적 한계에서는 환경의 증가가 메모리의 감소를 상쇄해 Σ → 0===In the ideal quasistatic limit, environmental increase offsets memory decrease: Σ → 0
읽기·검색·테스트 등을 포함===Includes reading, search and tests
입력 자료===Inputs
자료·모델 선택===Select sources and models
자원 조건을 실행 규칙에 연결하기===Connect resources to execution rules
작업 한도와 기간별 총량===Task limits and period totals
작업별 한도와 기간별 총량===Task limits and period totals
작업의 목적과 입력===Task purpose and input
저자 보고값 재도표 · arXiv:2508.15734v1, Table 1===Replotted · arXiv:2508.15734v1, Table 1
저자 보고값 재도표 · arXiv:2508.15734v1, Table 1 · 전체 제공 인프라를 포함한 측정===Replotted · arXiv:2508.15734v1, Table 1 · Includes the serving infrastructure
저자 보고값 재도표 · arXiv:2611.23375v1===Replotted · arXiv:2611.23375v1
저자 보고값 재도표 · arXiv:2611.23375v1 · 입력 토큰은 비용 분모에서 제외===Replotted · arXiv:2611.23375v1 · Input tokens excluded from cost
적은 수의 중단 실행이 전체 출력 토큰의 약 3분의 2를 사용했다.===A few censored runs used about two thirds of all output tokens.
전력===Power
전력 투입===needs power
전력계의 경계를 넓혀 보기===Widen the measurement boundary
전체===Total
전체 엔트로피 생성===Total entropy production
전체 출력 토큰의 약 3분의 2 사용===about two thirds of all output tokens
정보 흐름===Information flow
정보와 에너지를 함께 따라가기===Track information and energy
정확성·유용성은 과제 기준으로 평가===Assess by task criteria
조건·판본을 남겨 다음 작업에 재사용===Retain conditions and versions for reuse
주기적 검토===Review cycle
주변 환경===Environment
진전·반복 확인===Check progress and repetition
초기 분포===Initial distribution
초기화===Reset
최종 분포===Final distribution
추가 근거가 있으면 수정===Revise with additional evidence
추론===Reasoning
추론과 행동을 이어 주는 하네스===Reasoning and action harness
출처 대조·계산·오류 기준===Source, calculation and error criteria
출처·계산·오류 기준===Sources · calculations · error criteria
측정 범위와 추정 방법 · 품질 조건 · 에너지·탄소·물의 기간별 총량===Boundaries · quality · totals: energy, carbon, water
측정 범위와 추정 방법을 함께 기록===Record boundaries and methods
토큰·에너지·시간·오류와 재시도===Tokens · energy · time · errors · retries
평가 결과를 다음 규칙 개정에 연결하는 설계 제안===Proposed feedback from evaluation to revised rules
평가 결과에 따라 설계를 갱신하는 제안 구조===Proposed feedback from evaluation to design
품질===Quality
품질 확인===Check quality
품질·에너지·탄소·물의 제약을 함께 확인===Check quality, energy, carbon and water limits
프롬프트===Prompt
필요한 증거와 계산 강도===Evidence needs and compute effort
학습된 모델===Learned model
한 비트를 비우는 물리적 과정===The physical process of resetting a bit
확보 근거·남은 작업·중단 이유===Evidence · remaining work · reason to stop
확인할 주장과 독자의 질문===Claims and reader questions
환경===Environment
활성 가속기===Active accelerators'''
LABELS = dict(line.split('===', 1) for line in PAIRS.splitlines())
TITLES = {
 1: ('Information processing and energy transfer', 'A prompt, learned model and new evidence feed tools, memory and checks. A separate physical flow supplies computing and cooling power and transfers heat to the environment.'),
 2: ('The entropy balance of one-bit reset', 'An equally probable symmetric two-state memory is reset isothermally. The memory entropy decrease accompanies an environmental increase. Total entropy production approaches zero in the ideal quasistatic limit.'),
 3: ('Different distributions of runs and token use', 'Author-reported values: 78 of 1,200 runs were stopped at 300 turns and used 65.6 percent of all output tokens. Separately, about 80 percent of successful-run output tokens came from calls that did not change goal progress.'),
 4: ('The operational energy boundary', 'Google reported 0.24 Wh for a median Gemini Apps text prompt in May 2025: active accelerators 0.14 Wh, CPU and DRAM 0.06 Wh, idle capacity 0.02 Wh and data-centre overhead 0.02 Wh.'),
 5: ('A proposed governance loop for resource-aware execution', 'A planner defines purpose, quality and budgets. The harness controls tools, memory and repetition. Independent checks precede recorded results. Unfinished work and evidence are handed over when budget or progress is inadequate. Observations feed the next policy review.')
}

def main():
    made = []
    for p in sorted(OUT.glob('fig[1-5]_*.svg')):
        if p.stem.endswith('_en'):
            continue
        n = int(p.name[3]); root = ET.parse(p).getroot()
        for el in root.iter():
            tag = el.tag.rsplit('}', 1)[-1]
            if tag in ['title', 'desc']:
                el.text = TITLES[n][0 if tag == 'title' else 1]
            elif tag == 'text' and el.text and re.search(r'[가-힣]', el.text):
                if el.text not in LABELS:
                    raise ValueError('Missing English label: '+el.text)
                el.text = LABELS[el.text]
        if n == 1 and 'desktop' in p.stem:
            for el in root.iter():
                if el.tag.rsplit('}',1)[-1]=='text' and el.text=='Environment':
                    el.set('x','1255'); el.set('font-size','27')
                if el.tag.rsplit('}',1)[-1]=='line' and el.get('x1')=='901' and el.get('x2')=='1183':
                    el.set('x2','1148')
        if 'mobile' in p.stem:
            for el in root.iter():
                if el.tag.rsplit('}',1)[-1] != 'text': continue
                if n==3 and el.text=='About 20%': el.text='~20%'
                if n==3 and el.text=='About 80%': el.text='~80%'
                if n==5 and el.text=='Claims and reader questions': el.set('x','174')
        out = p.with_name(p.stem + '_en.svg')
        ET.ElementTree(root).write(out, encoding='unicode', xml_declaration=False)
        made.append(out.name)
    print(json.dumps({'english_figures':made}))

if __name__ == '__main__': main()
