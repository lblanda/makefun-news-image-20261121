# stories.py — the world news of Saturday 21 November 2026, as reported that day.
#
# Every fact below was checked against reporting published on 21 November
# 2026 (AP, Reuters, AFP via Gulf News, Xinhua, The Hindu, One Turn's
# daily digest, Standard Topic's world archive). The image renders only
# these baked-in facts; the program fetches nothing at run time.

DATE_LINE = "SATURDAY 21 NOVEMBER 2026"
MASTHEAD = "THE WORLD IN ONE DAY"
TAGLINE = "The day's news, in one picture"

# Lead story: Russia's biggest overnight barrage of the war so far, and
# missiles coming down on Polish soil.
LEAD = {
    "kicker": "KYIV, UKRAINE",
    "headline": "RUSSIA RAINS FIRE",
    "subhead": "MISSILES LAND IN POLAND",
    "body": [
        "Russia fires more than 400 drones and",
        "110 missiles at Ukraine overnight, killing",
        "at least 8 in Kyiv, wrecking bridges and",
        "rail stations and cutting power, water and",
        "heat in the capital. Two missiles and a",
        "suspected drone come down in Poland, and",
        "Prime Minister Tusk calls it a deliberate",
        "provocation.",
    ],
}

# Second row, left: the world court rules on the Rohingya.
COURT = {
    "kicker": "THE HAGUE",
    "headline": "MYANMAR GUILTY",
    "headline2": "OF GENOCIDE",
    "body": [
        "The International Court of Justice finds",
        "Myanmar responsible for genocide against",
        "the Rohingya, a landmark ruling for the",
        "stateless minority driven from their homes.",
    ],
}

# Second row, right: the Strait of Hormuz flashpoint.
HORMUZ = {
    "kicker": "STRAIT OF HORMUZ",
    "headline": "IRAN DOWNS",
    "headline2": "US DRONE",
    "body": [
        "Iran says it shot down a US MQ-9 drone",
        "over the strait, its 58th, as two tankers",
        "are attacked nearby and Saudi strikes kill",
        "41 in Yemen. Trump says Iran wants a deal",
        "on terms Washington will not accept.",
    ],
}

# Third row, left: the AI sell-off drags Wall Street down.
MARKETS = {
    "kicker": "NEW YORK",
    "headline": "AI ROUT HITS",
    "headline2": "WALL STREET",
    "body": [
        "US stocks fall 3.7% as the sell-off in AI",
        "and chip shares deepens, pushing the S&P",
        "500 and the Dow into correction territory",
        "as bubble fears spread through markets.",
    ],
}

# Third row, right: the climate summit runs into overtime.
CLIMATE = {
    "kicker": "ANTALYA, TURKIYE",
    "headline": "COP31 RUNS",
    "headline2": "PAST DEADLINE",
    "body": [
        "Climate talks run past their deadline as",
        "nearly 200 nations fail to agree on fossil",
        "fuels. Pacific states call it the worst",
        "COP ever as the summit grinds into overtime.",
    ],
}

# Bottom strip: short briefs, all reported on 21 November 2026. Rendered
# as one wrapped line group after the "ALSO TODAY:" label.
BRIEFS_TEXT = (
    "UK and EU sign biggest post-Brexit deals  •  Gen Z protests spread "
    "across 25 European countries  •  Pancreatic cancer pill shows promise "
    "•  Lewis Pugh swims the Strait of Hormuz  •  Wildberries chief quits"
)
