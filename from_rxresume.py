#!/usr/bin/env python3
"""cv.json (RxResume export) + site_extras.json  ->  content.generated.json
Reads the CV sections; website-only items (news, links, collaboration, wording switches) come from site_extras.json.
Never reads the phone number. Fails loudly (non-zero exit) if the CV is missing key sections, so a bad upload never breaks the live site."""
import json, re, sys, pathlib
H = pathlib.Path(__file__).resolve().parent
cv = json.loads((H / "cv.json").read_text(encoding="utf8"))
ex = json.loads((H / "site_extras.json").read_text(encoding="utf8"))
if cv["basics"].get("phone") or cv["basics"].get("customFields"):   # cv.json is public on GitHub Pages: never keep the phone number in it
    cv["basics"]["phone"] = ""; cv["basics"]["customFields"] = []
    (H / "cv.json").write_text(json.dumps(cv, indent=1, ensure_ascii=False), encoding="utf8")
    print("Phone number removed from cv.json (the file is public).")
sec = cv["sections"]
txt = lambda s: re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", s or "")).strip()
def items(name):
    s = sec.get(name, {})
    return [] if s.get("hidden") else [i for i in s.get("items", []) if not i.get("hidden")]
def custom(title):
    for c in cv.get("customSections", []):
        if c["title"].strip().lower() == title.lower() and not c.get("hidden"):
            return [i for i in c.get("items", []) if not i.get("hidden")]
    return []
def bullets(html):
    b = [txt(x) for x in re.findall(r"<li>(.*?)</li>", html or "", re.S)]
    return b or ([txt(html)] if txt(html) else [])
def period(i): return i.get("period") or (i.get("dates") or {}).get("raw") or ""
url = lambda i: (i.get("website") or {}).get("url", "") if str((i.get("website") or {}).get("url", "")).startswith("http") else ""
rep = ex.get("text_replacements", {})
doi_map = ex.get("doi_by_title", {})
def fix(s):
    for a, b in rep.items(): s = s.replace(a, b)
    return s

BADGE = re.compile(r"(JIF\s*[\d.]+\s*[,·]?\s*Q\d|Scopus\s*Q\d)", re.I)
def pub(i):
    p = i.get("publisher", ""); m = BADGE.search(p)
    badge = re.sub(r"(JIF\s*[\d.]+)\s*[,·]?\s*(Q\d)", r"\1 · \2", m.group(1), flags=re.I) if m else ""
    acc = bool(re.search(r"\(accepted\)", p, re.I))
    v = BADGE.sub("", re.sub(r"\(accepted\)", "", p, flags=re.I)).strip(" ·.,;")
    v = re.sub(r"\s*·\s*", " ", v); v = re.sub(r",\s+(?=\d|e\d)", " ", v, count=1)
    return dict(title=txt(i["title"]), venue=v + (" (accepted)" if acc else ""), year=str(i.get("date") or (i.get("dates") or {}).get("start") or ""), badge=badge, doi=url(i) or doi_map.get(txt(i["title"]), ""))

journals = [pub(i) for i in items("publications")]
conferences = [dict(title=txt(i["company"]), venue=txt(i["position"]), year=period(i), badge="", doi=url(i) or doi_map.get(txt(i["company"]), "")) for i in custom("Conference Publications")]
preprints, under = [], []
for i in custom("Manuscripts Under Review"):
    t, v = txt(i["company"]), txt(i["position"]); m = re.search(r"\d{4}\.\d{4,5}", v)
    if "arxiv" in v.lower() and m: preprints.append(dict(title=t, venue="arXiv:" + m.group(0), year="2026", badge="", doi="https://arxiv.org/abs/" + m.group(0)))
    else: under.append(dict(title=t, venue=v))
def role(i, org, rl, place=""): return dict(org=txt(i[org]), place=txt(i.get(place, "")) if place else "", role=rl, period=period(i), bullets=bullets(i.get("description")))
experience = [role(i, "company", txt(i["position"]), "location") for i in items("experience")]
education = [role(i, "school", txt(i["degree"]) + (", " + txt(i["area"]) if txt(i.get("area")) else "")) for i in items("education")]
awards = [", ".join(x for x in (txt(i["title"]), txt(i.get("awarder"))) if x) + (f" ({txt(i['date'])})" if txt(i.get("date")) else "") for i in items("awards")]
certs = [", ".join(x for x in (txt(i["title"]), txt(i.get("issuer"))) if x) + (f" ({txt(i['date'])})" if txt(i.get("date")) else "") + (", " + txt(i["description"]) if txt(i.get("description")) else "") for i in items("certifications")]
service = [txt(i["organization"]) + (", " + txt(i["description"]) if txt(i.get("description")) else "") + (f" ({period(i)})" if period(i) else "") for i in items("volunteer") if txt(i.get("organization"))]
skills = [[txt(i["name"]), ", ".join(i.get("keywords", []))] for i in items("skills")]
langs = [[txt(i["language"]), txt(i.get("fluency"))] for i in items("languages")]
ri = custom("Research Interests")
interests = [x.strip() for x in txt(ri[0].get("description")).split("·") if x.strip()] if ri else []

out = json.loads(json.dumps(ex))                      # start from the website-only extras
out.pop("text_replacements", None); out.pop("doi_by_title", None)
out.setdefault("site", {}); out["site"].setdefault("name", cv["basics"]["name"])
out["site"].setdefault("emails", [cv["basics"]["email"]])
out.setdefault("links", {})
for p in items("profiles"):
    key = {"google scholar": "scholar", "orcid": "orcid", "github": "github", "linkedin": "linkedin"}.get(p["network"].strip().lower())
    if key and url(p) and not out["links"].get(key): out["links"][key] = url(p)
for k in ("scholar", "orcid", "github", "linkedin"): out["links"].setdefault(k, "")
if not out.get("lead"): out["lead"] = txt(cv["summary"]["content"])
if interests and not out.get("interests"): out["interests"] = interests
out.update(journals=journals, preprints=preprints, conferences=conferences, under_review=under, experience=experience,
           education=education, awards=awards, certifications=certs, service=service, skills=skills, languages=langs)

def apply(o):
    if isinstance(o, str): return fix(o)
    if isinstance(o, list): return [apply(x) for x in o]
    if isinstance(o, dict): return {k: apply(v) for k, v in o.items()}
    return o
out = apply(out)
bad = [k for k in ("journals", "experience", "education", "lead") if not out.get(k)]
if bad: sys.exit(f"ERROR: CV export has no usable: {bad}. Site left unchanged.")
for p in journals + conferences:
    if not p["title"] or not p["year"]: sys.exit(f"ERROR: publication without title or year: {p}")
out = {"_DO_NOT_EDIT": "Generated from cv.json + site_extras.json on every rebuild. Edit site_extras.json or the CV instead.", **out}
(H / "content.generated.json").write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf8")
print(f"CV read: {len(journals)} journals, {len(preprints)} preprints, {len(conferences)} conference, {len(under)} under review, "
      f"{len(experience)} roles, {len(education)} degrees, {len(awards)} awards, {len(certs)} certifications, {len(service)} service, {len(skills)} skills")
print("Not read on purpose: phone number. Sections ignored:", [s for s in sec if s not in ("profiles","experience","education","skills","languages","awards","certifications","publications","volunteer") and sec[s].get("items")])
