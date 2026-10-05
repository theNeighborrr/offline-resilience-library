# Project roadmap

## v0.1 — Starter (current)

- Local start page, category filters, and catalog search.
- Four original guides and blank worksheets.
- Source catalog with candidate items clearly separated from included content.
- Repeatable build, file verification, and portable/source ZIP packaging.
- Public GitHub repository for sharing the starter with friends.

## v0.2 — First real reference pack

1. Select a Windows Kiwix reader and a small English ZIM archive. Prefer a preparedness archive as the first smoke test; confirm its current availability and terms. Add a broader Wikipedia edition after measuring storage needs.
2. Download a small set of current, authoritative preparedness PDFs with reviewed sharing terms.
3. Add an initial map region around Memphis and nearby Tennessee, Arkansas, and Mississippi. Select an offline viewer and confirm whether route calculation is supported. A map image alone does not supply offline routing.
4. Test the resulting folder with networking disconnected on the owner's PC and a second Windows PC.

## Later content categories

| Section | Intended material |
|---|---|
| Start here | How to use the drive; printable index; update date |
| Preparedness | Household plans; weather and hazard guides |
| Water & sanitation | Current drinking-water and sanitation references |
| Food & growing | Food storage, safe preservation, gardening |
| Health & first aid | Current authoritative first-aid and health references |
| Shelter & weather | Clothing, shelter, local weather hazards |
| Power & repair | Device manuals, electrical safety, repair references |
| Maps & navigation | Regional maps, map reading, tested offline viewer |
| Communications | Contact plans, radio manuals, locally verified information |
| Reference & learning | Encyclopedia, math, science, practical skills |
| Household records | Blank forms; completed private copies stored separately |
| Readers & tools | Tested software, install/recovery instructions |

## Acceptance checklist for a usable reference pack

- Extract to a fresh folder; all included links resolve.
- Disconnect networking. Open the start page, each file type, reader, and archive.
- Search a known article inside Kiwix; search the homepage catalog separately.
- Open each map at useful zoom levels; test any promised routing offline.
- Copy to USB, safely eject, reconnect, and repeat on a second PC.
- Compare SHA-256 values after copying.
- Print the start instructions and household sheets in black and white.
- Check dates, editions, retained attribution, and reader compatibility.
- Record exact tested Windows/browser versions and results; do not label unperformed checks as passed.

## Initial validation limitations

Third-party downloads, visual browser/print checks, and actual Wi-Fi-off testing remain pending. No complete encyclopedia, map pack, medical guide, or executable is claimed as installed.

Automated validation completed on 2026-10-05: build and manifest verification; nine Python tests covering copied archives, excluded private files, corrupted files, unsafe paths, catalog state, third-party checksum requirements, missing links, remote dependencies, stale templates, and release overwrite protection; JavaScript checks for search, availability/category filters, combined terms, empty results, and reset. These checks do not substitute for browser rendering or a physical USB test.
