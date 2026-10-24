# MasterZone TV — téléchargement

Ce dépôt sert uniquement à distribuer l’application **MasterZone TV** pour Android TV, Google TV et les boîtiers
Android. Il ne contient pas le code source de l’application.

## Télécharger

- Page d’installation : <https://rv2kd22k9n-star.github.io/masterzone-tv/>
- Fichier de la dernière version : <https://github.com/rv2kd22k9n-star/masterzone-tv/releases/latest/download/masterzone-tv.apk>

Sur le téléviseur : installez **Downloader**, autorisez-le à installer des applications, tapez l’adresse
indiquée sur la page d’installation, puis choisissez **Installer**.

## Vérifier le fichier

- Identifiant Android : `com.masterzone.tv`
- Empreinte SHA-256 de chaque APK : dans la description de sa release et dans `SHA256SUMS.txt`
- Certificat de signature MasterZone (SHA-256) : `a483df854d4b6f59879a76889d6559476769553efb5e54055d2e6d5ca90a91d9`
  (fichier public `certificat/masterzone-tv-certificate.pem`)

Toutes les versions sont signées avec ce même certificat : une nouvelle version s’installe par-dessus la
précédente en conservant le compte et les réglages.

## Publication (réservé à MasterZone)

Une version est publiée en poussant une branche `publication/vX.Y.Z` contenant `release/masterzone-tv.apk`,
`release/release.json` et `release/notes.md`. Le workflow « Publier une version » contrôle l’identifiant, le
numéro de version, l’empreinte et le certificat MasterZone, crée la release, vérifie le lien public sans compte,
puis supprime la branche : le fichier reste uniquement dans la release. Pour compléter la description d’une
version déjà publiée (résultats de tests, par exemple), poussez `notes/vX.Y.Z.md` sur `main`.

Support : masterzone195@gmail.com
