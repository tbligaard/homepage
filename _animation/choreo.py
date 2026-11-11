import numpy as np
from scipy.spatial.transform import Rotation as Rot, Slerp
FPS=30; T=21.0; F=int(T*FPS); SHIFT=0.8
ts=np.arange(F)/FPS-SHIFT
y0=-10.65; s=1.775
n=np.array([0,-1.0,0]); ex=np.array([1.0,0,0]); ez=np.array([0,0,1.0])
def site(k,m,h): return np.array([k*s, y0-h, 2.1+m*s])
Hh,Ch,Oh=0.80,0.95,1.00
EL=[]; POS=[]
def new(el):
    EL.append(el); POS.append(np.full((F,3),np.nan)); return len(EL)-1
def fr(t): return int(round((t+SHIFT)*FPS))
def sm(u): u=np.clip(u,0,1); return u*u*u*(u*(6*u-15)+10)
def hold(a,t0,t1,p):
    for i in range(fr(t0),min(fr(t1),F)): POS[a][i]=p
def move(a,t0,t1,p0,p1,arc=0.4):
    for i in range(fr(t0),min(fr(t1),F)):
        u=(ts[i]-t0)/(t1-t0); w=sm(u)
        POS[a][i]=p0+(p1-p0)*w+n*arc*np.sin(np.pi*w)
def rigid(atoms,offs0,offs1,t0,t1,c0,c1,ctrl,easing,spin=None):
    """centre along quadratic bezier c0->ctrl->c1; internal geometry slerps from offs0 frame to offs1 frame plus spin"""
    for i in range(fr(t0),min(fr(t1),F)):
        u=(ts[i]-t0)/(t1-t0); w=easing(u)
        c=(1-w)**2*c0+2*(1-w)*w*ctrl+w*w*c1
        for a,o0,o1 in zip(atoms,offs0,offs1):
            o=o0+(o1-o0)*sm(min(1,max(0,(u-0.0)/1.0))) if spin is None else spin(u,o0,o1)
            POS[a][i]=c+o
def tumble(axis,turns,blend_at):
    """rotate offsets about axis by turns*360*(1-u) and blend to final offsets near end/start"""
    def f(u,o0,o1):
        ang=turns*2*np.pi*(1-u)
        R=Rot.from_rotvec(np.array(axis)/np.linalg.norm(axis)*ang)
        return R.apply(o1)
    return f
def tumble_out(axis,turns):
    def f(u,o0,o1):
        R=Rot.from_rotvec(np.array(axis)/np.linalg.norm(axis)*turns*2*np.pi*u)
        return R.apply(o0)
    return f
ease_in=lambda u: 1-np.cos(np.pi*u/2)
ease_out=lambda u: np.sin(np.pi*u/2)
ease_exit=lambda u: 0.35*u+0.65*u*u
# ---------- H2 arrivals ----------
def h2_arrive(t0,t1,k,m,start,axis,t_split,t_split_end,dst):
    a=new('H'); b=new('H')
    land=site(k,m,1.9)   # above atom
    start=land+start
    o=0.37*ex
    rigid([a,b],[-o,o],[-o,o],t0,t1,start,land,(start+land)/2+np.array([0,0,10]),ease_out,tumble(axis,0.6,0))
    hold(a,t1,t_split,land-o); hold(b,t1,t_split,land+o)
    move(a,t_split,t_split_end,land-o,site(*dst[0],Hh),0.0)
    move(b,t_split,t_split_end,land+o,site(*dst[1],Hh),0.0)
    return a,b
