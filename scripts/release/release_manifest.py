"""Explicit publication targets and safe addition of the second Android edition."""


def publication_targets(release):
    targets = release.get('targets', ['mobile', 'tv'])
    if (not isinstance(targets, list) or not targets
            or any(t not in ('mobile', 'tv') for t in targets)
            or len(targets) != len(set(targets))
            or set(release.get('artifacts', {})) != set(targets)):
        raise ValueError('Les APK doivent correspondre exactement aux variantes annoncées')
    return targets


def check_progression(previous, current):
    previous_targets = set(publication_targets(previous))
    current_targets = set(publication_targets(current))
    old_code, new_code = previous['versionCode'], current['versionCode']
    if type(old_code) is not int or type(new_code) is not int or new_code < old_code:
        raise ValueError('versionCode en recul ou invalide')
    if new_code == old_code:
        if (previous['version'] != current['version']
                or not previous_targets < current_targets):
            raise ValueError('Même versionCode : seul l’ajout d’une variante est autorisé')
        for target in previous_targets:
            for field in ('package', 'sha256', 'certificateSha256'):
                if previous['artifacts'][target][field] != current['artifacts'][target][field]:
                    raise ValueError('Un APK déjà publié ne peut changer avec le même versionCode')
