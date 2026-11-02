import sys, time; sys.path.insert(0,'.')
import numpy as np
from hyb_model import *
K,Vt=calibrate(); base=dict(DEF,K=K,Vt=Vt)
cfg={'nodroop':dict(base),'vout_only':dict(base,droop=1),'vout_only_toff300n':dict(base,droop=1,t_off=300e-9),
     'gate1.30_toff300n':dict(base,droop=1,V_gate=1.30,t_off=300e-9),'gate1.20_toff1u':dict(base,droop=1,V_gate=1.20,t_off=1e-6)}
names=list(cfg); P=[cfg[k] for k in names]
# 序列：5 mA → 95 mA(100 ns) → 45 → 20 → 5，每段 10 µs
te=100e-9
tb=np.array([0,10e-6,10e-6+te,20e-6,20e-6+te,30e-6,30e-6+te,40e-6,40e-6+te,50e-6])
Ib=np.array([[5,5,95,95,45,45,20,20,5,5]]*len(P))*1e-3
t0=time.time(); r=sim(P,tb,Ib,50e-6); print('time',time.time()-t0)
pre=r['V'][(r['t']>9.5e-6)&(r['t']<10e-6)].mean(0); us=pre-r['V'][(r['t']>10e-6)&(r['t']<12e-6)].min(0)
for j,nm in enumerate(names):
    s=f"{nm:22s} US100ns={us[j]*1e3:6.1f} mV |"
    for (a,b,L) in ((5e-6,10e-6,5),(15e-6,20e-6,95),(25e-6,30e-6,45),(35e-6,40e-6,20),(45e-6,50e-6,5)):
        pp,mean,nch,ndr=window_metrics(r,a,b,1.6)
        s+=f" {L}mA pp{pp[j]:6.1f} mean{mean[j]:+6.1f} chg{nch[j]:3d} dr{ndr[j]:3d} code{r['code'][(r['t']>=a)&(r['t']<b)][:,j].min()}-{r['code'][(r['t']>=a)&(r['t']<b)][:,j].max()} |"
    print(s)
np.savez('res/h1_quick.npz',t=r['t'],V=r['V'],pg=r['pg'],code=r['code'],droop=r['droop'],names=names)
