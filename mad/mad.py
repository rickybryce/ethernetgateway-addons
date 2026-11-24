#!/usr/bin/env python3
# M.A.D. -- Mutual Assured Destruction.  A Cold War strategy simulation for
# the Ethernet Gateway: choose a side, name the enemy's cities, and watch the
# scores climb.  Standard library only, so it runs wherever Python 3 does.
#
# Optional settings live in settings.conf in this folder (not shipped, so an
# update never replaces it):
#     baud = 600        # how fast the text types out; 0 = full speed
#     missiles = 6      # missiles each side has
import os
import random
import sys
import time
import difflib

# ---------------------------------------------------------------- settings

def read_settings():
    s = {"baud": 600, "missiles": 6}
    try:
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "settings.conf")) as f:
            for line in f:
                line = line.split("#", 1)[0].strip()
                if "=" not in line:
                    continue
                k, v = (x.strip().lower() for x in line.split("=", 1))
                if k in s and v.isdigit():
                    s[k] = int(v)
    except OSError:
        pass
    s["baud"] = min(s["baud"], 115200)
    s["missiles"] = max(1, min(s["missiles"], 20))
    return s

SETTINGS = read_settings()
COLOR = os.environ.get("EG_COLOR") == "1"
def columns():
    try:
        return int(os.environ.get("EG_COLUMNS") or 80)
    except ValueError:
        return 80

WIDTH = max(32, min(columns(), 80)) - 1

GREEN, YELLOW, RED, WHITE, OFF = (
    ("\033[32m", "\033[33m", "\033[31m", "\033[37m", "\033[0m") if COLOR else ("",) * 5
)

# ---------------------------------------------------------------- output

def out(text="", color=GREEN, end="\n"):
    """Type text out at the configured baud rate (ten bits a character)."""
    delay = 10.0 / SETTINGS["baud"] if SETTINGS["baud"] else 0
    # Paced against the clock, not by summing sleeps: a sleep can run long
    # (on Windows before Python 3.11 it rounds up to ~15 ms), and the next
    # character then simply waits less.
    due = time.monotonic()
    sys.stdout.write(color)
    for i, chunk in enumerate((text, end)):
        if i == 1:
            sys.stdout.write(OFF)
        for ch in chunk:
            sys.stdout.write(ch)
            if delay:
                sys.stdout.flush()
                due += delay
                wait = due - time.monotonic()
                if wait > 0:
                    time.sleep(wait)
    sys.stdout.flush()

def pause(seconds):
    if SETTINGS["baud"]:
        time.sleep(seconds)

class Quit(Exception):
    """Q typed at any prompt: leave the game."""

def ask(prompt):
    out(prompt, YELLOW, end="")
    line = sys.stdin.readline()
    if not line:            # the caller left
        sys.exit(0)
    line = line.strip()
    if line.upper() in ("Q", "QUIT"):
        raise Quit
    return line

def n(x):
    return "{:,}".format(x)

# ---------------------------------------------------------------- the map
# Approximate early-1980s metropolitan populations.  Names are as they were
# in 1983; today's names are accepted too (see ALIASES).

USA = {
    "NEW YORK": 9120000, "LOS ANGELES": 7478000, "CHICAGO": 7104000,
    "PHILADELPHIA": 4717000, "DETROIT": 4353000, "SAN FRANCISCO": 3251000,
    "WASHINGTON": 3060000, "DALLAS": 2975000, "HOUSTON": 2905000,
    "BOSTON": 2763000, "ST LOUIS": 2356000, "PITTSBURGH": 2264000,
    "BALTIMORE": 2174000, "MINNEAPOLIS": 2114000, "ATLANTA": 2030000,
    "CLEVELAND": 1899000, "SAN DIEGO": 1862000, "MIAMI": 1626000,
    "DENVER": 1621000, "SEATTLE": 1607000, "TAMPA": 1569000,
    "PHOENIX": 1509000, "CINCINNATI": 1401000, "MILWAUKEE": 1397000,
    "KANSAS CITY": 1327000, "SAN JOSE": 1295000, "BUFFALO": 1243000,
    "PORTLAND": 1243000, "NEW ORLEANS": 1187000, "INDIANAPOLIS": 1167000,
    "COLUMBUS": 1093000, "SAN ANTONIO": 1072000, "SACRAMENTO": 1014000,
    "SALT LAKE CITY": 936000, "MEMPHIS": 913000, "LOUISVILLE": 906000,
    "NASHVILLE": 851000, "OKLAHOMA CITY": 834000, "NORFOLK": 807000,
    "HONOLULU": 763000, "OMAHA": 570000, "ALBUQUERQUE": 485000,
    "LAS VEGAS": 463000, "COLORADO SPRINGS": 317000, "ANCHORAGE": 174000,
}

