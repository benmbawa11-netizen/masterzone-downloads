#!/usr/bin/env python3
"""Reassemble public, already signed APK archives before independent APK inspection."""
import argparse,hashlib,json,lzma,shutil
from pathlib import Path
from release_config import load
from release_manifest import publication_targets,artifact_names

def receive(manifest,release,parts_dir,out_dir,config):
    targets=publication_targets(release)
    archives=manifest.get('archives',[])
    if manifest.get('schemaVersion')!=1 or len(archives)!=len(targets) or {a['target'] for a in archives}!=set(targets):
        raise ValueError('Archives et variantes incompatibles')
    root=Path(parts_dir).resolve();out=Path(out_dir);out.mkdir(parents=True,exist_ok=True)
    for archive in archives:
        target=archive['target'];item=release['artifacts'][target]
        versioned,stable=artifact_names(release,target,config['artifacts'][target])
        if type(item['size']) is not int or not 0<item['size']<250000000:
            raise ValueError('Taille APK invalide')
        if type(archive.get('size')) is not int or not 0<archive['size']<250000000:
            raise ValueError('Taille archive invalide')
        parts=archive.get('parts',[])
        if not 0<len(parts)<=512:raise ValueError('Nombre de fragments invalide')
        chunks=[];total=0
        for index,part in enumerate(parts):
            expected=f'{target}.apk.xz.part-{index:03d}'
            if part.get('file')!=expected or type(part.get('size')) is not int or not 0<part['size']<=750000:
                raise ValueError('Fragment inattendu')
            path=root/expected
            if path.is_symlink() or path.stat().st_size!=part['size']:raise ValueError('Fichier fragment incorrect')
            data=path.read_bytes();total+=len(data)
            if total>archive['size'] or hashlib.sha256(data).hexdigest()!=part['sha256']:
                raise ValueError('Fragment altéré')
            chunks.append(data)
        data=b''.join(chunks)
        if total!=archive['size'] or hashlib.sha256(data).hexdigest()!=archive['sha256']:
            raise ValueError('Archive altérée')
        decoder=lzma.LZMADecompressor(memlimit=128*1024*1024)
        apk=decoder.decompress(data,max_length=item['size']+1)
        if not decoder.eof or decoder.unused_data or len(apk)!=item['size'] or hashlib.sha256(apk).hexdigest()!=item['sha256']:
            raise ValueError('APK altéré ou décompression excessive')
        (out/versioned).write_bytes(apk);shutil.copyfile(out/versioned,out/stable)

def main():
    p=argparse.ArgumentParser();p.add_argument('--manifest',required=True);p.add_argument('--release-json',required=True);p.add_argument('--parts',required=True);p.add_argument('--out',required=True);a=p.parse_args()
    receive(json.loads(Path(a.manifest).read_text()),json.loads(Path(a.release_json).read_text()),a.parts,a.out,load())
    print('Archives reçues et sommes SHA-256 vérifiées ; inspection native et signature encore obligatoires.')

if __name__=='__main__':main()
