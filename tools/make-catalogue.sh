#!/bin/sh
# Rebuild catalogue.txt from the committed add-ons and sign it (catalogue.sig).
#
# Ethernet Gateway's "check for new add-ons" reads these two files from the
# main branch and refuses the list unless the signature matches the public key
# built into the gateway.  Run this after committing a change to any add-on,
# then commit catalogue.txt and catalogue.sig and push.
#
# The private key never goes in this repository.  Default location:
#   ~/.config/ethernetgateway/addons-signing-key.pem   (or set EGW_ADDONS_KEY)
set -eu
KEY=${EGW_ADDONS_KEY:-$HOME/.config/ethernetgateway/addons-signing-key.pem}
cd "$(git rev-parse --show-toplevel)"
[ -r "$KEY" ] || { echo "no signing key at $KEY" >&2; exit 1; }
# The list describes what is committed: raw.githubusercontent.com serves the
# committed bytes, so an uncommitted edit would be listed with the wrong hash.
if ! git diff --quiet HEAD -- . ':!catalogue.txt' ':!catalogue.sig'; then
  echo "commit your add-on changes first" >&2; exit 1
fi
hash() { git show "HEAD:$1" | sha256sum | cut -d' ' -f1; }
size() { git cat-file -s "HEAD:$1"; }
val() { git show "HEAD:$1/addon.conf" | tr -d '\r' \
        | sed -n "s/^[[:space:]]*$2[[:space:]]*=[[:space:]]*//p" | tail -n 1; }
tmp=$(mktemp)
{
  echo "# Ethernet Gateway add-on list, made by tools/make-catalogue.sh.  Do not edit."
  echo "egw-addons 1"
  for d in $(git ls-files | grep / | cut -d/ -f1 | sort -u); do
    git cat-file -e "HEAD:$d/addon.conf" 2>/dev/null || continue
    v=$(val "$d" version); min=$(val "$d" min_gateway); max=$(val "$d" max_gateway)
    printf 'addon\t%s\t%s\t%s\t%s\n' "$d" "${v:--}" "${min:--}" "${max:--}"
    git ls-files -s -- "$d" | while read -r mode _ _ path; do
      case "$path" in
        */*/*) echo "$path: add-on files must sit directly in the add-on's folder" >&2; exit 1 ;;
        */.*) echo "$path: hidden files are not downloaded" >&2; exit 1 ;;
      esac
      x=0; [ "$mode" = 100755 ] && x=1
      printf 'file\t%s\t%s\t%s\t%s\n' "$path" "$(size "$path")" "$(hash "$path")" "$x"
    done
  done
} > "$tmp"
mv "$tmp" catalogue.txt
openssl pkeyutl -sign -inkey "$KEY" -rawin -in catalogue.txt | od -An -v -tx1 | tr -d ' \n' > catalogue.sig
echo >> catalogue.sig
echo "catalogue.txt + catalogue.sig written:"
grep '^addon' catalogue.txt