USSR = {
    "MOSCOW": 8400000, "LENINGRAD": 4800000, "KIEV": 2400000,
    "TASHKENT": 1900000, "BAKU": 1600000, "KHARKOV": 1500000,
    "MINSK": 1400000, "GORKY": 1400000, "NOVOSIBIRSK": 1400000,
    "SVERDLOVSK": 1300000, "KUIBYSHEV": 1200000, "TBILISI": 1100000,
    "DNEPROPETROVSK": 1100000, "YEREVAN": 1100000, "ODESSA": 1100000,
    "CHELYABINSK": 1100000, "OMSK": 1100000, "DONETSK": 1000000,
    "PERM": 1000000, "KAZAN": 1000000, "UFA": 1000000,
    "ALMA-ATA": 1000000, "ROSTOV": 1000000, "VOLGOGRAD": 970000,
    "SARATOV": 890000, "RIGA": 870000, "ZAPOROZHYE": 850000,
    "KRASNOYARSK": 850000, "VORONEZH": 850000, "LVOV": 730000,
    "KRIVOY ROG": 680000, "YAROSLAVL": 620000, "KARAGANDA": 600000,
    "VLADIVOSTOK": 590000, "IRKUTSK": 580000, "KHABAROVSK": 560000,
    "VILNIUS": 520000, "TALLINN": 460000, "MURMANSK": 400000,
    "ARKHANGELSK": 400000, "KALININGRAD": 380000, "SEVASTOPOL": 320000,
    "PETROPAVLOVSK": 240000,
}

ALIASES = {
    "ST PETERSBURG": "LENINGRAD", "SAINT PETERSBURG": "LENINGRAD",
    "KYIV": "KIEV", "KHARKIV": "KHARKOV", "NIZHNY NOVGOROD": "GORKY",
    "YEKATERINBURG": "SVERDLOVSK", "SAMARA": "KUIBYSHEV", "ALMATY": "ALMA-ATA",
    "DNIPRO": "DNEPROPETROVSK", "ZAPORIZHZHIA": "ZAPOROZHYE", "LVIV": "LVOV",
    "KRYVYI RIH": "KRIVOY ROG", "ROSTOV-ON-DON": "ROSTOV",
    "NYC": "NEW YORK", "LA": "LOS ANGELES", "DC": "WASHINGTON",
    "SAINT LOUIS": "ST LOUIS", "ST. LOUIS": "ST LOUIS", "SF": "SAN FRANCISCO",
}

SIDES = {"1": ("UNITED STATES", USA), "2": ("SOVIET UNION", USSR)}

# ---------------------------------------------------------------- game

def find_city(typed, cities):
    """The city meant by `typed`, or None.  Close spellings count."""
    t = " ".join(typed.upper().replace(".", "").split())
    t = ALIASES.get(t, t)
    if t in cities:
        return t
    starts = [c for c in cities if c.startswith(t)] if len(t) >= 3 else []
    if len(starts) == 1:
        return starts[0]
    close = difflib.get_close_matches(t, list(cities), n=1, cutoff=0.75)
    return close[0] if close else None

