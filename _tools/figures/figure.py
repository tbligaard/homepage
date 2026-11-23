#!/usr/bin/env python3
"""Redo the figure (thumbnail) of one publication on publications.html.

    python3 _tools/figures/figure.py KEY [options]        (run from the homepage folder)

The thumbnail pubfig/KEY.jpg is cut from the paper's PDF in the full-text store
(iCloud Literature_cl/KEY.pdf; set LITERATURE_CL to override) using
  - the page and region in _tools/pubfigs.tsv (columns pdf_page, rect_pt: PDF points x0,y0,x1,y1), and
  - the after-steps in _tools/figures/figures.json (crop, rot, trim, box, source, image).
Options change those settings and save them, so the next run gives the same figure:
  --page N              PDF page (1-based)
  --rect x0,y0,x1,y1    region on that page in PDF points (72 per inch; 'page' = whole page)
  --crop a,b,c,d        then keep this fraction of the region (left, top, right, bottom; 0..1)
  --rot DEG             then rotate anticlockwise by DEG (90 or -90 for a quarter turn)
  --trim T              white-margin threshold (default 12; higher trims light-grey margins too)
  --box W,H             largest thumbnail size in pixels (default 360,260)
  --image FILE          use this image instead of a PDF (cover, logo); path relative to this folder
  --credit TEXT         credit line shown under the figure (e.g. "© Wiley", "© the authors, CC BY 4.0")
  --show                print the current settings and stop
Afterwards: python3 _tools/make_publications.py, look at the page, commit.
Needs Pillow and pdftoppm (poppler); PyMuPDF is used instead of pdftoppm if installed.
"""
import argparse, csv, json, os, subprocess, sys, tempfile
from PIL import Image, ImageChops

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
TSV = os.path.join(ROOT, '_tools', 'pubfigs.tsv')
SET = os.path.join(HERE, 'figures.json')
STORES = [os.environ.get('LITERATURE_CL', ''),
          os.path.expanduser('~/Library/Mobile Documents/com~apple~CloudDocs/Literature_cl'),
          os.path.expanduser('~/mnt/com~apple~CloudDocs--Literature_cl')]
DPI = 200

def pdf_path(key):
    for s in STORES:
        p = os.path.join(s, key + '.pdf')
        if s and os.path.exists(p): return p
    sys.exit(f'{key}.pdf not found in the full-text store; set LITERATURE_CL or connect iCloud Literature_cl')

def render(pdf, page, rect):
    try:
        import fitz
        pg = fitz.open(pdf)[page - 1]
        clip = pg.rect if rect is None else fitz.Rect(rect) & pg.rect
        pix = pg.get_pixmap(clip=clip, dpi=DPI)
        return Image.frombytes('RGB', (pix.w, pix.h), pix.samples) if pix.n == 3 else Image.frombytes('RGBA', (pix.w, pix.h), pix.samples).convert('RGB')
    except ImportError:
        pass
    with tempfile.TemporaryDirectory() as d:
        cmd = ['pdftoppm', '-f', str(page), '-l', str(page), '-r', str(DPI), '-png', '-singlefile']
        if rect is not None:
            s = DPI / 72; x0, y0, x1, y1 = rect
            cmd += ['-x', str(int(x0 * s)), '-y', str(int(y0 * s)), '-W', str(int((x1 - x0) * s)), '-H', str(int((y1 - y0) * s))]
        subprocess.run(cmd + [pdf, os.path.join(d, 'p')], check=True)
        return Image.open(os.path.join(d, 'p.png')).convert('RGB')

def main():
    a = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    a.add_argument('key'); a.add_argument('--page', type=int); a.add_argument('--rect'); a.add_argument('--crop')
    a.add_argument('--rot', type=float); a.add_argument('--trim', type=int); a.add_argument('--box'); a.add_argument('--image')
    a.add_argument('--credit'); a.add_argument('--show', action='store_true')
    o = a.parse_args(); k = o.key
    rows = list(csv.DictReader(open(TSV, encoding='utf-8'), delimiter='\t')); fields = list(rows[0].keys())
    row = next((r for r in rows if r['key'] == k), None)
    if row is None:
        row = {f: '' for f in fields}; row.update(key=k, kind='figure'); rows.append(row)
        print(f'{k}: new row in pubfigs.tsv; set section and number there (as in own-publications.tsv) and a --credit')
    S = json.load(open(SET, encoding='utf-8')); s = S.get(k, {})
    if o.show: print(json.dumps({'row': row, 'settings': s}, ensure_ascii=False, indent=1)); return
    if o.page: row['pdf_page'] = str(o.page)
    if o.rect: row['rect_pt'] = '' if o.rect == 'page' else o.rect
    if o.crop: s['crop'] = [float(x) for x in o.crop.split(',')]
    if o.rot is not None: s['rot'] = o.rot
    if o.trim is not None: s['trim'] = o.trim
    if o.box: s['box'] = [int(x) for x in o.box.split(',')]
    if o.image: s['image'] = o.image
    if o.credit: row['credit'] = o.credit
    if s.get('image'):
        im = Image.open(os.path.join(HERE, s['image'])); row['kind'] = row['kind'] or 'image'
        if im.mode in ('RGBA', 'LA', 'P'):
            im = im.convert('RGBA'); bg = Image.new('RGBA', im.size, (255, 255, 255, 255)); bg.alpha_composite(im); im = bg
        im = im.convert('RGB')
    else:
        if not row.get('pdf_page'): sys.exit(f'{k}: give --page (and --rect) the first time')
        rect = [float(x) for x in row['rect_pt'].split(',')] if row.get('rect_pt') else None
        im = render(pdf_path(s.get('source', k)), int(row['pdf_page']), rect)
    if 'crop' in s:
        x0, y0, x1, y1 = s['crop']; W, H = im.size; im = im.crop((int(x0 * W), int(y0 * H), int(x1 * W), int(y1 * H)))
    if s.get('rot'): im = im.rotate(s['rot'], expand=True, fillcolor='white')
    t = s.get('trim', 12)
    bb = ImageChops.difference(im, Image.new('RGB', im.size, 'white')).convert('L').point(lambda v: 255 if v > t else 0).getbbox()
    if bb: im = im.crop((max(0, bb[0] - 6), max(0, bb[1] - 6), min(im.width, bb[2] + 6), min(im.height, bb[3] + 6)))
    im.thumbnail(tuple(s.get('box', (360, 260))), Image.LANCZOS)
    im.save(os.path.join(ROOT, 'pubfig', k + '.jpg'), quality=85 if 'box' in s else 82, optimize=True)
    row['size'] = f'{im.width}x{im.height}'
    if s: S[k] = s
    json.dump(dict(sorted(S.items())), open(SET, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
    with open(TSV, 'w', encoding='utf-8', newline='') as f:
        f.write('\t'.join(fields) + '\n')
        for r in rows: f.write('\t'.join(r.get(c, '') or '' for c in fields) + '\n')
    print(f'pubfig/{k}.jpg {im.width}x{im.height}; now run python3 _tools/make_publications.py')

if __name__ == '__main__': main()
