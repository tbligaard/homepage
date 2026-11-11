import numpy as np
from ase import Atoms
from ase.io import write
a=3.55  # Ni3Fe L12
# L12 basis: Fe at corner, Ni at face centers
basis=[('Fe',(0,0,0)),('Ni',(.5,.5,0)),('Ni',(.5,0,.5)),('Ni',(0,.5,.5))]
n=8
pos=[];sym=[]
for i in range(-n,n):
  for j in range(-n,n):
    for k in range(-n,n):
      for s,(x,y,z) in basis:
        pos.append(((i+x)*a,(j+y)*a,(k+z)*a)); sym.append(s)
pos=np.array(pos)
# centre on an atom (Fe at origin) -> symmetric
d100=12.0; d111=0.87*d100*1.0  # Wulff distances (Å), gamma111/gamma100 ~0.87
normals=[]
for v in [(1,0,0),(0,1,0),(0,0,1)]:
  for sgn in (1,-1): normals.append((np.array(v)*sgn,d100))
for sx in (1,-1):
  for sy in (1,-1):
    for sz in (1,-1): normals.append((np.array([sx,sy,sz])/np.sqrt(3),d111))
keep=np.ones(len(pos),bool)
for nv,d in normals:
  keep &= pos@nv <= d+1e-6
# Winterbottom truncation at interface: cut below z = -h
h=0.35*d100
keep &= pos[:,2] >= -h-1e-6
P=pos[keep]; S=[s for s,k in zip(sym,keep) if k]
zmin=P[:,2].min(); P[:,2]-=zmin
print('particle atoms',len(P),'Ni',S.count('Ni'),'Fe',S.count('Fe'),'height',P[:,2].max(),'width',np.ptp(P[:,0]))
# MgO(100) slab, rocksalt a=4.21, 3 layers
b=4.21; m=12; L=3
spos=[];ssym=[]
for i in range(-m,m):
  for j in range(-m,m):
    for l in range(L):
      for (x,y),s in [((0,0),'O'),((.5,.5),'O'),((.5,0),'Mg'),((0,.5),'Mg')]:
        # alternate per layer
        if l%2: s={'O':'Mg','Mg':'O'}[s]
        spos.append(((i+x)*b,(j+y)*b,-l*b/2)); ssym.append(s)
spos=np.array(spos)
# place particle: bottom layer 2.1 Å above top O layer, centred on an O site
P[:,2]+=2.1
np.save('particle_pos.npy',P); np.save('support_pos.npy',spos)
open('particle_sym.txt','w').write(' '.join(S)); open('support_sym.txt','w').write(' '.join(ssym))
write('scene.xyz',Atoms(S+ssym,positions=np.vstack([P,spos])))
print('support atoms',len(spos))
