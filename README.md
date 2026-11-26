# Personal website of Dr. Zahid Iqbal

## Update from your CV (recommended)
1. In RxResume, edit your CV, then **Export, JSON**, and **Download PDF**.
2. In this repository: **Add file, Upload files**. Upload the JSON renamed to `cv.json` and the PDF renamed to `cv.pdf`. Commit.
3. The "Rebuild site" workflow reads the JSON, rebuilds the page and shows a "CV (PDF)" button. Check the Actions tab for a green tick; the site updates in 1 to 3 minutes.

What comes from the CV: profile text, links (Scholar, ORCID, GitHub, LinkedIn from the CV's Profiles section), journal papers (with JIF and quartile text and DOI links), conference papers, "Manuscripts Under Review" (arXiv items become the Preprints list), experience, education, honours, certifications, service, skills, languages and research interests.
Never published: the phone number.

## Privacy: phone number and PDF
`cv.json` and `cv.pdf` are public files. The script removes the phone number from `cv.json` automatically, but the file stays visible in GitHub's history. Best: clear the phone field in RxResume before exporting. Upload `cv.pdf` only if you are happy for its contents (including any phone number on it) to be public.

## Website-only text: `site_extras.json`
Recent highlights, collaboration countries, headings, contact line, the switch `show_under_review` (true/false), the address and the `text_replacements` list (for example `{"Reviewer of Top tier journals": "Reviewer"}` replaces wording on the site without changing your CV).

## If a run is red
Open the failed run in the Actions tab; the last lines name the problem (a bad JSON edit, or a CV missing a required section). The live site stays unchanged until a run is green.

## Wording fixes
To change how a CV phrase appears on the site without touching the CV, add it to `text_replacements` in `site_extras.json`. DOI links missing in RxResume can be added under `doi_by_title`.


**Do not edit `content.generated.json`.** It is rebuilt from `cv.json` + `site_extras.json` on every run, so hand edits are lost (the workflow now stops with a red run if you try). Change website wording in `site_extras.json` (fields such as `pub_note`, `news`, `contact_text`, or a `text_replacements` entry), or change the CV and upload a new `cv.json`.
