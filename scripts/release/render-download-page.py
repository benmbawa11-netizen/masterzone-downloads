#!/usr/bin/env python3
import argparse,html,json,shutil
from pathlib import Path
from release_config import ROOT,load,approved_apk_url

def render(c,release=None):
 cards=[]
 for t,title,desc in [('mobile','Android','Téléphone et tablette'),('tv','Android TV / Google TV','Téléviseur et boîtier TV')]:
  item=(release or {}).get('artifacts',{}).get(t);body='<p>APK non publié.</p><span class="download disabled" aria-disabled="true">Téléchargement indisponible</span>'
  if item:
   if release.get('testOnly') is not False or item['package']!=c['artifacts'][t]['package']:raise ValueError('APK client requis')
   if item.get('url'):
    url=approved_apk_url(item['url'],c,t);esc=html.escape
    dc=str(c['artifacts'][t].get('downloaderCode',''));code=f'<p>Avec l’application <strong>Downloader</strong> : tapez le code <strong style="font-size:1.6em">{esc(dc)}</strong> puis « Go ».</p>' if dc.isdigit() else ''
    body=f'<p>Version {esc(release["version"])} ({int(release["versionCode"])}) · {int(item["size"])/1000000:.1f} Mo</p><a class="download" href="{esc(url,quote=True)}">Télécharger l’APK {title}</a>{code}<details><summary>Vérifier le fichier</summary><p>{esc(item["file"])}</p><p>SHA-256</p><code>{esc(item["sha256"])}</code><p>Certificat SHA-256</p><code>{esc(item["certificateSha256"])}</code></details>'
  cards.append(f'<section class="card"><small>{desc}</small><h2>{title}</h2>{body}</section>')
 return (ROOT/'distribution/index.template.html').read_text().replace('{{CARDS}}','\n'.join(cards))

def main():
 p=argparse.ArgumentParser();p.add_argument('--release-json');p.add_argument('--config');p.add_argument('--out',required=True);a=p.parse_args();d=Path(a.out);d.mkdir(exist_ok=True,parents=True)
 release=json.loads(Path(a.release_json).read_text()) if a.release_json else None
 (d/'index.html').write_text(render(load(a.config),release));shutil.copyfile(ROOT/'distribution/logo-192.png',d/'logo-192.png');(d/'.nojekyll').touch()
if __name__=='__main__':main()
