"""Recalculate the independent teaching examples using only the standard library."""
import json
import math
from pathlib import Path

root = Path(__file__).resolve().parents[1]
out = root / 'tmp' / 'examples.json'
out.parent.mkdir(parents=True, exist_ok=True)
sigma = ((.04,.01),(.01,.09))
mu = (.08,.12)
portfolio = []
for x in ((0,0),(1,0),(0,1),(1,1)):
    risk = sum(x[i]*sigma[i][j]*x[j] for i in range(2) for j in range(2))
    ret = sum(x[i]*mu[i] for i in range(2))
    portfolio.append({'x':x,'cost':round(risk-ret+(sum(x)-1)**2,10)})
a = 13/30
result = {
 'grover_success':[math.sin((2*r+1)*math.pi/6)**2 for r in range(3)],
 'portfolio':portfolio,
 'encoded_payoff_se':30*math.sqrt(a*(1-a)/10000),
 'direct_payoff_se':math.sqrt(141/10000),
 'at_least_one_success':1-(1-.001)**1000,
 'loop_seconds':[100*(2+.3+.2),2+100*(.3+.2)],
 'statevector_gib':{n:16*2**n/2**30 for n in (30,32,40)},
 'feasible_integer_allocations':sum(1 for i in range(8) for j in range(8) for k in range(8) if i+j+k<=6),
}
assert [p['cost'] for p in portfolio]==[1,-.04,-.03,.95]
assert result['feasible_integer_allocations']==84
assert abs(result['grover_success'][1]-1)<1e-12
out.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result))
