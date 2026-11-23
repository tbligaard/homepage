# Publication figures

`figure.py` redoes one thumbnail in `pubfig/` (see its header for the options). Settings:

- `_tools/pubfigs.tsv`: one row per publication: key, section, number, credit line, kind, PDF page,
  region (PDF points), thumbnail size, optional `maxh` (display height in px, default 200).
- `figures.json`: after-steps per key: `crop` (fractions), `rot` (degrees, anticlockwise), `trim`
  (white-margin threshold), `box` (max thumbnail size), `source` (take the figure from another key's
  PDF, e.g. a correction from its paper), `image` (a cover or logo in `images/` instead of a PDF).

The figures were picked in Nov 2026 as the most colourful sizeable figure of each paper, checked by
hand, then cropped and rotated as TB asked (14 Nov). Credits: "© publisher" from Crossref, or
"© the authors, CC BY x.y" for open-access papers. The DOE seal (PruskiEtAl2016) is public domain.
