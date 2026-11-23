# Ethernet Gateway add-ons

Add-ons for [Ethernet Gateway](https://github.com/rickybryce/ethernetgateway):
programs a gateway offers its callers from the Second Menu (`2`, then `A`),
the way a BBS offered doors.

| Folder | What it is |
|---|---|
| `hello` | Shows the `EG_*` values the gateway passes, then reads a typed line. The place to start when writing your own. |
| `guess` | Guess the number: a small game with ANSI colour that also works on a Commodore 64. |

## Installing

The gateway's setup wizard can download these for you ("Download the Ethernet
Gateway add-ons").  It fetches the exact versions its own release was built
with and checks each file's SHA-256, so a change here reaches a gateway only
through a gateway release.

By hand: copy a folder into `ethernetgateway-data/AddOns/` beside the gateway.
On Linux and macOS the script must be executable (`chmod +x`).  It appears in
the list the next time it is opened; no restart is needed.

## Writing one

Each add-on is a folder with an `addon.conf` and the program it names.  Each
example here has a POSIX shell script for Linux and macOS and a `.cmd` for
Windows, chosen by `command` and `command_windows`.  The gateway's user manual,
"Writing an add-on", lists every `addon.conf` key and every `EG_*` value.

Add-ons run as the same user as the gateway, with its rights.

## Licence

GPL-3.0, the same as Ethernet Gateway.
