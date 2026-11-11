# Front-page animation: CO + 3H2 -> CH4 + H2O on Ni3Fe/MgO

Illustration (choreographed, not simulated). Rendered with Blender (Cycles) via `pip install bpy ase`.

1. `python build.py` — Ni3Fe (L1_2) Winterbottom particle (541 atoms) on MgO(100).
2. `python choreo.py` — adsorbate trajectories, 21 s loop at 30 fps -> traj.npz.
3. `python render.py plate 128` — static particle + support, rendered once.
4. `python render.py frames 20 0 630` — adsorbates only (static atoms as holdouts), one PNG per frame.
5. Composite with ffmpeg:
   `ffmpeg -framerate 30 -i plate_bg.png -framerate 30 -i frames/h_%04d.png -filter_complex "[0:v]loop=-1:1,trim=end_frame=630,setpts=N/30/TB[bg];[bg][1:v]overlay=shortest=1,format=yuv420p" -r 30 -c:v libx264 -crf 22 -preset slow -movflags +faststart nanoparticle.mp4`
   (plate_bg.png = plate.png flattened onto #fdfdfc, the page background.)
