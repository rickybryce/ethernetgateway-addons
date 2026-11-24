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
with and checks each file's SHA-256.

Later, **Check for add-ons** (`C` on the gateway's Add-Ons list, or the button in
its web and desktop Add-Ons settings) offers what is new here, or newer than the
copy installed, and suits that gateway's version (`min_gateway`/`max_gateway`).
It reads `catalogue.txt`, which is signed (`catalogue.sig`); a gateway refuses a
list whose signature does not match the key built into it.

By hand: copy a folder into `ethernetgateway-data/AddOns/` beside the gateway.
On Linux and macOS the script must be executable (`chmod +x`).  It appears in
the list the next time it is opened; no restart is needed.

## Writing one

Each add-on is a folder with an `addon.conf` and the program it names.  Each
example here has a POSIX shell script for Linux and macOS and a `.cmd` for
Windows, chosen by `command` and `command_windows`.  The gateway's user manual,
"Writing an add-on", lists every `addon.conf` key and every `EG_*` value.

Add-ons run as the same user as the gateway, with its rights.

## Changing one (maintainers)

1. Edit the add-on and raise its `version` in `addon.conf`; commit.
2. Run `tools/make-catalogue.sh`.  It lists every committed add-on with each
   file's size and SHA-256 and signs the list with the private key (kept off
   this repository: `~/.config/ethernetgateway/addons-signing-key.pem`, or
   `EGW_ADDONS_KEY`).
3. Commit `catalogue.txt` and `catalogue.sig` and push.

## Licence

GPL-3.0, the same as Ethernet Gateway.
