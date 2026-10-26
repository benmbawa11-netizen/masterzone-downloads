#!/usr/bin/env bash
# Inspects a built Android or TV APK and fails if it is not a self-contained MasterZone TV release.
# Usage: scripts/ci/inspect-apk.sh <apk> <expected-package> <versionCode> <versionName> <report.md> [expected-abis]
# Requires ANDROID_HOME with build-tools 36.0.0 (aapt2, apksigner) and python3.
set -eu
APK=$1 PACKAGE=$2 VERSION_CODE=$3 VERSION_NAME=$4 REPORT=$5 EXPECTED_ABIS=${6:-}
TARGET=${7:-}
if [ -z "$TARGET" ]; then case "$PACKAGE" in *.tv) TARGET=tv;; *) TARGET=mobile;; esac; fi
case "$TARGET" in mobile|tv) ;; *) echo 'mobile ou tv requis' >&2; exit 1;; esac
BT="$ANDROID_HOME/build-tools/36.0.0"
HERE=$(cd "$(dirname "$0")" && pwd)
WORK=$(mktemp -d)
trap 'rm -rf "$WORK"' EXIT
NAME=$(basename "$APK")
fail() { echo "::error title=APK refusé ($NAME)::$1"; echo "- ÉCHEC : $1" >> "$REPORT"; exit 1; }
line() { grep -m1 "$1" <<< "$BADGING" || echo "$2"; }

test -s "$APK" || fail "fichier absent ou vide"
"$BT/aapt2" dump badging "$APK" > "$WORK/badging.txt"
"$BT/aapt2" dump xmltree --file AndroidManifest.xml "$APK" > "$WORK/manifest.txt"
BADGING=$(cat "$WORK/badging.txt")
SIZE=$(stat -c %s "$APK")
SHA=$(sha256sum "$APK" | cut -d' ' -f1)
PERMISSIONS=$(grep '^uses-permission:' "$WORK/badging.txt" | sed -E "s/.*name='([^']+)'.*/\1/" | tr '\n' ' ' || true)

{
  echo "### $NAME"
  echo
  echo "- Taille : $SIZE octets"
  echo "- SHA-256 : \`$SHA\`"
  echo "- $(line '^package:' 'package: ?')"
  echo "- $(line '^minSdkVersion:' "$(line '^sdkVersion:' 'minSdkVersion: ?')") / $(line '^targetSdkVersion:' 'targetSdkVersion: ?')"
  echo "- $(line '^native-code:' 'native-code: (aucun)')"
  echo "- $(line '^application-label:' 'application-label: ?')"
  echo "- $(line '^launchable-activity:' 'launchable-activity: ABSENT')"
  echo "- $(line '^leanback-launchable-activity:' 'leanback-launchable-activity: (non listé par aapt2)')"
  echo "- Permissions : $PERMISSIONS"
} >> "$REPORT"

grep -q "^package: name='$PACKAGE' versionCode='$VERSION_CODE' versionName='$VERSION_NAME'" "$WORK/badging.txt" \
  || fail "identité attendue $PACKAGE $VERSION_NAME ($VERSION_CODE), obtenu : $(line '^package:' '?')"
if ! FACTS=$(python3 "$HERE/manifest_check.py" "$TARGET" < "$WORK/manifest.txt" 2> "$WORK/manifest-errors.txt"); then
  fail "manifeste $TARGET non conforme : $(tr '\n' ' ' < "$WORK/manifest-errors.txt")"
fi
echo "- Manifeste compilé : \`$FACTS\`" >> "$REPORT"
for permission in SYSTEM_ALERT_WINDOW READ_EXTERNAL_STORAGE WRITE_EXTERNAL_STORAGE RECORD_AUDIO USE_BIOMETRIC USE_FINGERPRINT VIBRATE; do
  if grep -q "uses-permission: name='android.permission.$permission'" "$WORK/badging.txt"; then fail "permission inutile présente : $permission"; fi
done

