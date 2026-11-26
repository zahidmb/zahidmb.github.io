#!/usr/bin/env python3
"""Builds index.html from content.json. Run:  python3 build.py   (needs only Python 3, no packages).
Edit content.json (text, papers, links); never edit index.html by hand."""
import json, html, pathlib, datetime
H = pathlib.Path(__file__).resolve().parent
src = H / "content.generated.json" if (H / "cv.json").exists() and (H / "content.generated.json").exists() else H / "content.json"
c = json.loads(src.read_text(encoding="utf8"))
s = c["site"]
if not s.get("cv_pdf"):   # a PDF in the repo root becomes the "CV (PDF)" button: cv.pdf, or the only .pdf there
    pdfs = [p.name for p in H.glob("*.pdf")]
    s["cv_pdf"] = "cv.pdf" if "cv.pdf" in pdfs else (pdfs[0] if len(pdfs) == 1 else "")
E = lambda x: html.escape(x or "", quote=True)

def a(url, text): return f'<a href="{E(url)}" rel="noopener">{text}</a>' if url else text
def pub(p, badge=True):
    b = f' <span class="badge">{E(p["badge"])}</span>' if badge and p.get("badge") else ""
    return f'<li><span class="yr">{E(p["year"])}</span><div>{a(p.get("doi"), E(p["title"]))}<br><span class="venue">{E(p["venue"])}</span>{b}</div></li>'
def role(r):
    ul = "<ul>" + "".join(f"<li>{E(b)}</li>" for b in r["bullets"]) + "</ul>" if r["bullets"] else ""
    pl = f", {E(r['place'])}" if r.get("place") else ""
    return f'<article class="role"><div class="when">{E(r["period"])}</div><div><h3>{E(r["role"])}</h3><p class="org">{E(r["org"])}{pl}</p>{ul}</div></article>'
def ul(items, cls="plain"): return f'<ul class="{cls}">' + "".join(f"<li>{E(i)}</li>" for i in items) + "</ul>"

names = {"scholar": "Google Scholar", "orcid": "ORCID", "github": "GitHub", "linkedin": "LinkedIn"}
btns = [("Email", "mailto:" + s["emails"][0])] + [(names[k], v) for k, v in c["links"].items() if v] + ([("CV (PDF)", s["cv_pdf"])] if s.get("cv_pdf") else [])
btns = "".join(f'<a class="btn{" primary" if i == 0 else ""}" href="{E(u)}" rel="noopener">{E(l)}</a>' for i, (l, u) in enumerate(btns))
photo = f'<img class="photo" src="{E(s["photo"])}" alt="Portrait of {E(s["name"])}" width="168" height="168">' if s.get("photo") else '<div class="photo initials" aria-hidden="true">ZI</div>'
ur = ""
if s.get("show_under_review") and c["under_review"]:
    ur = '<h3 class="sub">Manuscripts under review</h3><ul class="list">' + "".join(
        f'<li><span class="yr"></span><div>{E(p["title"])}<br><span class="venue">{E(p["venue"])}</span></div></li>' for p in c["under_review"]) + "</ul>"
ld = {"@context": "https://schema.org", "@type": "Person", "name": s["name"], "jobTitle": s["title"], "url": s["site_url"],
      "affiliation": {"@type": "CollegeOrUniversity", "name": "University of Gujrat"},
      "alumniOf": {"@type": "CollegeOrUniversity", "name": "Universiti Sains Malaysia"},
      "sameAs": [v for v in c["links"].values() if v], "knowsAbout": c["interests"]}
emails = "".join(f'<a class="btn{" primary" if i == 0 else ""}" href="mailto:{E(m)}">{E(m)}</a>' for i, m in enumerate(s["emails"]))

page = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{E(s["name"])} | {E(s["tagline_short"])}</title>
<meta name="description" content="{E(s["description"])}">
<meta property="og:title" content="{E(s["name"])}"><meta property="og:description" content="{E(s["description"])}"><meta property="og:type" content="profile"><meta property="og:url" content="{E(s["site_url"])}">
<link rel="canonical" href="{E(s["site_url"])}"><link rel="stylesheet" href="style.css">
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script></head><body>
<header class="top"><nav aria-label="Sections"><a class="brand" href="#top">Z. Iqbal</a><a href="#research">Research</a><a href="#publications">Publications</a><a href="#experience">Experience</a><a href="#collaboration">Collaboration</a><a href="#contact">Contact</a></nav></header>
<main id="top">
<section class="hero">{photo}<div><h1>{E(s["name"])}</h1><p class="role-line">{E(s["title"])}<br>{E(s["affiliation"])}</p><p class="lead">{E(c["lead"])}</p><p class="actions">{btns}</p></div></section>
<section id="research"><h2 class="small">{E(c.get("research_heading","Research interests"))}</h2>{f'<p>{E(c["about"])}</p>' if c.get("about") else ""}<ul class="chips">{"".join(f"<li>{E(x)}</li>" for x in c["interests"])}</ul></section>
<section id="news"><h2>Recent highlights</h2><ul class="list">{"".join(f'<li><span class="yr">{E(d)}</span><div>{t}</div></li>' for d, t in c["news"])}</ul></section>
<section id="publications"><h2>Publications</h2><p class="note">{E(c["pub_note"])}</p>
<h3 class="sub">Journal articles</h3><ul class="list">{"".join(pub(p) for p in c["journals"])}</ul>
<h3 class="sub">Preprints (arXiv)</h3><ul class="list">{"".join(pub(p, False) for p in c["preprints"])}</ul>
<h3 class="sub">Conference papers</h3><ul class="list">{"".join(pub(p, False) for p in c["conferences"])}</ul>{ur}</section>
<section id="experience"><h2>Experience</h2>{"".join(role(r) for r in c["experience"])}<h2 class="mt">Education</h2>{"".join(role(r) for r in c["education"])}</section>
<section id="collaboration"><h2>International collaboration</h2><p>{E(c["collaboration_text"])}</p><ul class="collab">{"".join(f"<li><b>{E(x)}</b><span>{E(y)}</span></li>" for x, y in c["collaboration"])}</ul></section>
<section id="service"><h2>Honours, service and skills</h2><div class="two"><div><h3 class="sub">Honours and awards</h3>{ul(c["awards"])}<h3 class="sub">Certifications</h3>{ul(c["certifications"])}</div>
<div><h3 class="sub">Professional service</h3>{ul(c["service"])}<h3 class="sub">Skills</h3>{ul([f"{k}: {v}" for k, v in c["skills"]])}<h3 class="sub">Languages</h3>{ul([f"{k} ({v})" for k, v in c["languages"]])}</div></div></section>
<section id="contact"><h2>Contact</h2><p>{E(c["contact_text"])}</p><p class="actions">{emails}</p><p class="addr">{E(s["address"])}</p></section>
</main><footer><p>© {datetime.date.today().year} {E(s["name"])}. Last updated {datetime.date.today():%d %B %Y}.</p></footer></body></html>"""

(H / "index.html").write_text(page, encoding="utf8")
(H / ".nojekyll").write_text("")
(H / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {s['site_url']}sitemap.xml\n")
(H / "sitemap.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>{s["site_url"]}</loc></url></urlset>')
print("built index.html:", len(c["journals"]), "journals,", len(c["preprints"]), "preprints,", len(c["conferences"]), "conference,", len(c["under_review"]), "under review")