Ha,Hb=h2_arrive(-0.8,2.6,1,1,np.array([-17,-14,20.0]),[0.3,1,0.2],2.9,3.7,[(2,1),(0,1)])
Hc,Hd=h2_arrive(1.2,5.0,1,3,np.array([19,-14,18.0]),[1,0.2,0.4],5.3,6.1,[(2,3),(1,4)])
He,Hf=h2_arrive(8.6,12.0,0,2,np.array([-18,-12,17.0]),[0.2,0.4,1],12.3,13.1,[(1,2),(-1,2)])
# ---------- CO ----------
C=new('C'); O=new('O')
top=site(2,2,0)  # atom position projected; on-top: C at 1.85
cC=site(2,2,1.85); cO=site(2,2,1.85+1.15)
st=cC+np.array([6,-16,22.0])
rigid([C,O],[np.zeros(3),1.15*n],[np.zeros(3),1.15*n],0.0,4.4,st,cC,(st+cC)/2+np.array([4,0,8]),ease_out,tumble([0.5,0.2,1],0.7,0))
hold(C,4.4,5.8,cC); hold(O,4.4,5.8,cO)
# dissociation: tilt then split
Cs=site(3,2,Ch); O1=site(1,2,Oh)
mid_C=site(2.5,2,1.3); mid_O=site(1.6,2,1.9)
move(C,5.8,6.4,cC,mid_C,0); move(O,5.8,6.4,cO,mid_O,0)
move(C,6.4,7.0,mid_C,Cs,0); move(O,6.4,7.0,mid_O,O1,0)
# O diffusion
hold(O,7.0,7.2,O1)
move(O,7.2,7.9,O1,site(0,3,Oh)); hold(O,7.9,8.3,site(0,3,Oh))
move(O,8.3,9.0,site(0,3,Oh),site(-1,2,Oh)); hold(O,9.0,9.4,site(-1,2,Oh))
Os=site(-2,3,Oh)
move(O,9.4,10.1,site(-1,2,Oh),Os)
# ---------- C hydrogenation ----------
def dirv(theta,phi):  # angle theta from n, azimuth phi in facet plane
    t=np.radians(theta); p=np.radians(phi)
    return np.cos(t)*n+np.sin(t)*(np.cos(p)*ex+np.sin(p)*ez)
