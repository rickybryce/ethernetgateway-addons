#!/bin/sh
# Lines are kept under 38 characters so they fit a Commodore 64.
echo "Hello from an add-on!"
echo
echo "The gateway told me:"
echo "  terminal $EG_TERMINAL, $EG_COLUMNS x $EG_ROWS"
echo "  colour   $EG_COLOR, input $EG_INPUT"
echo "  from     ${EG_REMOTE_ADDR:-this machine}"
echo "  over     $EG_CONNECTION"
echo "  gateway  $EG_GATEWAY_VERSION"
echo
printf "What is your name? "
read -r name
echo "Nice to meet you, ${name:-stranger}."
