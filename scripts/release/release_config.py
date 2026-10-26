import json,re
from pathlib import Path
from urllib.parse import urlsplit
ROOT=Path(__file__).resolve().parents[2]
def load(path=None):
 c=json.loads(Path(path or ROOT/'distribution/release-config.json').read_text())
 if c.get('schemaVersion')!=1:raise ValueError('configuration inconnue')
 repo=c.get('publicRepository','')
 if repo and not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+',repo):raise ValueError('dépôt invalide')
 for key in ['pageUrl','downloadBaseUrl']:
  if c.get(key):secure_url(c[key])
 return c
def secure_url(url):
 p=urlsplit(url)
 if p.scheme!='https' or not p.hostname or p.username or p.password or p.query or p.fragment or p.port not in (None,443):raise ValueError('URL HTTPS sans identifiants requise')
 if '%' in p.path or '..' in p.path.split('/') or '\\' in p.path:raise ValueError('chemin invalide')
 return p
def download_base(c):
 if c.get('downloadBaseUrl'):return c['downloadBaseUrl'].rstrip('/')
 if c.get('publicRepository'):return 'https://github.com/'+c['publicRepository']+'/releases/latest/download'
 raise ValueError('hébergement non configuré')
def approved_apk_url(url,c,target=None):
 secure_url(url)
 for t in ([target] if target else ['mobile','tv']):
  if url==download_base(c)+'/'+c['artifacts'][t]['stableAssetName']:return url
  if c.get('publicRepository'):
   stem='MasterZone-TV' if t=='tv' else 'MasterZone-Android'
   if re.fullmatch(r'https://github\.com/'+re.escape(c['publicRepository'])+r'/releases/download/v(\d+\.\d+\.\d+)/'+stem+r'-v\1\.apk',url):return url
 raise ValueError('URL extérieure à la distribution configurée')
