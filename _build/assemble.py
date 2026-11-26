# Turn the rendered page bodies (_raw.json) into the final static site folder.
# usage: python3 assemble.py <srcProjectDir> <blobDir> <outDir>
import json, os, re, shutil, sys, html

SRC, BLOBS, OUT = sys.argv[1:4]
SITE = os.path.join(OUT, 'site')
DOMAIN = 'https://archanakannan.org'

PAGES = {
    'Main.dc.html': ('index.html', '/'),
    'About.dc.html': ('about.html', '/about'),
    'Portfolio.dc.html': ('portfolio.html', '/portfolio'),
    'WayATL.dc.html': ('wayatl.html', '/wayatl'),
    'LAYA.dc.html': ('laya.html', '/laya'),
    'Jinx.dc.html': ('jinx.html', '/jinx'),
}
SOON = {'Accommodate.dc.html': 'SCAD Accommodate', 'MURK.dc.html': 'MURK', 'Infographics.dc.html': 'Infographic Design'}
DESC = {
    'Main.dc.html': 'Archana Kannan is a UI/UX designer in Atlanta. Case studies in product design, research and graphic design.',
    'About.dc.html': 'About Archana Kannan, UI/UX designer: background, experience and how she works.',
    'Portfolio.dc.html': 'Selected UI/UX and graphic design projects by Archana Kannan.',
    'WayATL.dc.html': 'WayATL: a multilingual wayfinding web app for fans at the 2026 FIFA World Cup in Atlanta. UI/UX case study by Archana Kannan.',
    'LAYA.dc.html': 'LAYA: an AI leadership platform for newly PE-backed executives in their first 100 days. UI/UX case study by Archana Kannan.',
    'Jinx.dc.html': 'Jinx: a hand-drawn playing-card deck and packaging inspired by Arcane. Graphic design project by Archana Kannan.',
}
OG_IMG = {  # social preview image per page (asset id)
    'Main.dc.html': 'a1889a93f6cd6be676451e73ab9da8d9',
    'About.dc.html': 'a1889a93f6cd6be676451e73ab9da8d9',
    'Portfolio.dc.html': 'c2cc7ef31978651b7a8eafd556bc45b3',
    'WayATL.dc.html': 'c2cc7ef31978651b7a8eafd556bc45b3',
    'LAYA.dc.html': '352fc2d4969f460e832c488de6656d42',
    'Jinx.dc.html': 'b086ae3448a5b18f96a7bc1322249490',
}
FAVICON = '2f3749e4e9e6d088b02340126ade3fc6'
# Adobe Fonts web project: Snaga Unicase Display, Forma DJR Banner, Helvetica Neue LT Pro
TYPEKIT = 'https://use.typekit.net/zhl4enq.css'

raw = json.load(open(os.path.join(OUT, '_raw.json')))
blob_ext = {f.split('.')[0]: f.split('.')[1] for f in os.listdir(BLOBS)}

if os.path.exists(SITE): shutil.rmtree(SITE)
os.makedirs(os.path.join(SITE, 'assets')); os.makedirs(os.path.join(SITE, 'css'))
for f in ['tokens.css']: shutil.copy(os.path.join(SRC, 'ds/ak', f), os.path.join(SITE, 'css', f))
shutil.copy(os.path.join(SRC, 'ds/ak/components/bundle.css'), os.path.join(SITE, 'css/components.css'))
shutil.copy(os.path.join(SRC, 'motion.css'), os.path.join(SITE, 'css/motion.css'))

SITE_CSS = """/* Site-only additions for the published build */
html{background:var(--bg)}
/* below the desktop breakpoint the sidebar sits on top, so the page content needs its own full-width row */
@media (max-width:1023px){body .main{flex:1 1 100%}}
/* tab panels stack in one grid cell: let them shrink to the column instead of the widest panel */
.rx>.rx-panels{min-width:0;max-width:100%}
.rx-panels>.rx-panel{min-width:0}
@media (max-width:600px){.dz-table{display:block;max-width:100%;overflow-x:auto}}
/* keep the footer email on screen on phones */
@media (max-width:600px){footer#connect a[href^="mailto:"]{font-size:clamp(17px,5vw,24px)!important;max-width:100%}}
.is-soon{cursor:default}
.is-soon .ak-card__media{filter:grayscale(1) brightness(.5)}
.is-soon:hover .ak-card__media{transform:none}
.is-soon:hover .ak-card__frame{box-shadow:none}
.is-soon:hover .ak-card__title{text-decoration:none}
.soon-row{display:inline-flex;flex-wrap:wrap;gap:var(--space-2)}
.bento .ak-card__meta.soon-badge{border-color:var(--border-strong);color:var(--text-strong)}
.soon-tag{margin-left:var(--space-2);padding:2px 6px;border:var(--border-width) solid var(--border-subtle);border-radius:var(--radius-pill);font-size:10px;letter-spacing:.08em;text-transform:uppercase;color:var(--text-muted)}
"""
open(os.path.join(SITE, 'css/site.css'), 'w').write(SITE_CSS)

used = set()
def fix_blobs(s):
    def rep(m):
        i = m.group(1); used.add(i)
        return f'/assets/{i}.{blob_ext[i]}'
    return re.sub(r'/_blob/([0-9a-f]{32})', rep, s)

