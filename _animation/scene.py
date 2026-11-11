import bpy, numpy as np, math, mathutils
R={'Ni':1.24,'Fe':1.26,'Mg':0.95,'Os':1.05,'C':0.82,'O':0.78,'H':0.52}
def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)
def mat(name,col,metal=0.0,rough=0.4,coat=0.0):
    m=bpy.data.materials.new(name); m.use_nodes=True
    b=m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value=(*col,1)
    b.inputs['Metallic'].default_value=metal
    b.inputs['Roughness'].default_value=rough
    if coat: b.inputs['Coat Weight'].default_value=coat; b.inputs['Coat Roughness'].default_value=0.1
    return m
MATS={}
FADE=(24.0,46.0)
def fade(m):
    nt=m.node_tree; out=nt.nodes['Material Output']; b=nt.nodes['Principled BSDF']
    oi=nt.nodes.new('ShaderNodeObjectInfo'); sep=nt.nodes.new('ShaderNodeSeparateXYZ')
    comb=nt.nodes.new('ShaderNodeCombineXYZ'); ln=nt.nodes.new('ShaderNodeVectorMath'); ln.operation='LENGTH'
    nt.links.new(oi.outputs['Location'],sep.inputs[0])
    nt.links.new(sep.outputs['X'],comb.inputs['X']); nt.links.new(sep.outputs['Y'],comb.inputs['Y'])
    nt.links.new(comb.outputs[0],ln.inputs[0])
    mr=nt.nodes.new('ShaderNodeMapRange'); mr.inputs['From Min'].default_value=FADE[0]; mr.inputs['From Max'].default_value=FADE[1]
    mr.inputs['To Min'].default_value=1.0; mr.inputs['To Max'].default_value=0.0
    nt.links.new(ln.outputs['Value'],mr.inputs['Value'])
    nt.links.new(mr.outputs['Result'],b.inputs['Alpha'])
    return m
MESH={}
def setup(res=(1280,720),samples=64):
    reset()
    sc=bpy.context.scene
    sc.render.engine='CYCLES'; sc.cycles.device='CPU'
    sc.cycles.samples=samples; sc.cycles.use_denoising=True
    sc.render.resolution_x,sc.render.resolution_y=res; sc.render.resolution_percentage=100
    sc.render.film_transparent=True
    sc.view_settings.view_transform='AgX'; sc.view_settings.look='AgX - Medium High Contrast'
    sc.cycles.max_bounces=6
    # world: soft studio gradient (bright top) for metal reflections
    w=bpy.data.worlds.new('W'); sc.world=w; w.use_nodes=True
    nt=w.node_tree; bg=nt.nodes['Background']
    tc=nt.nodes.new('ShaderNodeTexCoord'); sep=nt.nodes.new('ShaderNodeSeparateXYZ')
    ramp=nt.nodes.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].position=0.35; ramp.color_ramp.elements[0].color=(0.18,0.19,0.22,1)
    ramp.color_ramp.elements[1].position=0.75; ramp.color_ramp.elements[1].color=(1.0,1.0,1.0,1)
    mp=nt.nodes.new('ShaderNodeMapRange'); mp.inputs['From Min'].default_value=-1
    nt.links.new(tc.outputs['Generated'] if False else tc.outputs['Normal'],sep.inputs[0])
    nt.links.new(sep.outputs['Z'],mp.inputs['Value']); nt.links.new(mp.outputs['Result'],ramp.inputs['Fac'])
    nt.links.new(ramp.outputs['Color'],bg.inputs['Color']); bg.inputs['Strength'].default_value=0.9
    # lights
    def area(loc,size,energy,col=(1,1,1)):
        d=bpy.data.lights.new('A','AREA'); d.size=size; d.energy=energy; d.color=col
        o=bpy.data.objects.new('A',d); sc.collection.objects.link(o); o.location=loc
        o.rotation_euler=(mathutils.Vector((0,0,7))-mathutils.Vector(loc)).to_track_quat('-Z','Y').to_euler()
    area((-40,-60,70),40,90000)
    area((60,-10,40),25,30000,(0.9,0.95,1.0))
    area((0,60,30),30,25000,(1.0,0.95,0.9))
    # materials
    MATS['Ni']=mat('Ni',(0.86,0.86,0.84),1.0,0.16)
    MATS['Fe']=mat('Fe',(0.80,0.55,0.38),1.0,0.20)
    MATS['Mg']=fade(mat('Mg',(0.84,0.87,0.93),0.0,0.55))
    MATS['Os']=fade(mat('Os',(0.97,0.84,0.82),0.0,0.55))
    MATS['C']=mat('C',(0.10,0.10,0.11),0.0,0.25,0.6)
    MATS['O']=mat('O',(0.80,0.06,0.06),0.0,0.25,0.6)
    MATS['H']=mat('H',(0.96,0.96,0.96),0.0,0.25,0.6)
    for k,r in R.items():
        bpy.ops.mesh.primitive_uv_sphere_add(segments=48,ring_count=24,radius=r)
        o=bpy.context.object; bpy.ops.object.shade_smooth()
        me=o.data; me.name=k; me.materials.append(MATS[k]); MESH[k]=me
        bpy.data.objects.remove(o)
def atom(el,p,name=None):
    o=bpy.data.objects.new(name or el,MESH[el]); bpy.context.scene.collection.objects.link(o); o.location=p; return o
def camera(target=(0,-3,8.5),dist=66,elev=20,azim=-76,lens=50):
    sc=bpy.context.scene
    c=bpy.data.cameras.new('C'); c.lens=lens; o=bpy.data.objects.new('C',c); sc.collection.objects.link(o)
    t=mathutils.Vector(target); e=math.radians(elev); a=math.radians(azim)
    o.location=t+dist*mathutils.Vector((math.cos(e)*math.cos(a),math.cos(e)*math.sin(a),math.sin(e)))
    o.rotation_euler=(t-o.location).to_track_quat('-Z','Y').to_euler(); sc.camera=o
    c.dof.use_dof=False; c.dof.focus_distance=dist; c.dof.aperture_fstop=2.8
    return o
def load_static(radius=48):
    P=np.load('particle_pos.npy'); S=open('particle_sym.txt').read().split()
    for s,p in zip(S,P): atom(s,tuple(p))
    Q=np.load('support_pos.npy'); T=open('support_sym.txt').read().split()
    for s,p in zip(T,Q):
        if p[0]**2+p[1]**2<=radius**2 and p[2]>-3: atom('Mg' if s=='Mg' else 'Os',tuple(p))
    return P
