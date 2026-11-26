const {chromium,devices}=require('playwright');const path=require('path');
const out=process.argv[2];const pages=['/','/about','/portfolio','/wayatl','/laya','/jinx'];
(async()=>{const b=await chromium.launch();
for(const [label,opts] of [['phone',{...devices['iPhone 13'],reducedMotion:'reduce'}]]){
 const ctx=await b.newContext(opts);
 for(const p of pages){const pg=await ctx.newPage();const bad=[];
  pg.on('response',r=>{if(r.status()>=400)bad.push(r.status()+' '+r.url())});
  pg.on('console',m=>{if(m.type()==='error')bad.push('console: '+m.text())});
  await pg.goto('http://localhost:8080'+p,{waitUntil:'networkidle'});
  await pg.evaluate(async()=>{for(let y=0;y<document.body.scrollHeight;y+=600){window.scrollTo(0,y);await new Promise(r=>setTimeout(r,40));}window.scrollTo(0,0);});
  await pg.waitForTimeout(400);
  const w=await pg.evaluate(()=>document.documentElement.scrollWidth>window.innerWidth+1);
  const name=(p==='/'?'home':p.slice(1))+'-'+label;
  await pg.screenshot({path:path.join(out,name+'.png'),fullPage:true});
  console.log(name,'hscroll:',w,bad.length?bad:'');await pg.close();}
 await ctx.close();}
await b.close();})();
