# MasterZone — téléchargements Android et TV

Ce dépôt public contient uniquement la page, les outils de distribution et les certificats PUBLICS. Les sources de l’application, l’historique privé et les clés restent privés.

Configurer `distribution/release-config.json` avec le dépôt public autorisé et la page HTTPS réellement attribuée. Sans configuration ni APK publié, les deux boutons restent indisponibles. Les anciens liens courts ne sont plus utilisés.

Le workflow privé `masterzone-publish.yml` publie les fichiers signés et vérifiés, `release.json` et les empreintes. Le jeton inter-dépôts doit être limité à Contents: write sur ce seul dépôt public. Activer **Settings → Pages → Source → GitHub Actions** : après publication d’une release, `publier-page.yml` télécharge sans compte les deux APK, vérifie les certificats et déploie la page. Seul le job de déploiement dispose de Pages: write et OIDC.

Les noms stables sont `MasterZone-Android.apk` et `MasterZone-TV.apk`. Les noms versionnés conservent les mêmes octets. Un APK preview, TEST-ONLY, non signé, mal identifié ou signé avec un autre certificat est refusé. Les certificats attendus sont dans `signing/`.

Les scripts peuvent aussi préparer et vérifier une distribution sur un autre hébergeur HTTPS permis ; aucun compte externe n’est supposé connecté.

## État de publication

Dépôt de distribution autorisé par le propriétaire : benmbawa11-netizen/masterzone-downloads.
- **Téléphone Android 1.8.1 (12)** publié le 29/10/2026, signé avec la **nouvelle clé** MasterZone (les clés d’origine ont été perdues avec l’ancien compte ; aucun client réel n’avait installé l’application). Une ancienne installation 1.7.x doit être désinstallée une fois.
- **Code Downloader téléphone : 9824404** (aftv.news/9824404 → lien « latest », toujours la dernière version).
- **TV Android / Google TV 1.8.1 (12)** publiée le 29/10/2026 avec la nouvelle clé TV (même version que le téléphone).
- **Code Downloader TV : 8474968** (aftv.news/8474968 → lien « latest » de l’APK TV).

### Publier Android avant la TV

La publication accepte une sélection explicite `targets: mobile`. La page conserve les deux choix et laisse la TV indisponible tant que son APK signé n’est pas publié. Les contrôles de certificat, manifeste, version, Hermes, architectures et SHA-256 restent obligatoires pour chaque APK. Sans sélection explicite, les anciens manifestes doivent toujours contenir les deux éditions.

Pour ajouter la TV au même numéro de version, réutiliser exactement l’APK mobile déjà publié dans le brouillon privé contenant la TV : son SHA-256 ne doit pas changer. Un remplacement du mobile exige un versionCode supérieur. Ne jamais utiliser la TV 1.7.1 comme complément.
