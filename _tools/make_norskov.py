#!/usr/bin/env python3
"""Build norskov-publications.html (Jens K. Nørskov's publication list) from
_tools/norskov-publications.tsv: section, date, doi, text (one line per item).

Items are numbered chronologically within each section (1 = oldest) by the
publication date (YYYY, YYYY-MM or YYYY-MM-DD, from Crossref's 'issued' date where
there is a DOI); items with the same date keep their order in the file. The page
lists the newest first.

Maintain the list by adding a line to the TSV (section, date, DOI, text) and run:
    python3 _tools/make_norskov.py
The page is deliberately not linked from the other pages (TB, 2026-11-13).
Source: Jens's own list (October 2025), revised 2026-11-13 (doublets removed,
volumes corrected, Web of Science additions); DOIs checked against Crossref.
"""
import csv, html, os, re
HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.dirname(HERE)
TSV = os.path.join(HERE, 'norskov-publications.tsv')
OUT = os.path.join(SITE, 'norskov-publications.html')
SECTIONS = [('Papers', 'papers', 'Papers'), ('Books, Lecture Notes', 'books', 'Books and book chapters'),
            ('Other Publications', 'other', 'Other publications'),
            ('To be verified', 'to-be-verified', 'To be verified')]   # provisional (TB, 2026-11-13)

rows = list(csv.DictReader(open(TSV, encoding='utf-8'), delimiter='\t', quoting=csv.QUOTE_NONE))

def sortkey(d):
    p = (d.split('-') + ['06', '15'])[:3] if len(d) == 4 else (d.split('-') + ['15'])[:3]
    return tuple(int(x) for x in p)

def fmt(n, r):
    t = html.escape(r['text'], quote=False)
    t = re.sub(r'(\d)-(\d)', '\\1–\\2', t)
    t = re.sub(r'ISBN:?[^)]*', lambda m: m.group(0).replace('–', '-'), t)   # ISBNs keep hyphens
    if r['doi']:
        d = html.escape(r['doi'])
        t += f' <a class="doi" href="https://doi.org/{d}">doi:{d}</a>'
    return f'  <li value="{n}">{t}</li>'

body, nav = [], []
for name, sid, title in SECTIONS:
    items = [r for r in rows if r['section'] == name]
    items = sorted(items, key=lambda r: sortkey(r['date']))          # stable: file order breaks ties
    if not items: continue
    nav.append(f'<a href="#{sid}">{title}</a>')
    body.append(f'<h2 id="{sid}">{title}</h2>\n<ol class="pubs" reversed>')
    body += [fmt(i + 1, r) for i, r in reversed(list(enumerate(items)))]
    body.append('</ol>')

page = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="format-detection" content="telephone=no">
<title>Publications · Jens K. Nørskov</title>
<meta name="description" content="Publication list of Jens K. Nørskov, with DOI links to the journal pages.">
<link rel="stylesheet" href="style.css">
</head>
<body>
<header class="site-header">
  <div class="wrap header-row">
    <a href="https://www.dtu.dk" class="logo"><img src="dtu-logo.svg" alt="DTU – Technical University of Denmark"></a>
  </div>
</header>
<main class="wrap">
<h1>Jens K. Nørskov · Publications</h1>
<p class="pubs-nav">{' · '.join(nav)}</p>
{chr(10).join(body)}
</main>
<footer class="wrap">
  <p>Jens K. Nørskov · <a href="https://physics.dtu.dk">DTU Physics</a> · Technical University of Denmark</p>
</footer>
</body>
</html>
'''
open(OUT, 'w', encoding='utf-8').write(page)
print('wrote', OUT, len(rows), 'items,', sum(1 for r in rows if r['doi']), 'with DOI')
