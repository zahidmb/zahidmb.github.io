# Personal website of Dr. Zahid Iqbal
All text lives in `content.json`. `index.html` is generated; do not edit it by hand.

## Update later (no tools needed)
1. On GitHub open `content.json`, click the pencil, change the text, commit.
2. The workflow in `.github/workflows/build.yml` rebuilds `index.html`; the site updates in about a minute.

## Add links or a photo
- In `content.json`: `links` (scholar, orcid, github, linkedin), `site.photo` (e.g. `"photo.jpg"`, upload the file), `site.cv_pdf` (e.g. `"cv.pdf"`, upload the file).
- Hide the "under review" list: set `site.show_under_review` to `false`.

## Update locally
`python3 build.py`, then open `index.html`.
