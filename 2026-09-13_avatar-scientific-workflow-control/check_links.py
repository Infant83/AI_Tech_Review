"""GET-check public references; optionally include newly deployed article URLs."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import json
import sys
from urllib.request import Request, urlopen

P=Path(__file__).resolve().parent
urls=json.loads((P/'notes/package_validation.json').read_text())['external_reference_urls']
if '--include-live' not in sys.argv:
    urls=[u for u in urls if P.name not in u]
def check(url):
    try:
        with urlopen(Request(url,headers={'User-Agent':'AI-Tech-Review-Link-Check/1.0'}),timeout=45) as r:
            body=r.read()
            return {'url':url,'status':r.status,'final_url':r.url,'bytes':len(body)}
    except Exception as e:
        return {'url':url,'error':str(e)}
with ThreadPoolExecutor(max_workers=6) as pool:
    results=list(pool.map(check,urls))
(P/'notes/link_validation.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(results,ensure_ascii=False,indent=2))
sys.exit(any('error' in r or r['status']!=200 for r in results))