def list_cities(cities, gone):
    left = sorted((c for c in cities if c not in gone), key=lambda c: -cities[c])
    col = 19
    per_row = max(1, (WIDTH + 1) // col)
    for i in range(0, len(left), per_row):
        out("".join(c.ljust(col) for c in left[i:i + per_row]).rstrip())

def strike(attacker, target, pop, color):
    out()
    out("{} LAUNCH: {}".format(attacker, target), color)
    pause(0.4)
    for t in ("T-30", "T-20", "T-10"):
        out("  " + t + " ...", WHITE)
        pause(0.3)
    out("  IMPACT. " + target + " DESTROYED.", RED)
    out("  POPULATION: " + n(pop), color)

def enemy_choice(cities, gone, last_hit):
    left = [c for c in cities if c not in gone]
    if not left:
        return None
    left.sort(key=lambda c: -cities[c])
    # A heavy blow is answered in kind: the biggest cities left.
    if last_hit >= 3000000:
        return random.choice(left[:3])
    # Otherwise mostly large cities, with a little doubt about which.
    weights = [cities[c] for c in left]
    return random.choices(left, weights=weights, k=1)[0]

def scoreboard(names, score):
    out()
    out("SCORE", WHITE)
    for side in (0, 1):
        out("  {:<15}{:>14}".format(names[side], n(score[side])))

def stood_down(fired):
    out()
    if fired == 0:
        out("NO LAUNCH ORDERED.", WHITE)
        pause(0.5)
        out("ENEMY FORCES STANDING DOWN.", WHITE)
        pause(0.5)
        out("DETERRENCE HOLDS. CASUALTIES: 0.", YELLOW)
        out()
        out("OF EVERY ENDING, THIS IS THE ONLY")
        out("ONE WITH A WINNER.")
    else:
        out("CEASE-FIRE ORDERED.", WHITE)
        pause(0.5)
        out("THE ENEMY FIRES ONE LAST TIME,", WHITE)
        out("THEN STANDS DOWN.", WHITE)

def final(names, score):
    out()
    out("=" * min(WIDTH, 38), WHITE)
    out("FINAL TALLY", WHITE)
    for side in (0, 1):
        out("  {:<15}{:>14}".format(names[side], n(score[side])))
    out("  {:<15}{:>14}".format("COMBINED", n(score[0] + score[1])), RED)
    out()
    pause(1.0)
    out("WINNER: NONE", YELLOW)
    pause(1.0)
    out()
    out("A HIGHER SCORE IS ONLY MORE DEAD.")
    out("IN THIS EXCHANGE, AS IN EVERY")
    out("EXCHANGE, BOTH SIDES LOSE.")

def play():
    sys.stdout.write("\033[2J\033[H")
    out("M.A.D. STRATEGIC SIMULATION", WHITE)
    out("MUTUAL ASSURED DESTRUCTION")
    out()
    pause(0.5)
    out("WHICH SIDE DO YOU COMMAND?")
    out("  1  UNITED STATES")
    out("  2  SOVIET UNION")
    while True:
        pick = ask("SIDE: ")
        if pick in SIDES:
            break
        out("ENTER 1 OR 2, OR Q TO QUIT.")
    me = SIDES[pick]
    them = SIDES["2" if pick == "1" else "1"]
    names = (me[0], them[0])
    gone = set()
    score = [0, 0]
    missiles = SETTINGS["missiles"]
    out()
    out("YOU COMMAND THE " + me[0] + ".")
    out("EACH SIDE HAS {} MISSILES.".format(missiles))
    out("NAME AN ENEMY CITY TO TARGET.")
    out("? LISTS TARGETS. STAND DOWN ENDS IT.")
    out("Q QUITS.")
    fired = 0
    while fired < missiles:
        out()
        typed = ask("TARGET ({} LEFT): ".format(missiles - fired))
        if not typed:
            continue
        word = typed.upper()
        if word in ("?", "LIST", "HELP"):
            list_cities(them[1], gone)
            continue
        if word in ("STAND DOWN", "STANDDOWN", "PEACE"):
            stood_down(fired)
            if fired == 0:
                return
            target = enemy_choice(me[1], gone, 0)
            if target:
                gone.add(target)
                score[1] += me[1][target]
                strike(them[0], target, me[1][target], RED)
            break
        city = find_city(typed, them[1])
        if city is None:
            own = find_city(typed, me[1])
            if own:
                out(own + " IS ONE OF YOURS.")
            else:
                out("NO SUCH TARGET. ? LISTS THEM.")
            continue
        if city in gone:
            out(city + " IS ALREADY DESTROYED.")
            continue
        if city.upper() != word:
            out("TARGETING " + city + ".")
        gone.add(city)
        score[0] += them[1][city]
        fired += 1
        strike(me[0], city, them[1][city], GREEN)
        pause(0.8)
        out()
        out("ENEMY LAUNCH DETECTED.", RED)
        target = enemy_choice(me[1], gone, them[1][city])
        if target:
            gone.add(target)
            score[1] += me[1][target]
            strike(them[0], target, me[1][target], RED)
        scoreboard(names, score)
    final(names, score)

def main():
    # A byte that is not UTF-8 (an old terminal's accented letter, a
    # Commodore graphics key) must not end the game with a traceback.
    try:
        sys.stdin.reconfigure(errors="replace")
    except (AttributeError, ValueError):
        pass
    try:
        while True:
            play()
            out()
            if ask("PLAY AGAIN? (Y/N) ").upper()[:1] != "Y":
                break
        out("CONNECTION CLOSED.", WHITE)
    except Quit:
        out()
        out("CONNECTION CLOSED.", WHITE)
    except (BrokenPipeError, KeyboardInterrupt):
        # The caller left mid-line: nothing more to say, and no traceback
        # for the gateway's log when Python flushes on the way out.
        try:
            os.dup2(os.open(os.devnull, os.O_WRONLY), sys.stdout.fileno())
        except OSError:
            pass

if __name__ == "__main__":
    main()
