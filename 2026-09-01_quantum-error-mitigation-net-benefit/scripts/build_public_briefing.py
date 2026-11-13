# coding: utf-8
"""Correct the historical DQB with explicit edits and an ATRL revision page.

The caller supplies the private original, Korean font and private QA directory.
Original five-page geometry, scientific links and pixels outside declared edits
are checked. No registration, model execution or deployment is performed.
"""
import argparse, hashlib, json, math, re
from pathlib import Path
import fitz
from PIL import Image, ImageChops, ImageDraw
from pypdf import PdfReader

TOPIC=Path(__file__).resolve().parents[1]
ROOT=TOPIC.parent
SOURCE_SHA='754684668b37d79945b0f1e71d08b3dc0d83456e1c4373bde46ce25206045e46'

def sha(data):return hashlib.sha256(data).hexdigest()
def bitmap(page):
 p=page.get_pixmap(matrix=fitz.Matrix(2,2),alpha=False)
 return Image.frombytes('RGB',(p.width,p.height),p.samples)
def uri(page):return sorted([(x['uri'],list(x['from'])) for x in page.get_links() if x.get('uri')])
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--source',type=Path,required=True);ap.add_argument('--font',type=Path,required=True);ap.add_argument('--qa-dir',type=Path,required=True);args=ap.parse_args()
 source=fitz.open(args.source);assert sha(args.source.read_bytes())==SOURCE_SHA and len(source)==5
 public=fitz.open(stream=args.source.read_bytes(),filetype='pdf');fontbuf=args.font.read_bytes();font=fitz.Font(fontbuffer=fontbuf)
 changes=[]
 def lines(page):
  return [x for b in source[page].get_text('dict')['blocks'] for x in b.get('lines',[])]
 def edit(page,prefix,count,new,size=None):
  all_lines=lines(page);matches=[i for i,l in enumerate(all_lines) if ''.join(s['text'] for s in l['spans']).startswith(prefix)];assert len(matches)==1,prefix
  ls=all_lines[matches[0]:matches[0]+count];first=ls[0]['spans'][0];rect=fitz.Rect(61.8,ls[0]['bbox'][1]-1,535.0,ls[-1]['bbox'][3]+1)
  changes.append({'page':page,'rect':list(rect),'origin':list(first['origin']),'size':size or first['size'],'color':first['color'],'lines':new,'original_anchor':prefix})
 edit(0,'2026년 9월 1일 · 최근',1,['2026년 9월 1일 · 오류완화의 정확도와 자원비용'])
 edit(1,'반복부호로 양자 샘플링',1,['판독 반복부호의 오류 예측과 인코딩 비용'],size=14)
 edit(1,'무엇을 입증했나. 각 데이터',3,['모형 예측. 계산기저의 판독값을 k개 큐비트에 반복 인코딩해 다수결로 읽는다. 최종 비트 오류를 독립으로 취급한',
  '저자 모형은 Zuchongzhi 3.0·Willow 오류율에서 k=9–11일 때 10-8–10-9를 예측했다. 인코딩 게이트의 고장이',
  '사슬을 따라 전파할 수 있으므로, 이 수치를 실제 잡음 회로의 검증값과 구별한다.'])
 edit(1,'기술 핵심. 추가 CNOT의',2,['기술 핵심. 저자들은 CNOT 잡음을 유효 판독 오류로 옮겨 계산했다. 그 모형에서 Zuchongzhi 2.0 조건은 k=3일 때',
  'RCS fidelity 개선이 8배를 넘고 최대 약 13.3배에 포화된다. k=11은 데이터당 보조 큐비트 10개를 더 쓴다.'])
 edit(1,'한계. 실제 프로세서',2,['해석 조건. 독립적인 물리 고장이 최종 독립 비트 오류를 뜻하지는 않는다. CNOT 사슬에서 단일 X 오류가 다수결을',
  '뒤집는 예를 새 수정 페이지에 적었다. 실제 배선·상관 판독 오류·shots·실행시간은 칩에서 확인할 과제다.'])
 edit(1,'한계. 원문의 2.16은',3,['해석 조건. 표의 비율은 적응형/균등 ZNE 비교다. 공개 코드는 제안된 Neyman 식과 달리 표준편차 비율로 배분한다.',
  '표의 B는 최종 배분 샷 수이며 별도로 수행한 pilot 비용과 구별한다. 원문의 2.16은 적응형 MSE 평균 2.16×10-3과',
  '일치하지만 비율 평균은 약 2.32다. 단일 장치·calibration과 잡음모형의 시험 규칙에서 얻은 비교다.'])
 # Private collection/search context is removed rather than merely hidden.
 edit(3,'AI 학회 확인',3,['모형과 자료의 조건 · 2026-11-13','M-Diffushadow의 결과 masking은 주어진 매개변수·측정축에서 수행했다. Cavity 수치의 조건과 hBN 적용 대상은', '새 수정 페이지의 원문 대조 기록을 따른다.'],size=8.4)
 edit(4,'수집 메모',3,['수정 이력 · Agentic Tech Review Letters (ATRL)','원 발행일·근거 기준일은 2026-09-01이다. 2026-11-13 원문과 보충자료를 다시 대조해 인코딩 오류와 샷 비용의', '해석 조건을 보완하고 수집·검색 메모를 삭제했다. 새 페이지에 정식 서지와 작은 검산의 범위를 남긴다.'],size=8.4)
 for item in changes:public[item['page']].add_redact_annot(fitz.Rect(item['rect']),fill=None)
 for page in public:page.apply_redactions(images=0,graphics=0,text=0)
 def draw_lines(page,textlines,x,y,size,color=(.11,.14,.18),step=None):
  page.insert_font(fontname='ArchiveRevision',fontbuffer=fontbuf)
  for i,text in enumerate(textlines):
   assert all(font.has_glyph(ord(c)) for c in text if not c.isspace()),text
   assert x+font.text_length(text,fontsize=size)<536,(text,font.text_length(text,fontsize=size))
   page.insert_text((x,y+i*(step or size*1.5)),text,fontname='ArchiveRevision',fontsize=size,color=color)
  return y+len(textlines)*(step or size*1.5)
 for item in changes:
  c=item['color'];rgb=tuple(((c>>shift)&255)/255 for shift in (16,8,0));draw_lines(public[item['page']],item['lines'],*item['origin'],item['size'],rgb,step=14)
 # Restore every original public scientific URI and its rectangle after true redaction.
 for before,after in zip(source,public):
  for link in list(after.get_links()):after.delete_link(link)
  for link in before.get_links():
   if link.get('uri'):after.insert_link({'kind':fitz.LINK_URI,'from':link['from'],'uri':link['uri']})
 page=public.new_page(width=source[0].rect.width,height=source[0].rect.height);y=draw_lines(page,['Agentic Tech Review Letters (ATRL)','수정 이력과 정식 참고문헌 · 2026-11-13'],62.7,58,12,step=20)+12
 def wrap(text,size):
  out=[];line=''
  for word in text.split(' '):
   candidate=(line+' '+word).strip()
   if font.text_length(candidate,fontsize=size)>472 and line:out.append(line);line=word
   else:line=candidate
  if line:out.append(line)
  return out
 notes=[
  '원 발행일·근거 기준일은 2026-09-01이다. 원 Daily Quantum Brief의 과학 기록과 링크를 보존하고 수집·검색 메모를 삭제했다. 2026-11-13 원문 재검토로 인코딩 오류와 샷 비용의 해석 조건을 보완했다.',
  'Huang의 최종 독립 비트 오류 모형값은 저자 보고 예측이다. 보충자료의 CNOT1→2, CNOT2→3에서 입력 000에 첫 게이트 직후 두 번째 비트의 X 오류 하나가 생기면 010→011이 되어 다수결이 뒤집힌다. 독립 게이트 고장도 상관된 최종 오류를 만든다. 이는 작은 검산이며 전체 잡음모형의 수정 성능을 계산한 것이 아니다.',
  'Chongder의 여섯 예산은 보정값 기반 모사다. 공개 배분 코드는 제안된 외삽 계수 가중 Neyman 식과 다르며, 별도 pilot까지 포함한 총비용을 확인해야 한다. M-Diffushadow는 주어진 매개변수·측정축에서 결과 토큰을 가린다. Cavity의 0.15 Angstrom·0.8 Angstrom·18% 수치는 본문 hBN 계산에 해당한다.',
  'root가 편집·공개 사본을 통합하고 독립 담당이 원문·보충자료·선택 코드와 산술을 대조했다. 원 모델·실험·QPU·학습은 재실행하지 않았다. 원 발행팀과 새 감수 역할·판본은 웹 리뷰의 작성·검증 이력과 공개 참고 기록을 따른다.'
 ]
 for text in notes:y=draw_lines(page,wrap(text,8.3),62.7,y,8.3,step=12.1)+7
 y=draw_lines(page,['References'],62.7,y+3,11,step=16)+5
 refs=json.loads((ROOT/'.automation/writing-reviews/legacy-refresh/2026-11-13-error-mitigation/reference-manifest.json').read_text())['references']
 for ref in refs:
  text='[%d] '%ref['number']+ref['text'];links=[ref['url']]
  if ref.get('software'):text=text.rstrip('.')+'; '+ref['software']['text'];links.append(ref['software']['url'])
  start=y;ls=wrap(text,7.8);y=draw_lines(page,ls,62.7,y,7.8,step=10.8)+7
  for index,url in enumerate(links):
   page.insert_link({'kind':fitz.LINK_URI,'from':fitz.Rect(62.7+index*240,start-8,297.7+index*240,y-7),'uri':url})
 assert y<787,('appendix overflow',y)
 draw_lines(page,['ATRL · 2026-11-13 · 원 Daily Quantum Brief 2026-09-01'],62.7,813,7.1)
 draw_lines(page,['6'],530,813,7.1)
 public.set_metadata({'title':'Daily Quantum Brief 2026-09-01 — revised public edition','author':'Agentic Tech Review Letters','subject':'Original evidence cutoff 2026-09-01; source-comparison revision 2026-11-13','creator':'ATRL public archive builder','creationDate':source.metadata.get('creationDate',''),'modDate':'D:20261113000000Z'})
 public.del_xml_metadata();public.subset_fonts();out=TOPIC/'artifacts/daily_quantum_brief_2026-09-01.pdf';public.save(out,garbage=4,deflate=True,clean=True);public.close();final=fitz.open(out);args.qa_dir.mkdir(parents=True,exist_ok=True)
 checks=[]
 for i,(a,b) in enumerate(zip(source,final)):
  aa,bb=bitmap(a),bitmap(b);regions=[x['rect'] for x in changes if x['page']==i]
  for rect in regions:
   box=(math.floor(rect[0]*2)-2,math.floor(rect[1]*2)-2,math.ceil(rect[2]*2)+2,math.ceil(rect[3]*2)+2)
   ImageDraw.Draw(aa).rectangle(box,fill='white');ImageDraw.Draw(bb).rectangle(box,fill='white')
  check={'page':i+1,'declared_edit_rectangles_pt':regions,'pixels_equal_outside_edits_144dpi':ImageChops.difference(aa,bb).getbbox() is None,'original_uri_and_rectangles_preserved':uri(a)==uri(b),'page_geometry_preserved':a.rect==b.rect};assert all(v for k,v in check.items() if k not in ['page','declared_edit_rectangles_pt']),check;checks.append(check)
 for i,page in enumerate(final):bitmap(page).save(args.qa_dir/('public-%d.png'%(i+1)))
 text='\n'.join(p.get_text() for p in final);assert not re.search(r'[/](?:Users|home)[/]|@[A-Za-z]|LinkedIn|지난 실행|최근 24시간|\ufffd|\x00',text)
 reader=PdfReader(out,strict=True);assert len(reader.pages)==6 and not reader.attachments and not reader.get_fields()
 for i in range(1,final.xref_length()):
  obj=final.xref_object(i);assert not re.search(r'/(JavaScript|JS|Launch|OpenAction|AA|EmbeddedFiles|SubmitForm)\b',obj)
 assert all(x['uri'].startswith('https://') for page in final for x in page.get_links() if x.get('uri'))
 report={'date':'2026-11-13','source_sha256':SOURCE_SHA,'sha256':sha(out.read_bytes()),'source_pages':5,'pages':6,'appendix_bottom_pt':y,'page_checks':checks,'original_scientific_uri_annotations':sum(len(uri(page)) for page in source),'inspection':{'strict_pypdf':True,'no_attachments':True,'no_forms':True,'no_active_actions':True,'no_private_collection_context_or_paths':True,'public_https_uris_only':True,'no_missing_glyphs':True},'visual_review':{'status':'pending'},'independent_review':{'status':'pending'},'original_model_or_experiment_reproduction':False}
 (args.qa_dir/'production-qa.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'sha256':report['sha256'],'pages':6,'appendix_bottom':y}))
if __name__=='__main__':main()
