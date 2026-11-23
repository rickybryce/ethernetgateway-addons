#!/bin/sh
# Colour only when the caller has it (EG_COLOR=1).  Plain ANSI: on a
# Commodore 64 the gateway turns these into PETSCII colours.
if [ "$EG_COLOR" = 1 ]; then
    Y=$(printf '\033[1;33m'); G=$(printf '\033[1;32m')
    C=$(printf '\033[1;36m'); N=$(printf '\033[0m')
else
    Y= G= C= N=
fi
secret=$(awk 'BEGIN { srand(); print int(rand() * 100) + 1 }')
tries=0
echo "${Y}GUESS THE NUMBER${N}"
echo
echo "I am thinking of a number from"
echo "1 to 100. Q gives up."
echo
while :; do
    printf '%sYour guess:%s ' "$C" "$N"
    read -r guess || exit 0
    case $guess in
        q|Q) echo "It was $secret."; exit 0 ;;
        ''|*[!0-9]*) echo "Numbers only, please."; continue ;;
    esac
    tries=$((tries + 1))
    if [ "$guess" -lt "$secret" ]; then
        echo "Higher."
    elif [ "$guess" -gt "$secret" ]; then
        echo "Lower."
    else
        echo "${G}Yes! $secret in $tries tries.${N}"
        exit 0
    fi
done
