# Offline Resilience Library

A personal, portable reference collection to share with friends. The first target is a Windows PC and a USB drive. No accounts, paid services, or internet connection are needed to read the included pages.

## Use the starter

Download this repository using **Code → Download ZIP**, or use a packaged portable ZIP.

1. Extract the entire ZIP into a folder (do not open pages from inside the ZIP).
2. Double-click **START-HERE.html**.
3. Open an included guide or worksheet. Use Ctrl+P to print.
4. Copy the entire extracted folder to a USB drive and repeat with Wi-Fi disconnected.

This is **v0.1, a functional starter**, not a complete emergency reference collection. It includes four original pages: setup instructions, a household contact worksheet, an inventory worksheet, and a communications worksheet. Wikipedia, maps, medical manuals, repair guides, and readers are **not included**. Their cards are a research queue, not offline downloads. Search covers catalog titles, descriptions, and keywords, not the full text of future archives.

## Project files

- `catalog.json`: source records, topic order, rights-review notes, reader requirements, and local paths.
- `content/guides/`: original printable pages.
- `assets/`: local styles and search/filter code; no remote dependencies.
- `templates/start.html`: homepage template.
- `tools/library.py`: rebuild, verify, and package with Python 3.10+ and the standard library.
- `START-HERE.html`: ready-to-open generated homepage, committed for convenience.
- `SHA256SUMS.json`: generated file checksums to detect changed or damaged copies.
- `docs/ROADMAP.md`: next milestones and the offline acceptance checklist.

## Build and check

```powershell
python tools/library.py build
python tools/library.py verify
python -m unittest discover -s tests -v
node tests/test_search.js
python tools/library.py package
```

`package` checks the current build and writes separate portable and source ZIPs under `dist/`. It refuses to overwrite an existing ZIP. It uses explicit file lists; private data, downloads, and the Git repository are never swept into a shared archive. File checksums detect corruption relative to this manifest; they do not establish publisher authenticity.

Node.js is needed only for the search test; reading the library and running the Python build do not require it. A source checkout with added third-party files requires those files to be restored separately before rebuilding.

## Add content later

For each selected title, record its exact edition, publisher URL, download URL, format, byte size, SHA-256, attribution, and actual redistribution terms. Review the complete file and any separately licensed material. Keep publisher notices intact. Candidate entries are not approved simply because a site is free to read.

To add a self-contained HTML/PDF/TXT file, place it under `content/external/`, record its path and SHA-256 in a catalog entry, set `rights_status` to `reviewed`, and add a `rights_note`. Change its `state` to `included` only after opening it offline. Supply a reader requirement if the browser cannot open the format. Rebuild and verify. The tool requires a recorded checksum for every non-original included file. Complex HTML with images needs all assets bundled and linked locally; PDF or a complete ZIM archive is preferable.

For Kiwix, choose and test a Windows reader plus a specific ZIM archive. Keep software licensing and archive-content licensing as separate records. Do not claim an archive is usable until its reader has also been tested on the destination machine. Large archives stay out of Git; retain exact version and checksum records in the catalog.

## Share and develop

Public repository: [theNeighborrr/offline-resilience-library](https://github.com/theNeighborrr/offline-resilience-library). Share this link with friends so they can download the starter. Keep the source code, blank forms, catalog, and tests in Git. Store bulk downloads and finished USB copies separately. Do not commit filled-in household forms.

## Rights

Third-party works retain their own terms. Original blank worksheets may be copied as part of this personal/friends collection. A project-wide open-source license has not yet been selected. The source catalog is a research queue; it does not grant rights to redistribute the listed third-party works.
