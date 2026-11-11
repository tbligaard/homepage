# homepage — simulate.dk

Personal academic homepage of Thomas Bligaard, served at https://simulate.dk.

- Plain static files, no build step, no framework. One shared `style.css`.
- Pages (menu order): `index.html` (Bligaard Research Group, the front page), `publications.html`,
  `catalyst-genome.html`, `software.html`, `students.html`, `contact.html`. No CV page.
- The header is a single line: DTU logo (dtu-logo.svg, Coral Red, links to dtu.dk) + menu. No name/position line.
- The header and menu are copied into every page; when the menu changes, update
  it in all pages (mark the current page with class="active").
- Publications: newest first, each with a DOI link.
- Profile links: Google Scholar (user=2psbMXgAAAAJ), Web of Science (A-6161-2011). No link to DTU Orbit. No MHC series for now.
- `CNAME` tells GitHub Pages the custom domain; do not delete it.
- Keep it simple, readable, fast, accessible, mobile-friendly. No tracking cookies.
- Papers: link to accepted manuscripts / DOIs, not publishers' PDFs.
