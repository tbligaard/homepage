import sys,time,os; sys.path.insert(0,'.')
import scene,bpy,numpy as np
mode=sys.argv[1]   # plate | frames
W,H=1280,720
samples=int(sys.argv[2])
scene.setup(res=(W,H),samples=samples)
sc=bpy.context.scene; sc.cycles.seed=7
static=[]
P=np.load('particle_pos.npy'); S=open('particle_sym.txt').read().split()
for s_,p in zip(S,P): static.append(scene.atom(s_,tuple(p)))
Q=np.load('support_pos.npy'); Tt=open('support_sym.txt').read().split()
for s_,p in zip(Tt,Q):
    r2=p[0]**2+p[1]**2
    if r2<=48**2 and (p[2]>-1 or r2<26**2): static.append(scene.atom('Mg' if s_=='Mg' else 'Os',tuple(p)))
scene.camera()
os.makedirs('frames',exist_ok=True)
if mode=='plate':
    sc.render.filepath='/home/claude/np/plate.png'; bpy.ops.render.render(write_still=True); sys.exit()
for o in static: o.is_holdout=True
d=np.load('traj.npz'); el=d['el']; pos=d['pos']
objs=[scene.atom(e,(0,0,-100)) for e in el]
frames=[int(x) for x in sys.argv[3].split(',')] if ',' in sys.argv[3] else range(int(sys.argv[3]),int(sys.argv[4]))
for f in frames:
    out=f'/home/claude/np/frames/h_{f:04d}.png'
    if os.path.exists(out): continue
    for o,p in zip(objs,pos[:,f]):
        if np.isnan(p[0]): o.hide_render=True; o.location=(0,0,-100)
        else: o.hide_render=False; o.location=tuple(p)
    sc.render.filepath=out+'.tmp.png'
    t=time.time(); bpy.ops.render.render(write_still=True); os.rename(out+'.tmp.png',out)
    print('frame',f,'%.1fs'%(time.time()-t),flush=True)
