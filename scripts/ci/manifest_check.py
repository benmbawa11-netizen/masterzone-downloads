#!/usr/bin/env python3
"""Structural checks of a compiled AndroidManifest.xml for an Android mobile or TV release.

Reads the output of `aapt2 dump xmltree --file AndroidManifest.xml <apk>` on stdin (aapt and aapt2 formats are
both accepted) and exits 1 with readable French messages when the TV launch contract is not met.
"""
import argparse
import json
import re
import sys


def parse(text):
    root = {'tag': 'root', 'attrs': {}, 'children': []}
    stack = [(-1, root)]
    for line in text.splitlines():
        stripped = line.lstrip(' ')
        depth = len(line) - len(stripped)
        if stripped.startswith('E: '):
            tag = stripped[3:].split(' ', 1)[0]
            while stack and stack[-1][0] >= depth:
                stack.pop()
            node = {'tag': tag, 'attrs': {}, 'children': []}
            stack[-1][1]['children'].append(node)
            stack.append((depth, node))
        elif stripped.startswith('A: '):
            body = stripped[3:]
            name_part, _, value = body.partition('=')
            name = re.sub(r'\(0x[0-9a-f]+\)$', '', name_part).split(':')[-1]
            raw = re.search(r'\(Raw: "(.*)"\)\s*$', value)
            if raw:
                value = raw.group(1)
            else:
                value = re.sub(r'^\(type 0x[0-9a-f]+\)', '', value.strip()).strip('"')
            stack[-1][1]['attrs'][name] = value
    return root


def walk(node):
    yield node
    for child in node['children']:
        yield from walk(child)


def falsy(value):
    return str(value).lower() in ('false', '0x0', '0')


def check(text,target='tv'):
    if target not in ('mobile','tv'):raise ValueError('target')
    tree = parse(text)
    nodes = list(walk(tree))
    errors, facts = [], {}
    application = next((n for n in nodes if n['tag'] == 'application'), None)
    if not application:
        errors.append('élément <application> introuvable')
    else:
        facts['banner'] = application['attrs'].get('banner')
        facts['usesCleartextTraffic'] = application['attrs'].get('usesCleartextTraffic')
        if target=='tv' and not facts['banner']:
            errors.append('android:banner absent : pas de bannière dans le lanceur Android TV')
    launchers = []
    for activity in (n for n in nodes if n['tag'] in ('activity', 'activity-alias')):
        for intent in (c for c in activity['children'] if c['tag'] == 'intent-filter'):
            actions = {c['attrs'].get('name') for c in intent['children'] if c['tag'] == 'action'} - {None}
            categories = {c['attrs'].get('name') for c in intent['children'] if c['tag'] == 'category'} - {None}
            if 'android.intent.action.MAIN' in actions:
                launchers.append({'activity': activity['attrs'].get('name'), 'categories': sorted(categories),
                                  'screenOrientation': activity['attrs'].get('screenOrientation')})
    facts['launchers'] = launchers
    tv_launcher=any('android.intent.category.LEANBACK_LAUNCHER' in l['categories'] for l in launchers)
    if target=='mobile' and tv_launcher:errors.append('lanceur TV interdit sur mobile')
    if target=='tv' and not tv_launcher:
        errors.append("aucune activité MAIN avec la catégorie LEANBACK_LAUNCHER : l'application n'apparaîtrait pas sur l'accueil Android TV")
    if not any('android.intent.category.LAUNCHER' in l['categories'] for l in launchers):
        errors.append('aucune activité MAIN avec la catégorie LAUNCHER')
    features = {n['attrs'].get('name'): n['attrs'].get('required', 'true') for n in nodes if n['tag'] == 'uses-feature'}
    facts['features'] = features
    for name in (('android.hardware.touchscreen','android.software.leanback') if target=='tv' else ()):
        if name not in features:
            errors.append(f'{name} non déclaré')
        elif not falsy(features[name]):
            errors.append(f'{name} est déclaré obligatoire : il doit être facultatif')
    if application:
        for name in ('debuggable','testOnly'):
            if name in application['attrs'] and not falsy(application['attrs'][name]):errors.append(name+' interdit en production')
    for launcher in launchers:
        if target=='mobile' and str(launcher['screenOrientation']) not in ('10','0xa','fullSensor'):errors.append('rotation mobile fullSensor requise')
        if 'android.intent.category.LEANBACK_LAUNCHER' in launcher['categories'] and str(launcher['screenOrientation']) not in ('0', '0x0', 'landscape'):
            errors.append(f"orientation du lecteur inattendue : {launcher['screenOrientation']} (paysage attendu)")
    return facts, errors

def main():
    parser=argparse.ArgumentParser();parser.add_argument('target',nargs='?',choices=['mobile','tv'],default='tv');args=parser.parse_args()
    facts,errors=check(sys.stdin.read(),args.target)
    print(json.dumps(facts, ensure_ascii=False))
    for error in errors:
        print('ERREUR: ' + error, file=sys.stderr)
    sys.exit(1 if errors else 0)


if __name__ == '__main__':
    main()
