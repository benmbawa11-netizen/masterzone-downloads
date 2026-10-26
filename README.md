# MasterZone — téléchargements Android et TV

Ce dépôt public contient uniquement la page, les outils de distribution et les certificats PUBLICS. Les sources de l’application, l’historique privé et les clés restent privés.

Configurer `distribution/release-config.json` avec le dépôt public autorisé et la page HTTPS réellement attribuée. Sans configuration ni APK publié, les deux boutons restent indisponibles. Les anciens liens courts ne sont plus utilisés.

Le workflow privé `masterzone-publish.yml` publie les fichiers signés et vérifiés, `release.json` et les empreintes. Le jeton inter-dépôts doit être limité à Contents: write sur ce seul dépôt public. Activer **Settings → Pages → Source → GitHub Actions** : après publication d’une release, `publier-page.yml` télécharge sans compte les deux APK, vérifie les certificats et déploie la page. Seul le job de déploiement dispose de Pages: write et OIDC.

Les noms stables sont `MasterZone-Android.apk` et `MasterZone-TV.apk`. Les noms versionnés conservent les mêmes octets. Un APK preview, TEST-ONLY, non signé, mal identifié ou signé avec un autre certificat est refusé. Les certificats attendus sont dans `signing/`.

Les scripts peuvent aussi préparer et vérifier une distribution sur un autre hébergeur HTTPS permis ; aucun compte externe n’est supposé connecté.

## État de publication

Dépôt de distribution autorisé par le propriétaire : benmbawa11-netizen/masterzone-downloads. Aucun APK client n’est encore publié. Les deux téléchargements restent indisponibles jusqu’à l’obtention et à la vérification de véritables APK signés.
