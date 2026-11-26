// Export the Claude Design canvas pages to a plain static website.
// usage: node build.js <srcProjectDir> <blobDir> <outDir>
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const [SRC, BLOBS, OUT] = process.argv.slice(2);
const H = __dirname;

// page file -> output file + clean URL
const PAGES = {
  'Main.dc.html': { out: 'index.html', url: '/' },
  'About.dc.html': { out: 'about.html', url: '/about' },
  'Portfolio.dc.html': { out: 'portfolio.html', url: '/portfolio' },
  'WayATL.dc.html': { out: 'wayatl.html', url: '/wayatl' },
  'LAYA.dc.html': { out: 'laya.html', url: '/laya' },
  'Jinx.dc.html': { out: 'jinx.html', url: '/jinx' },
};
const SOON = ['Accommodate.dc.html', 'MURK.dc.html', 'Infographics.dc.html'];

const docs = {};
for (const f of fs.readdirSync(SRC)) if (f.endsWith('.dc.html')) docs[f] = fs.readFileSync(path.join(SRC, f), 'utf8');

const blobExt = {};
for (const f of fs.readdirSync(BLOBS)) { const [id, ext] = f.split('.'); blobExt[id] = ext; }

const runtime = `
(function(){
const h = React.createElement;
window.DCLogic = class { constructor(p){ this.props = p||{}; } };
function vals(scriptText, props){
  const C = new Function('DCLogic', scriptText + '\\nreturn Component;')(DCLogic);
  return new C(props).renderVals() || {};
}
function camel(s){ return s.replace(/-([a-z])/g, (_,c)=>c.toUpperCase()); }
function fill(root, v){
  root.querySelectorAll('*').forEach(el=>{
    for (const a of Array.from(el.attributes)) {
      const m = a.value.match(/^\\{\\{(\\w+)\\}\\}$/);
      if (m) { el.__raw = el.__raw||{}; el.__raw[a.name] = v[m[1]]; }
      if (a.value.includes('{{')) el.setAttribute(a.name, a.value.replace(/\\{\\{(\\w+)\\}\\}/g, (_,k)=> v[k]==null?'':String(v[k])));
    }
  });
  root.querySelectorAll('sc-if').forEach(el=>{
    const ok = el.__raw && el.__raw.value;
    if (ok) el.replaceWith(...Array.from(el.childNodes)); else el.remove();
  });
}
window.__build = function(docs, main){
  const headItems = [];
  function expand(name, props, target){
    const d = new DOMParser().parseFromString(docs[name], 'text/html');
    const sc = d.querySelector('script[data-dc-script]');
    let defaults = {};
    try { const dp = JSON.parse(sc.getAttribute('data-props')||'{}'); for (const k in dp) if (dp[k] && 'default' in dp[k]) defaults[k] = dp[k].default; } catch(e){}
    const v = vals(sc ? sc.textContent : 'class Component extends DCLogic{renderVals(){return {}}}', Object.assign({}, defaults, props));
    const helm = d.querySelector('helmet');
    if (helm) { for (const n of Array.from(helm.children)) headItems.push(n.outerHTML); helm.remove(); }
    const xdc = d.querySelector('x-dc');
    const frag = document.createElement('div');
    frag.append(...Array.from(xdc.childNodes).map(n=>document.importNode(n,true)));
    fill(frag, v);
    frag.querySelectorAll('dc-import').forEach(di=>{
      const p = {}; for (const a of di.attributes) p[camel(a.name)] = (di.__raw&&a.name in di.__raw)? di.__raw[a.name] : a.value;
      const holder = document.createElement('div');
      expand(di.getAttribute('name') + '.dc.html', p, holder);
      di.replaceWith(...Array.from(holder.childNodes));
    });
    target.append(...Array.from(frag.childNodes));
  }
  expand(main, {}, document.body);
  let x;
  while ((x = document.body.querySelector('x-import'))) {
    const comp = x.getAttribute('component-from-global-scope').split('.').reduce((o,k)=>o&&o[k], window);
    if (!comp) throw new Error('missing component ' + x.getAttribute('component-from-global-scope'));
    const props = {};
    for (const a of x.attributes) { if (a.name==='component-from-global-scope'||a.name.startsWith('hint-')) continue; let val = (x.__raw && a.name in x.__raw) ? x.__raw[a.name] : a.value; props[camel(a.name)] = val; }
    if (props.class) { props.className = props.class; delete props.class; }
    const hasKids = x.childNodes.length && x.innerHTML.trim();
    if (hasKids) props.children = h('x-slot');
    const html = ReactDOMServer.renderToStaticMarkup(h(comp, props));
    const t = document.createElement('template'); t.innerHTML = html;
    const slot = t.content.querySelector('x-slot');
    if (slot) slot.replaceWith(...Array.from(x.childNodes));
    x.replaceWith(t.content);
  }
  return { head: headItems, body: document.body.innerHTML };
};
})();`;

(async () => {
  const b = await chromium.launch();
  const pg = await b.newPage();
  const results = {};
  for (const name of Object.keys(PAGES)) {
    await pg.setContent('<!doctype html><html><head></head><body></body></html>');
    await pg.addScriptTag({ path: path.join(H, 'node_modules/react/umd/react.production.min.js') });
    await pg.addScriptTag({ path: path.join(H, 'node_modules/react-dom/umd/react-dom-server-legacy.browser.production.min.js') });
    await pg.addScriptTag({ path: path.join(SRC, 'ds/ak/components/bundle.js') });
    await pg.addScriptTag({ content: runtime });
    results[name] = await pg.evaluate(([d, m]) => window.__build(d, m), [docs, name]);
  }
  await b.close();
  fs.writeFileSync(path.join(OUT, '_raw.json'), JSON.stringify(results));
  console.log('rendered', Object.keys(results).length, 'pages');
})().catch(e => { console.error(e); process.exit(1); });