# The JavaScript must be inside the APK (no Metro / Expo Go) and compiled to Hermes bytecode.
unzip -p "$APK" assets/index.android.bundle > "$WORK/bundle" 2>/dev/null || fail "bundle JavaScript assets/index.android.bundle absent : l'APK dépendrait de Metro"
test -s "$WORK/bundle" || fail "bundle JavaScript vide"
MAGIC=$(head -c 8 "$WORK/bundle" | od -An -tx1 | tr -d ' \n')
BUNDLE_SIZE=$(stat -c %s "$WORK/bundle")
BUNDLE_SHA=$(sha256sum "$WORK/bundle" | cut -d' ' -f1)
[ "$MAGIC" = "c61fbc03c103191f" ] || fail "le bundle n'est pas du bytecode Hermes (signature $MAGIC)"
# Local startup marker replaces the obsolete requirement for a Supabase hostname.
grep -a -q 'masterzone:device-owner:no-account:v1' "$WORK/bundle" || fail "point d’entrée sans compte absent du bundle"
if grep -a -q -E 'nip\.io|sslip\.io|10\.0\.2\.2' "$WORK/bundle"; then fail "adresse de test présente dans le JavaScript : APK de test, pas de production"; fi
echo "- Bundle JavaScript Hermes embarqué : $BUNDLE_SIZE octets, SHA-256 \`$BUNDLE_SHA\`" >> "$REPORT"

if [ -n "$EXPECTED_ABIS" ]; then
  ACTUAL=$(line '^native-code:' '' | sed -E "s/native-code: //; s/'//g" | tr ' ' '\n' | grep -v '^$' | sort | tr '\n' ' ' | sed 's/ $//')
  WANTED=$(tr ',' '\n' <<< "$EXPECTED_ABIS" | sort | tr '\n' ' ' | sed 's/ $//')
  [ "$ACTUAL" = "$WANTED" ] || fail "architectures attendues [$WANTED], obtenues [$ACTUAL]"
fi

# Signature status (unsigned is allowed only with ALLOW_UNSIGNED=1 for private diagnosis).
if "$BT/apksigner" verify --verbose --print-certs "$APK" > "$WORK/signature.txt" 2>&1; then
  if grep -q 'CN=Android Debug' "$WORK/signature.txt"; then fail "signé avec la clé publique de débogage Android : interdit pour une version de production"; fi
  # Updates only install over the existing app when the certificate never changes.
  if [ "$TARGET" = tv ]; then CERT_FILE=masterzone-tv-certificate.sha256; else CERT_FILE=masterzone-android-certificate.sha256; fi
  test -s "$HERE/../../signing/$CERT_FILE" || fail "certificat attendu non configuré"
  EXPECTED_CERT=$(tr -d ' \n' < "$HERE/../../signing/$CERT_FILE")
  ACTUAL_CERT=$(grep -m1 'certificate SHA-256 digest' "$WORK/signature.txt" | sed -E 's/.*: //')
  [ "$ACTUAL_CERT" = "$EXPECTED_CERT" ] || fail "certificat $ACTUAL_CERT différent du certificat MasterZone $EXPECTED_CERT : les mises à jour seraient refusées"
  grep -q 'Verified using v2 scheme (APK Signature Scheme v2): true' "$WORK/signature.txt" || fail "signature v2 absente"
  echo "- Signature : $(grep -m1 'certificate DN' "$WORK/signature.txt" || true) / $(grep -m1 'certificate SHA-256' "$WORK/signature.txt" || true)" >> "$REPORT"
  SIGNATURE=signé
else
  [ "${ALLOW_UNSIGNED:-0}" = 1 ] || fail "signature absente ou invalide : distribution interdite"
  echo "- Signature : aucune (APK non signé, à signer avec la clé MasterZone avant distribution)" >> "$REPORT"
  SIGNATURE="non signé"
fi
echo >> "$REPORT"
echo "::notice title=APK vérifié ($NAME)::$PACKAGE $VERSION_NAME ($VERSION_CODE), $SIGNATURE — $SIZE octets — SHA-256 $SHA — bundle Hermes $BUNDLE_SIZE octets ($BUNDLE_SHA)"
rm -rf "$WORK"
