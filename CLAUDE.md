# homepage — simulate.dk

Shared rules for all projects: `../hub/working-style.md` (read first). Current state: `handoff.md`;
requests from other projects: `NOTES.md`.

Personal academic homepage of Thomas Bligaard, served at https://simulate.dk.

- Plain static files, no build step, no framework. One shared `style.css`.
- Pages (menu order): `index.html` (Bligaard Research Group, the front page), `publications.html`,
  `catalyst-genome.html`, `software.html`, `students.html`, `contact.html`. No CV page.
- The header is a single line: DTU logo (dtu-logo.svg, Coral Red, links to dtu.dk) + menu. No name/position line.
- The header and menu are copied into every page; when the menu changes, update
  it in all pages (mark the current page with class="active").
- Publications: newest first, each with a DOI link. Source of truth for own papers:
  ../hub/library/library.bib + ../hub/library/own-publications.tsv (keys, DOIs, order).
  Add a new paper there first, then add it here.
- Profile links: Google Scholar (user=2psbMXgAAAAJ), Web of Science (A-6161-2011). No link to DTU Orbit. No MHC series for now.
- `CNAME` tells GitHub Pages the custom domain; do not delete it.
- Keep it simple, readable, fast, accessible, mobile-friendly. No tracking cookies.
- Papers: link to accepted manuscripts / DOIs, not publishers' PDFs.

## Jens K. Nørskov publication list (TB, 2026-11-13)
- `norskov-publications.html` is deliberately NOT linked from any other page.
- Source: `_tools/norskov-publications.tsv` (section, date, doi, text); items numbered chronologically by date (generator). From Jens's list (Oct 2025), revised 2026-11-13: doublets removed, volumes corrected, published preprints dropped, Web of Science additions; DOIs checked against Crossref.
- Maintain: edit the TSV, then `python3 _tools/make_norskov.py`.
- Names are not bold on either publication page (TB, 2026-11-13).

- style.css is linked as `style.css?v=YYYYMMDD` on every page (and in _tools/make_norskov.py): when style.css changes, bump the version (date, plus a letter for a second change that day) in all of them, so browsers and the GitHub Pages cache load the new file.

## Publication figures (TB, 14 Nov 2026)
- Every item on publications.html has a figure from the paper next to it (left and right alternating),
  with a credit line under it. Thumbnails: `pubfig/<key>.jpg`; one row per item in `_tools/pubfigs.tsv`
  (credit, PDF page and region, size, optional `maxh` display height). `_tools/make_publications.py`
  builds the lists from the library and adds the figures (image URLs carry a content hash, so changed
  pictures are reloaded).
- Change or add a figure with `python3 _tools/figures/figure.py KEY ...` (crop, rotate, other page or
  region, credit; see `_tools/figures/README.md`), then run `_tools/make_publications.py` and look at the page.
- TB's taste: a figure from the paper itself (not the TOC graphic), colourful, little text, captions cut away.
- Software page: one figure per package in `swfig/` (ASE rendered with ASE; GPAW, CatMAP, Catalysis-Hub
  and CMR from their papers, each with a credit line linking the DOI).

## New publication of mine (checklist)
1. Library first, only via `hub/library/tools/libedit.py`: the entry in library.bib, and its line in
   own-publications.tsv and sources/bligaard-publications-latest.txt.
2. Its PDF in the full-text store (`hub/library/tools/fulltext.py add`), then its figure with
   `_tools/figures/figure.py KEY --page N --rect ... --credit "..."`.
3. `python3 _tools/make_publications.py`, look at the page, commit. TB pushes.

## Git
- Commit as bligaard <tbligaard@me.com> (set in this repository's .git/config, 23 Nov 2026).
- Keep `handoff.md` (current state) current and add an entry to `log.md` at the end of each work block; commit both
  with the work. These files, CLAUDE.md and NOTES.md are kept off the published site by `_config.yml`: list any new
  working file there too.
