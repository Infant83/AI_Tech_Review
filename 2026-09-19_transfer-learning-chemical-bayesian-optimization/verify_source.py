"""Check specific review statements against a supplied TL-ChemBO checkout.

No campaign is fitted or executed. The task-label probe runs the inspected
function with minimal dependency stubs and small synthetic pandas tables.
Usage: python verify_source.py PATH_TO_TL_CHEMBO
"""
import ast
import math
from pathlib import Path
import sys
import types
import pandas as pd

source=Path(sys.argv[1])
tree=ast.parse((source/'transfer_loop.py').read_text())
ns={'pd':pd,'N_ITER_ALL':30,'IMPUTE_MODE':'ignore'}
def searchspace(**kw):return types.SimpleNamespace(comp_rep_columns=['x','task'],parameters=[])
ns.update({
 'load_data':lambda **kw:{'lookup':pd.DataFrame({'x':[2]}),'F_BEST':1,'objective':None,'numerical_params':{},'discrete_data':{}},
 'generate_FP':lambda *a,**kw:{},
 'TaskParameter':type('TaskParameter',(),{'__init__':lambda self,**kw:None}),
 'create_search_space':searchspace,
 '_build_campaign':lambda *a,**kw:None,
 '_filter_lookup':lambda x,*a:x,
 '_filter_campaign':lambda x,*a:x,
 '_unwrapped_simulate':lambda campaign,lookup,**kw:(lookup,kw['init_data']),
})
selected=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='run_phase_2']
exec(compile(ast.Module(body=selected,type_ignores=[]),'<source function probe>','exec'),ns)
history=[pd.DataFrame({'origin':['A','B'],'x':[0,1]})]
lookup,observed=ns['run_phase_2']('synthetic','none','0',history,'x',[2],use_task_p=True)
assert observed[0]['transfer_task'].tolist()==['training','training']
assert lookup['transfer_task'].tolist()==['test']

ktree=ast.parse((source/'base'/'kernels.py').read_text())
kns={'math':math,'KernelFactory':object}
def record(*args,**kwargs):return {'args':args,**kwargs}
kns.update({k:record for k in ['GammaPrior','ScaleKernel','MaternKernel','RBFKernel']})
exec(compile(ast.Module(body=[n for n in ktree.body if isinstance(n,ast.ClassDef)],type_ignores=[]),'<kernel construction probe>','exec'),kns)
for d in [32,128,512,2048]:
 result=kns['MaternKernelFactory']('adaptive_emilien',d,'Matern')(None,None,None)
 mu=.4*math.sqrt(d)+4
 assert result['args'][0]['lengthscale_prior']['args']==(2*mu,2.0)
 assert result['outputscale_prior']['args']==(mu,1.0)
 print(f'd={d}; length-scale prior mean={mu:.6f}; shape/rate construction matches')
print('Task-label probe: A+B -> training; C lookup -> test. No BO performance reproduced.')