d=1.09
CH1={Ha:Cs+d*n}
CH2={Ha:Cs+d*dirv(55,0),Hc:Cs+d*dirv(55,180)}
CH3={Ha:Cs+d*dirv(70.5,0),Hc:Cs+d*dirv(70.5,120),Hb:Cs+d*dirv(70.5,240)}
Cup=site(3,2,2.45)
CH4={Ha:Cup+d*dirv(70.5,0),Hc:Cup+d*dirv(70.5,120),Hb:Cup+d*dirv(70.5,240),He:Cup-d*n}
hold(C,7.0,14.2,Cs)
# Ha: (2,1) -> CH
hold(Ha,3.7,7.6,site(2,1,Hh)); move(Ha,7.6,8.4,site(2,1,Hh),CH1[Ha],0.3); hold(Ha,8.4,9.6,CH1[Ha])
# Hc: (2,3) -> CH2
hold(Hc,6.1,9.6,site(2,3,Hh)); move(Hc,9.6,10.4,site(2,3,Hh),CH2[Hc],0.3); move(Ha,9.6,10.4,CH1[Ha],CH2[Ha],0)
hold(Ha,10.4,11.6,CH2[Ha]); hold(Hc,10.4,11.6,CH2[Hc])
# Hb: (0,1) -> (1,2) -> (2,1) -> CH3
hold(Hb,3.7,9.0,site(0,1,Hh)); move(Hb,9.0,9.6,site(0,1,Hh),site(1,2,Hh)); hold(Hb,9.6,10.4,site(1,2,Hh))
move(Hb,10.4,11.0,site(1,2,Hh),site(2,1,Hh)); hold(Hb,11.0,11.6,site(2,1,Hh))
move(Hb,11.6,12.4,site(2,1,Hh),CH3[Hb],0.3); move(Ha,11.6,12.4,CH2[Ha],CH3[Ha],0); move(Hc,11.6,12.4,CH2[Hc],CH3[Hc],0)
for h in (Ha,Hb,Hc): hold(h,12.4,14.2,CH3[h])
# He: (1,2) -> (2,3) -> CH4
hold(He,13.1,13.2,site(1,2,Hh))
move(He,13.2,13.8,site(1,2,Hh),site(2,3,Hh)); 
move(He,14.2,15.0,site(2,3,Hh),CH4[He],0.2); hold(He,13.8,14.2,site(2,3,Hh))
move(C,14.2,15.0,Cs,Cup,0)
for h in (Ha,Hb,Hc): move(h,14.2,15.0,CH3[h],CH4[h],0)
# CH4 desorption
grpC=[C,Ha,Hb,Hc,He]; offC=[np.zeros(3)]+[CH4[h]-Cup for h in (Ha,Hb,Hc,He)]
for a,o in zip(grpC,offC): hold(a,15.0,15.4,Cup+o)
endC=Cup+np.array([9,-17,26.0])
rigid(grpC,offC,offC,15.4,19.2,Cup,endC,Cup+np.array([1,-8,3.0]),ease_exit,tumble_out([0.3,0.5,1],0.5))
# ---------- O hydrogenation ----------
hold(O,10.1,13.6,Os)
OH={Hd:Os+0.97*n}
Oup=site(-2,3,2.1)
H2O={Hd:Oup+0.96*dirv(52,0)+0*n,Hf:Oup+0.96*dirv(52,180)}
# Hd: (1,4) -> (0,5)?  path: (1,4)->(0,3)->(-1,4)-> OH
hold(Hd,6.1,9.6,site(1,4,Hh)); move(Hd,9.6,10.2,site(1,4,Hh),site(0,3,Hh)); hold(Hd,10.2,10.8,site(0,3,Hh))
move(Hd,10.8,11.4,site(0,3,Hh),site(-1,4,Hh)); hold(Hd,11.4,12.0,site(-1,4,Hh))
move(Hd,12.0,12.8,site(-1,4,Hh),OH[Hd],0.3); hold(Hd,12.8,13.6,OH[Hd])
# Hf: (-1,2) -> H2O
hold(Hf,13.1,13.6,site(-1,2,Hh))
move(Hf,13.6,14.4,site(-1,2,Hh),H2O[Hf],0.3); move(Hd,13.6,14.4,OH[Hd],H2O[Hd],0); move(O,13.6,14.4,Os,Oup,0)
grpO=[O,Hd,Hf]; offO=[np.zeros(3),H2O[Hd]-Oup,H2O[Hf]-Oup]
for a,o in zip(grpO,offO): hold(a,14.4,14.8,Oup+o)
endO=Oup+np.array([-12,-16,19.0])
rigid(grpO,offO,offO,14.8,18.4,Oup,endO,Oup+np.array([-1,-8,3.0]),ease_exit,tumble_out([1,0.3,0.4],0.5))
# ---------- gentle thermal jiggle for adsorbed (non-flying) frames ----------
P=np.array(POS)  # N,F,3
rng=np.random.default_rng(3)
for a in range(len(EL)):
    ks=rng.integers(18,40,size=(3,2)); ph=rng.uniform(0,2*np.pi,size=(3,2))
    j=np.zeros((F,3))
    for dim in range(3):
        for q in range(2): j[:,dim]+=0.035*np.sin(2*np.pi*ks[dim,q]*ts/T+ph[dim,q])
    P[a]+=j
# sanity: gaps (atom visible, then invisible, then visible again)
for a in range(len(EL)):
    vis=~np.isnan(P[a,:,0]); idx=np.where(vis)[0]
    gaps=np.where(np.diff(idx)>1)[0]
    if len(gaps): print('GAP atom',a,EL[a],[(idx[g]/FPS,idx[g+1]/FPS) for g in gaps])
    # max per-frame displacement
    dp=np.linalg.norm(np.diff(P[a],axis=0),axis=1); dp=dp[~np.isnan(dp)]
    print(a,EL[a],'visible %.2f-%.2f'%(idx[0]/FPS,idx[-1]/FPS),'max step %.2f'%dp.max())
np.savez('traj.npz',el=np.array(EL),pos=P)
