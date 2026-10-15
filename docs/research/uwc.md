# University of the Western Cape (UWC): programme list, research note

Read on Thu 15 Oct 2026 (SAST) by a research agent. **Result: nothing added.** `uwc.yaml` still has `programmes: []`,
because none of UWC's own documents could be read without going around a block.

## What happened

| Host | robots.txt | Verdict |
|---|---|---|
| `www.uwc.ac.za` | **403 Forbidden**, twice, with a "This domain is temporarily unavailable" page (curl's own user agent; the page's `Last-Modified` is 16 Sep 2026) | not fetched: every UWC admission page and PDF found lives here |
| `uwc.ac.za` | 301 to `www.uwc.ac.za/robots.txt` | same as above |
| `prospectus.uwc.ac.za` | the name doesn't resolve (no DNS record from our resolver or from 8.8.8.8) | gone; search engines still list old pages from it |
| `student.uwc.ac.za` | 404 (no robots.txt) | the application portal: no programme requirements there, not used |

UWC applies directly, not through the CAO, so the CAO has no UWC requirements to read.

Search engines (UWC's domain only) listed the documents below. Their summaries were **not** used for any figure: they
are a model's paraphrase of a blocked host, and copying them would be working around the block.

## What a person should download in a browser

1. **General Admissions Criteria for 2027** (UWC's eight-panel admissions leaflet), the main source:
   https://www.uwc.ac.za/files/files/SEMU-8-Panel-Print-Admissions-2027.pdf
2. **The undergraduate admission requirements page:**
   https://www.uwc.ac.za/admission-and-financial-aid/undergraduate-admission/undergraduate-admission-requirements
3. **Each faculty's 2027 brochure, if published** (2026 ones exist at the same path, for example
   https://www.uwc.ac.za/files/files/UWC-Faculty-of-Education-2026-1-1.pdf and
   https://www.uwc.ac.za/files/files/UWC-Faculty-of-Community-and-Health-Sciences-2026.pdf). Look for the 2027 versions
   of all seven faculties: Arts and Humanities, Community and Health Sciences, Dentistry, Economic and Management
   Sciences, Education, Law, Natural Sciences.
4. **Faculty admission pages:**
   - https://www.uwc.ac.za/study/faculties-and-programmes/faculty-of-natural-sciences/student-admission
   - https://www.uwc.ac.za/study/faculties-and-programmes/faculty-of-economic-and-management-sciences/undergraduate-application-process
   - https://www.uwc.ac.za/study/faculties-and-programmes/faculty-of-education/admission-information
   - https://www.uwc.ac.za/study/faculties-and-programmes/faculty-of-arts-and-humanities/programmes

Saved into the scratch folder, these PDFs can be read with the brief's `pdf_text.py` and the programmes added then.

## Check first

- **The pack's existing sources come from the same host.** `s-uwc-aps` (the points table) and `s-uwc-apply` (the
  2027 window) were read from `www.uwc.ac.za` on 13 Oct 2026, and that host refuses robots.txt today. A person should
  confirm both against UWC's pages in a browser, and check whether the 2027 leaflet (item 1) states the points table
  the same way.
