# Company documents

PDFs and extracted text used for the company-facts dataset.

```
data/company_docs/
├── GENTING_IAR2024.pdf / .txt / .pages.json / .index.json   FY2024 annual report
├── GENTING_IAR2025.pdf / .txt / ...                         FY2025 annual report
├── GENM_IAR2024.pdf / .txt / ...                            FY2024 annual report
├── GENM_IAR2025.pdf / .txt / ...                            FY2025 annual report
├── annual_facts.md                                          structured summary + page refs
├── pdf_manifest.json                                        URL → local file manifest
├── quarterly/
│   ├── GENTING/   8 quarterly reports + 8 press releases (PDF + TXT)
│   ├── GENM/      8 quarterly reports + 8 press releases (PDF + TXT)
│   └── manifest.csv  period → report / press-release / announcement URL
└── announcements/ 83 announcement / annual-report PDFs + TXT from Bursa
```

Text extraction: `python3 scripts/extract_company_docs.py` (pypdf). Each `.txt` is
page-delimited with `=== PAGE n ===`; `.pages.json` stores the character offset of each
page; `.index.json` lists pages where key statement headings occur.

Other files in this directory (`annual/`, `GENT_AR2025_Part*.pdf`,
`GENT_GENT Corporate Governance Report 2025.pdf`, etc.) belong to a parallel
annual-report archive and are not part of this dataset's four authoritative annual
reports.
