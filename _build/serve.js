const http=require('http'),fs=require('fs'),path=require('path');
const root=process.argv[2],port=+process.argv[3]||8080;
const types={'.html':'text/html','.css':'text/css','.png':'image/png','.jpg':'image/jpeg','.webp':'image/webp','.mp4':'video/mp4','.ttf':'font/ttf','.otf':'font/otf','.json':'application/json','.xml':'application/xml','.txt':'text/plain','.pdf':'application/pdf'};
http.createServer((q,r)=>{let p=decodeURIComponent(q.url.split('?')[0]);if(p==='/')p='/index.html';let f=path.join(root,p);if(!path.extname(f))f+='.html';
fs.readFile(f,(e,d)=>{if(e){r.writeHead(404);r.end('404');return;}r.writeHead(200,{'content-type':types[path.extname(f)]||'application/octet-stream'});r.end(d);});}).listen(port,()=>console.log('up',port));
