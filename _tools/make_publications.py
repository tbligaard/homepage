#!/usr/bin/env python3
"""Rebuild the publication lists in publications.html from Thomas's own list.

Inputs (read only):
  ../hub/library/sources/bligaard-publications-latest.txt   own list (plain text from the Word file)
  ../hub/library/own-publications.tsv                        section, number, key, DOI
Only the <ol> lists of the sections below are replaced; everything else on the
page (header, textbook box, Preprints section, menu) is left as it is.
Run from the homepage folder:  python3 _tools/make_publications.py
"""
import csv, html, re, os
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
LIB = os.path.join(ROOT, '..', 'hub', 'library')
SRC = os.path.join(LIB, 'sources', 'bligaard-publications-latest.txt')
TSV = os.path.join(LIB, 'own-publications.tsv')
PAGE = os.path.join(ROOT, 'publications.html')
SECTIONS = {'Papers': 'papers', 'Patents': 'patents', 'Books': 'books', 'Book Chapters': 'book-chapters',
            'Academic Dissertations': 'academic-dissertations', 'Popular Scientific Publications': 'popular-science'}

items, sec = {}, None
for line in open(SRC, encoding='utf-8').read().splitlines():
    line = line.strip()
    if line in SECTIONS: sec = SECTIONS[line]; items[sec] = []; continue
    m = re.match(r'^(\d+)\.\s+(.*)$', line)
    if m and sec: items[sec].append([int(m.group(1)), m.group(2)])
    elif line and sec and items[sec]: items[sec][-1][1] += ' ' + line

doi = {}
for r in csv.DictReader(open(TSV, encoding='utf-8'), delimiter='\t'):
    for name, sid in SECTIONS.items():
        if r['section'] == name and r['doi']: doi[(sid, int(r['number']))] = r['doi']

def fmt(text):
    t = html.escape(text, quote=False)
    t = re.sub(r'T\.\s?Bligaard', '<strong>T. Bligaard</strong>', t)
    t = re.sub(r'(\d)-(\d)', '\\1–\\2', t)          # page ranges with en dash
    return t

page = open(PAGE, encoding='utf-8').read()
for sid, lst in items.items():
    lst.sort(key=lambda x: -x[0])
    lis = []
    for n, text in lst:
        li = fmt(text)
        d = doi.get((sid, n))
        if d: li += f' <a class="doi" href="https://doi.org/{d}">doi:{d}</a>'
        lis.append(f'  <li>{li}</li>\n')
    new = f'<h2 id="{sid}">\\1</h2>\n<ol class="pubs" reversed start="{lst[0][0]}">\n' + ''.join(lis).replace('\\', '\\\\') + '</ol>'
    page, k = re.subn(rf'<h2 id="{sid}">(.*?)</h2>\n<ol class="pubs" reversed start="\d+">\n.*?</ol>', new, page, flags=re.S)
    print(f'{sid}: {len(lst)} items, {sum((sid, n) in doi for n, _ in lst)} with DOI', '' if k else '(SECTION NOT FOUND)')
open(PAGE, 'w', encoding='utf-8').write(page)
