#!/usr/bin/env python3
import argparse,hashlib,json,os,re,subprocess
from pathlib import Path
from release_config import ROOT,load,approved_apk_url
p=argparse.ArgumentParser();p.add_argument('--release-dir',required=True);a=p.parse_args();d=Path(a.release_dir).resolve();i=json.loads((d/'release.json').read_text());c=load()
if i.get('testOnly') is not False or set(i['artifacts'])!={'tv','mobile'}:raise ValueError('deux APK client requis')
if not re.fullmatch(r'\d+\.\d+\.\d+',str(i['version'])) or type(i['versionCode']) is not int or i['versionCode']<10:raise ValueError('version invalide')
for t,item in i['artifacts'].items():
 spec=c['artifacts'][t];cert=(ROOT/spec['certificateFile']).read_text().strip()
 if item['package']!=spec['package'] or item['stableFile']!=spec['stableAssetName'] or item['certificateSha256']!=cert or not re.fullmatch('[0-9a-f]{64}',cert):raise ValueError('identité ou certificat incorrect')
 approved_apk_url(item['url'],c,t);f=d/spec['stableAssetName'];data=f.read_bytes()
 if len(data)!=item['size'] or hashlib.sha256(data).hexdigest()!=item['sha256']:raise ValueError('octets incorrects')
 subprocess.run(['bash',str(ROOT/'scripts/ci/inspect-apk.sh'),str(f),spec['package'],str(i['versionCode']),i['version'],str(d/'public-inspection.md'),'armeabi-v7a,arm64-v8a',t],check=True,env={**os.environ,'ALLOW_UNSIGNED':'0'})
 subprocess.run(['python3',str(ROOT/'scripts/release/check_alignment.py'),str(f)],check=True)
print('Deux APK contrôlés : signature, identité, version, manifeste, Hermes, ABI, alignement et SHA-256.')
