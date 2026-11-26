# Re-publishing the site from the design canvas

The pages are designed on the Claude Design canvas (artifact bc4d1e5f-38c4-44c7-8254-b525eefaf53e) and exported here as plain HTML. This folder holds the export scripts; Vercel does not deploy it (see `.vercelignore`).

1. Download the canvas's `project/` files (`*.dc.html`, `ds/ak/*`, `motion.css`) into a source folder, and every image they reference (`/_blob/<id>`) into a blob folder as `<id>.<ext>`. Existing images are already in `/assets/` under the same names.
2. `cd _build && npm install && npm install playwright`
3. `node build.js <srcProjectDir> <blobDir> <outDir>` renders each page to `<outDir>/_raw.json`.
4. `python3 assemble.py <srcProjectDir> <blobDir> <outDir>` writes the finished site to `<outDir>/site/` (asset paths, clean URLs, "Coming soon" projects, metadata, Adobe Fonts link, vercel.json, sitemap).
5. Copy `<outDir>/site/` over the repository root (keep `resume/` and `_build/`), commit and push. Vercel redeploys automatically.

To publish a finished project, move it from `SOON` to `PAGES` in both scripts and add its description and preview image in `assemble.py`.
