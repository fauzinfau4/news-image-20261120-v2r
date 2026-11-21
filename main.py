"""News-image entry for make.fun competition news-image-20261120.

A newspaper-style collage summing up Friday 20 November 2026.
Drawn from scratch with draw.py (pure stdlib PNG + 5x7 font).
Writes /output/entry.png (or the path in argv[1]).
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from draw import Canvas, encode_png, text_width, wrap_text
from draw import icon_kyiv, icon_scales, icon_market

W, H = 1024, 1024

# ---------------------------------------------------------------- palette
PAPER = (247, 243, 232)
INK = (26, 26, 26)
MUTED = (88, 84, 74)
NAVY = (20, 33, 61)
RED = (176, 58, 46)
CARD = (255, 255, 255)
BORDER = (214, 208, 194)
LIGHT = (235, 230, 218)
WHITE = (255, 255, 255)
CREAM = (245, 235, 205)

REGIONS = [
    ("EUROPE", (46, 95, 163)),
    ("AMERICAS", (14, 124, 123)),
    ("ASIA-PACIFIC", (217, 123, 41)),
    ("MIDDLE EAST", (169, 50, 38)),
    ("AFRICA", (46, 125, 50)),
    ("SCIENCE & SPORT", (108, 52, 131)),
]
REGION_COLOR = dict(REGIONS)

# ---------------------------------------------------------------- stories
# Heroes: (kicker, headline, standfirst, icon)
HEROES = [
    ("KYIV, UKRAINE",
     "RUSSIA HITS KYIV WITH 400 DRONES AND 110 MISSILES",
     "Three bridges struck; missiles land in Poland. Ukraine hits the Kerch Bridge in reply.",
     "kyiv"),
    ("THE HAGUE, NETHERLANDS",
     "UN COURT: MYANMAR COMMITTED GENOCIDE",
     "First time the world court has held a state responsible for genocide, against the Rohingya.",
     "scales"),
    ("MARKETS",
     "AI SELL-OFF DRAGS STOCKS INTO CORRECTION",
     "S&P 500 falls 3.7%; Nikkei drops 5.1%; Nasdaq erases its 2026 gains.",
     "market"),
]

# Briefs: (headline, sub) grouped by region, in display order.
BRIEFS = {
    "EUROPE": [
        ("EU-UK LANDMARK DEAL",
         "Youth mobility, trade and energy agreed at the Brussels summit."),
        ("DENMARK EXPELS ATTACHE",
         "Defence attache given seven days to leave over an alleged plot to kill a rapper."),
        ("GERMANY REJECTS YALTA",
         "Merz: no deal on Europe's future without Europeans at the table."),
        ("ESTONIA SHUTS BORDER",
         "Five road crossings with Russia close from 1 December after sabotage."),
        ("MILLION STRIKE IN ITALY",
         "Workers and students march against the 2027 budget."),
        ("PARIS POLICE JAILED",
         "Officers sentenced for the 2020 beating of producer Michel Zecler."),
    ],
    "AMERICAS": [
        ("TRUMP DEFENDS PUTIN",
         "After the Shenzhen summit, the three leaders pledge more nuclear-risk talks."),
        ("TRUMP THREATENS AI TAX",
         "US firms building data centres abroad face a tremendous tax."),
        ("SENATE PASSES ENERGY",
         "Bipartisan reform speeds up permits for energy projects and data centres."),
        ("CYBER CHIEF REPLACED",
         "Kirsten Davies tapped after outages rattled companies and agencies."),
        ("JEFFRIES FOR SPEAKER",
         "House Democrats pick him; he would be the first Black speaker."),
        ("14 IN TRAIN THEFT RING",
         "California freight-train ring stole 22.5m dollars in goods."),
    ],
    "ASIA-PACIFIC": [
        ("CHIP SALES HALTED",
         "TSMC and Samsung halt advanced chip sales after new US export curbs."),
        ("JAPAN INFLATION AT 2.2%",
         "Consumer prices reinforce expectations of another rate rise."),
        ("JAPAN EYES NUCLEAR SUBS",
         "Tokyo to fund a study of nuclear-powered boats."),
        ("BLOOMBERG REPORTER OUT",
         "Annmarie Hordern kept out of the summit over a question."),
        ("US-CHINA AI ARMS DEAL",
         "Trump and Xi: humans must stay in charge of AI weapons decisions."),
        ("XI HAILS AUSTRALIA TIES",
         "China's leader praises a turnaround in relations with Canberra."),
    ],
    "MIDDLE EAST": [
        ("HORMUZ WAR CHOKES OIL",
         "US blockade tightens; tankers burn; IEA calls it the largest energy shock on record."),
        ("HOUTHI FIRE AT RIYADH",
         "Saudi-led coalition shoots down three ballistic missiles; third night of alerts."),
        ("COP31 PAST DEADLINE",
         "Antalya climate summit stalls; draft deal omits fossil fuels."),
        ("IRAQ RETAKES JURF",
         "First time in 12 years."),
        ("UN COUNTS 2840 SHELLS",
         "UNIFIL records 2,840 Israeli shells and 90 airstrikes in south Lebanon in October."),
    ],
    "AFRICA": [
        ("SOMALIA EXPELS ENVOY",
         "Ambassador ordered out in a diplomatic row."),
        ("NIGERIA ENDS JAIL",
         "Jail terms for attempted suicide are abolished."),
        ("17 KILLED IN SHOOTINGS",
         "Separate mass shootings leave 17 dead."),
        ("AFRICA SEEKS CASH",
         "African nations press for funding to flow at COP31."),
    ],
    "SCIENCE & SPORT": [
        ("CANCER PILL WORKS",
         "Trial drug makes pancreatic tumours undetectable in one in 12 patients."),
        ("BAYER DEAL APPROVED",
         "US judge signs off the settlement."),
        ("ALCARAZ BEATS COBOLLI",
         "Injury worries aside, the Spaniard wins in style."),
    ],
}

TOTAL_STORIES = 3 + sum(len(v) for v in BRIEFS.values())


# ---------------------------------------------------------------- layout
def masthead(cv):
    cv.rect(0, 0, W, 100, NAVY)
    cv.rect(0, 100, W, 3, RED)
    cv.text_center(W // 2, 16, "THE WORLD IN ONE DAY", 4, WHITE, bold=True)
    cv.text(20, 66, "FRIDAY EDITION", 2, (180, 190, 215))
    cv.text_center(W // 2, 66, "FRIDAY 20 NOVEMBER 2026", 2, WHITE, bold=True)
    cv.text_right(W - 20, 66, "33 STORIES - 6 REGIONS", 2, (180, 190, 215))


def hero_card(cv, x, y, w, h, kicker, headline, standfirst, icon):
    cv.rect(x, y, w, h, CARD)
    cv.rect(x, y, w, h, BORDER)  # border via outline below
    cv.rect(x, y, w, 1, BORDER)
    cv.rect(x, y + h - 1, w, 1, BORDER)
    cv.rect(x, y, 1, h, BORDER)
    cv.rect(x + w - 1, y, 1, h, BORDER)
    if icon == "kyiv":
        icon_kyiv(cv, x + 1, y + 1, w - 2, 120)
    elif icon == "scales":
        icon_scales(cv, x + 1, y + 1, w - 2, 120)
    else:
        icon_market(cv, x + 1, y + 1, w - 2, 120)
    tx = x + 12
    tw = w - 24
    cy = y + 130
    cv.text(tx, cy, kicker, 2, RED, bold=True)
    cy += 20
    for line in wrap_text(headline, 2, tw)[:3]:
        cv.text(tx, cy, line, 2, INK, bold=True)
        cy += 16
    cy += 4
    for line in wrap_text(standfirst, 2, tw)[:4]:
        cv.text(tx, cy, line, 2, MUTED)
        cy += 15


def chips_row(cv, y):
    items = []
    for name, color in REGIONS:
        n = len(BRIEFS[name])
        label = "%s %d" % (name, n)
        items.append((label, color))
    widths = [text_width(label, 2) + 24 for label, _ in items]
    total = sum(widths) + 8 * (len(items) - 1)
    x = (W - total) // 2
    for (label, color), wd in zip(items, widths):
        cv.rect(x, y, wd, 30, color)
        cv.text_center(x + wd // 2, y + 8, label, 2, WHITE, bold=True)
        x += wd + 8


def region_block(cv, x, y, w, h, name, color, briefs):
    cv.rect(x, y, w, h, CARD)
    cv.rect(x, y, w, 1, BORDER)
    cv.rect(x, y + h - 1, w, 1, BORDER)
    cv.rect(x, y, 1, h, BORDER)
    cv.rect(x + w - 1, y, 1, h, BORDER)
    # header bar
    cv.rect(x + 1, y + 1, w - 2, 26, color)
    cv.text(x + 10, y + 7, name, 2, WHITE, bold=True)
    cv.text_right(x + w - 10, y + 7, "%d STORIES" % len(briefs), 2, (225, 225, 225))
    cy = y + 36
    tx = x + 12
    tw = w - 24
    for headline, sub in briefs:
        # small color tick
        cv.rect(tx, cy + 3, 8, 8, color)
        hx = tx + 14
        hw = tw - 14
        for line in wrap_text(headline, 2, hw)[:2]:
            cv.text(hx, cy, line, 2, INK, bold=True)
            cy += 15
        if sub:
            for line in wrap_text(sub, 1, hw)[:2]:
                cv.text(hx, cy, line, 1, MUTED)
                cy += 8
        cy += 4
        if cy > y + h - 12:
            break


def footer(cv):
    cv.rect(0, 982, W, 1, BORDER)
    cv.text_center(
        W // 2, 994,
        "MARKETS: S&P 500 -3.7%  -  NIKKEI -5.1%  -  NASDAQ ERASES 2026 GAINS",
        2, INK, bold=True)


def build():
    cv = Canvas(W, H, PAPER)
    masthead(cv)
    # hero row
    hx = [14, 349, 684]
    for (kicker, headline, standfirst, icon), x in zip(HEROES, hx):
        hero_card(cv, x, 108, 326, 260, kicker, headline, standfirst, icon)
    chips_row(cv, 378)
    # brief grid: 3 cols x 2 rows
    order = [name for name, _ in REGIONS]
    gx = [14, 349, 684]
    gy = [418, 702]
    for i, name in enumerate(order):
        col = i % 3
        row = i // 3
        region_block(cv, gx[col], gy[row], 326, 274, name,
                     REGION_COLOR[name], BRIEFS[name])
    footer(cv)
    return encode_png(W, H, bytes(cv.px))


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else "/output/entry.png"
    d = os.path.dirname(out)
    if d:
        os.makedirs(d, exist_ok=True)
    data = build()
    with open(out, "wb") as f:
        f.write(data)
    print("wrote %s (%d bytes, %d stories)" % (out, len(data), TOTAL_STORIES))


if __name__ == "__main__":
    main()