def fix_links(s):
    for src, (_, url) in PAGES.items():
        s = s.replace(f'href="{src}"', f'href="{url}"')
    s = s.replace('href="https://archanakannan.org/resume/Archana-Kannan-Resume.pdf"', 'href="/resume/Archana-Kannan-Resume.pdf"')
    return s

def soon(s):
    for src, name in SOON.items():
        # project cards on the Portfolio page
        def card(m):
            block = m.group(0)
            block = block.replace(f'<a class="ak-card ak-card--landscape" href="{src}">',
                                  f'<div class="ak-card ak-card--landscape is-soon" aria-label="{name}, coming soon">', 1)
            block = block[:-4] + '</div>'
            block = re.sub(r'(<span class="ak-card__meta">)(.*?)(</span>)',
                           r'<span class="soon-row">\1\2\3<span class="ak-card__meta soon-badge">Coming soon</span></span>', block, 1)
            return block
        s = re.sub(rf'<a class="ak-card ak-card--landscape" href="{re.escape(src)}">.*?</a>', card, s, flags=re.S)
        # sidebar case-study links
        s = re.sub(rf'<a href="{re.escape(src)}" aria-current="[^"]*" style="([^"]*)">(.*?)</a>',
                   lambda m: f'<span aria-disabled="true" style="{m.group(1)}; cursor: default">{m.group(2)}<span class="soon-tag">Soon</span></span>', s)
    # LAYA's "next case study" pointed at SCAD Accommodate: send it to Jinx
    s = s.replace('<a class="next" href="Accommodate.dc.html"><span style="display: flex; flex-direction: column; gap: var(--space-3)"><span class="cap">Next case study</span><span style="font-family: var(--font-display); font-weight: 800; font-size: clamp(44px,4.6vw,64px); line-height: .96">SCAD Accommodate</span>',
                  '<a class="next" href="/jinx"><span style="display: flex; flex-direction: column; gap: var(--space-3)"><span class="cap">Next project</span><span style="font-family: var(--font-display); font-weight: 800; font-size: clamp(44px,4.6vw,64px); line-height: .96">Jinx</span>')
    return s

for src, (out, url) in PAGES.items():
    doc = open(os.path.join(SRC, src)).read()
    title = html.unescape(re.search(r'<title>(.*?)</title>', doc).group(1))
    has_motion = 'motion.css' in doc
    seen, head_extra, fonts = set(), [], []
    for item in raw[src]['head']:
        if item in seen: continue
        seen.add(item)
        (fonts if item.startswith('<link') else head_extra).append(item)
    body = soon(fix_links(fix_blobs(raw[src]['body'])))
    # Nike role has no title/description yet: leave it off until filled in on the canvas
    body = re.sub(r'<li class="exp-row">\s*<p class="exp-date">[^<]*</p>\s*<div class="exp-body">\s*<h3 class="exp-role">\[Role title\]</h3>.*?</li>\s*', '', body, flags=re.S)
    head_extra = [fix_blobs(h) for h in head_extra]
    for ext in ['.dc.html']:
        left = re.findall(r'href="([^"]*' + re.escape(ext) + ')"', body)
        if left: print('WARNING unresolved links in', src, set(left))
    canonical = DOMAIN + ('' if url == '/' else url)
    og = f'{DOMAIN}/assets/{OG_IMG[src]}.{blob_ext[OG_IMG[src]]}'; used.add(OG_IMG[src])
    t = html.escape(title, quote=True); d = html.escape(DESC[src], quote=True)
    page = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<meta name="description" content="{d}">
<link rel="canonical" href="{canonical}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Archana Kannan">
<meta property="og:title" content="{t}">
<meta property="og:description" content="{d}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{og}">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#0D0D0D">
<link rel="icon" type="image/png" href="/assets/{FAVICON}.{blob_ext[FAVICON]}">
<link rel="preconnect" href="https://use.typekit.net" crossorigin>
<link rel="stylesheet" href="{TYPEKIT}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
{chr(10).join(fonts)}
<link rel="stylesheet" href="/css/tokens.css">
<link rel="stylesheet" href="/css/components.css">
{'<link rel="stylesheet" href="/css/motion.css">' if has_motion else ''}
<link rel="stylesheet" href="/css/site.css">
{chr(10).join(head_extra)}
</head>
<body style="margin:0">
{body}
</body>
</html>
"""
    open(os.path.join(SITE, out), 'w').write(page)
used.add(FAVICON)
for i in sorted(used):
    shutil.copy(os.path.join(BLOBS, f'{i}.{blob_ext[i]}'), os.path.join(SITE, 'assets'))

json.dump({"cleanUrls": True, "trailingSlash": False,
           "headers": [{"source": "/assets/(.*)", "headers": [{"key": "Cache-Control", "value": "public, max-age=31536000, immutable"}]}]},
          open(os.path.join(SITE, 'vercel.json'), 'w'), indent=2)
open(os.path.join(SITE, 'robots.txt'), 'w').write(f'User-agent: *\nAllow: /\nSitemap: {DOMAIN}/sitemap.xml\n')
urls = ''.join(f'  <url><loc>{DOMAIN + ("" if u == "/" else u)}</loc></url>\n' for _, u in PAGES.values())
open(os.path.join(SITE, 'sitemap.xml'), 'w').write(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}</urlset>\n')
print('pages', len(PAGES), 'assets', len(used))
