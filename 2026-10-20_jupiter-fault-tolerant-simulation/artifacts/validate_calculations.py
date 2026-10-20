"""Check the article's independent teaching arithmetic, not a quantum protocol run.

Only Python's standard library is needed. The coherent example is checked by
repeatedly evolving a two-component vector; the stochastic example is checked
with a two-state probability recurrence, independently of the closed forms.
"""
from pathlib import Path
import cmath, json, math
OUT=Path(__file__).resolve().parent

def main():
    theta=.01; repeats=20
    p=math.sin(theta/2)**2
    coherent=math.sin(repeats*theta/2)**2
    stochastic=(1-(1-2*p)**repeats)/2
    psi=[complex(1/math.sqrt(2)),complex(1/math.sqrt(2))]
    for _ in range(repeats):
        psi[0]*=cmath.exp(-1j*theta/2)
        psi[1]*=cmath.exp(1j*theta/2)
    direct_coherent=abs((psi[0]-psi[1])/math.sqrt(2))**2
    q=0.
    for _ in range(repeats):q=q*(1-p)+(1-q)*p
    assert math.isclose(coherent,direct_coherent,rel_tol=1e-12,abs_tol=1e-15)
    assert math.isclose(stochastic,q,rel_tol=1e-11,abs_tol=1e-15)
    memory=[{'encoded_bits':n,'amplitudes':2**n,'state_bytes':16*2**n,'state_TiB':2**(n-36)} for n in [40,45,46,50]]
    assert [m['state_TiB'] for m in memory]==[16,512,1024,16384]
    per_gpu=16*2**45//8192
    assert per_gpu==64*2**30
    qutrits={'qutrit_count':5,'basis_states':3**5,'binary_bits':math.ceil(math.log2(3**5)),'binary_entries':2**8,'padding_entries':2**8-3**5}
    assert qutrits=={'qutrit_count':5,'basis_states':243,'binary_bits':8,'binary_entries':256,'padding_entries':13}
    output={
      'purpose':'Independent arithmetic for educational examples. No JUPITER simulation, QPU experiment, error-correction circuit or performance measurement is reproduced.',
      'coherent_vs_stochastic':{'theta_radians':theta,'repetitions':repeats,'single_step_p':p,'coherent_X_minus_probability':coherent,'coherent_X_minus_percent':100*coherent,'stochastic_X_minus_probability':stochastic,'stochastic_X_minus_percent':100*stochastic,'independent_checks':{'repeated_two_amplitude_evolution':direct_coherent,'stochastic_probability_recurrence':q}},
      'complex128_memory':{'bytes_per_amplitude':16,'cases':memory,'gpu_count':8192,'45_bit_state_GiB_per_GPU':per_gpu/2**30,'excluded':'Workspace, communication buffers, factorization analysis and runtime overhead.'},
      'illustrative_qutrit_encoding':qutrits
    }
    (OUT/'teaching_calculations.json').write_text(json.dumps(output,indent=2)+'\n')
    print(json.dumps({'validated':True,'coherent_percent':100*coherent,'stochastic_percent':100*stochastic,'45_bit_state_TiB':512,'state_GiB_per_GPU':64,'qutrit_padding':13}))
if __name__=='__main__':main()
