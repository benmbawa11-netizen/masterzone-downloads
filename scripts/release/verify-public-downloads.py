#!/usr/bin/env python3
import argparse,hashlib,json,shutil,urllib.request
from pathlib import Path
from release_config import load,approved_apk_url
class HttpsRedirect(urllib.request.HTTPRedirectHandler):
 def redirect_request(self,req,fp,code,msg,headers,newurl):
  if not newurl.startswith('https://'):raise ValueError('redirection non HTTPS refusée')
  return super().redirect_request(req,fp,code,msg,headers,newurl)
def main():
 p=argparse.ArgumentParser();p.add_argument('--release-json',required=True);p.add_argument('--out',required=True);a=p.parse_args();info=json.loads(Path(a.release_json).read_text());c=load();d=Path(a.out);d.mkdir(exist_ok=True,parents=True)
 if info.get('testOnly') is not False or set(info['artifacts'])!={'tv','mobile'}:raise ValueError('Deux APK client requis')
 results=[]
 for target,item in info['artifacts'].items():
  url=approved_apk_url(item['url'],c,target);size=int(item['size'])
  if not 0<size<250000000:raise ValueError('taille invalide')
  f=d/item['file'];sha=hashlib.sha256();received=0;opener=urllib.request.build_opener(HttpsRedirect())
  with opener.open(urllib.request.Request(url,headers={'User-Agent':'MasterZone-anonymous-check'}),timeout=60) as response,f.open('wb') as out:
   if response.status!=200:raise ValueError('HTTP 200 requis')
   while True:
    data=response.read(1024*1024)
    if not data:break
    received+=len(data)
    if received>size:raise ValueError('taille téléchargée excessive')
    sha.update(data);out.write(data)
  if received!=size or sha.hexdigest()!=item['sha256']:f.unlink(missing_ok=True);raise ValueError('taille ou SHA-256 incorrect')
  shutil.copyfile(f,d/item['stableFile']);results.append({'target':target,'url':url,'anonymous':True,'size':received,'sha256':sha.hexdigest()})
 (d/'release.json').write_text(json.dumps(info,indent=2));(d/'anonymous-downloads.json').write_text(json.dumps(results,indent=2));print(json.dumps(results,indent=2))
if __name__=='__main__':main()
