import sys, json, time; sys.path.insert(0,'.')
import numpy as np
from hyb_model import *
K,Vt=calibrate(); print('K,Vt',K,Vt)
p=dict(DEF,K=K,Vt=Vt)
for I in (3e-3,18e-3): print(I, pg_for_current(I,1.6,1.8,K,Vt))
print('I_a at pg=e_min(0.9),Vsd=.2:', ia_pmos(0.9,1.6,1.8,K,Vt), ' at pg=1.76:', ia_pmos(1.76,1.6,1.8,K,Vt), ' pg 1.6:',ia_pmos(1.6,1.6,1.8,K,Vt))
f=np.logspace(3,9,600)
def marg(T):
    mag=20*np.log10(abs(T)); ph=np.degrees(np.unwrap(np.angle(T))); ph-=360*np.round(ph[0]/360)
    i=np.where((mag[:-1]>0)&(mag[1:]<=0))[0]
    if len(i)==0: return mag[0],np.nan,np.nan
    i=i[0]; return mag[0], f[i]/1e6, 180+ph[i]
out=[]
for Ia in (0.2e-3,1e-3,3e-3,10e-3,18e-3,50e-3,90e-3):
  for nsl in (0,4,8):
    Gs=12.2e-3/(0.2*(1-0.2/(2*1.38)))*(1-0.2/1.38)*nsl
    T,gma=loopgain_lin(p,Ia,Gs,f); dc,ugf,pm=marg(T)
    out.append(dict(Ia_mA=Ia*1e3,n_slices=nsl,gm_a_mS=round(gma*1e3,1),dc_db=round(dc,1),ugf_MHz=round(ugf,2),pm=round(pm,1)))
    print(out[-1])
json.dump(dict(K=K,Vt=Vt,loop=out),open('res/h0_loop.json','w'),indent=1)
# 純類比（凍結碼 0）大步階：5→95 mA，100 ns / 1 ns 邊沿；與 4 片固定比較
P=[dict(p,VL=-1.0,VH=9.0) for _ in range(2)]
for te in (100e-9,1e-9):
    tb=np.array([0,3e-6,3e-6+te,12e-6]); Ib=np.array([[5e-3,5e-3,95e-3,95e-3]]*2)
    t0=time.time(); r=sim(P,tb,Ib,12e-6); 
    pre=r['V'][(r['t']>2.5e-6)&(r['t']<3e-6)].mean(0); mn=r['V'][r['t']>3e-6].min(0)
    print('analog-only 5->95mA edge',te,'undershoot mV',(pre-mn)*1e3,'v_end',r['V'][-1], 'time',time.time()-t0)
