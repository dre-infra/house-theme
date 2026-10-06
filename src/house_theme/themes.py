"""Date-driven seasonal/holiday themes shared by every dre-infra family app.

Resolution order (most specific wins):
  1. Single days:   New Year's Day 1/1, Valentine's Day 2/14, St. Patrick's
                    Day 3/17, Halloween night 10/31, New Year's Eve 12/31
  2. Whole months:  Feb -> Black History Month, Jun -> Pride,
                    Oct -> Halloween, Dec -> Christmas
  3. Season:        Dec/Jan/Feb winter, Mar-May spring, Jun-Aug summer,
                    Sep-Nov fall (in practice: Jan, Mar-May, Jul-Aug, Sep, Nov)

Birthdays (from the BIRTHDAYS env var, see birthdays.py) layer on top of
whatever theme the date resolves to: the birthday greeting goes first in
the banner and cake/balloons join the particles.

Colors: every theme sets its own full accent set, so each holiday/season
reads as itself (brown + orange means fall and only fall):
  primary    -> --accent       links, buttons, banner
  secondary  -> --accent-2     secondary highlights
  soft       -> --accent-soft  pale tint behind chips/pills (light mode)
Neutrals (background, text, borders) stay with each app's style.css, so
readability and dark mode are untouched. Dark-mode accents and the text
color that sits on an accent are derived in colors.py, not hand-kept.

`emojis: []` = no particle effect (Black History Month, on purpose).
`direction` is 'fall' or 'rise'.
"""

THEMES = {
    # ---- seasons -------------------------------------------------------
    'winter': {
        'label': 'Winter',
        'primary': '#3a7ca5', 'secondary': '#9fb4c7', 'soft': '#e3eef6',
        'emojis': ['❄️'],
        'direction': 'fall',
        'banner': None,
    },
    'spring': {
        'label': 'Spring',
        'primary': '#4c9a2a', 'secondary': '#e07a9f', 'soft': '#eaf5e1',
        'emojis': ['🌸', '🌷', '🌼'],
        'direction': 'fall',
        'banner': None,
    },
    'summer': {
        'label': 'Summer',
        'primary': '#0f8b8d', 'secondary': '#f2b705', 'soft': '#e0f4f4',
        'emojis': ['☀️', '🌻'],
        'direction': 'rise',
        'banner': None,
    },
    'fall': {
        'label': 'Fall',
        'primary': '#c4570f', 'secondary': '#7a4a24', 'soft': '#f6e6d6',
        'emojis': ['🍁', '🍂', '🍃'],
        'direction': 'fall',
        'banner': None,
    },
    # ---- months --------------------------------------------------------
    'black_history': {
        'label': 'Black History Month',
        'primary': '#b3242e', 'secondary': '#2d6a4f', 'soft': '#f4d9b0',
        'emojis': [],
        'direction': 'fall',
        'banner': 'Black History Month',
    },
    'pride': {
        'label': 'Pride Month',
        'primary': '#e0245e', 'secondary': '#5b8def', 'soft': '#ffe1ea',
        'emojis': ['❤️', '🧡', '💛', '💚', '💙', '💜'],
        'direction': 'fall',
        'banner': '🏳️‍🌈 Pride Month',
    },
    'halloween': {
        'label': 'Halloween',
        # Purple + slime green; orange only shows up in the pumpkins, so
        # October reads as Halloween rather than "more fall".
        'primary': '#6b3fa0', 'secondary': '#7cb518', 'soft': '#ece3f5',
        'emojis': ['🎃', '👻', '🦇', '🕸️'],
        'direction': 'fall',
        'banner': '🎃 Spooky Season',
    },
    'christmas': {
        'label': 'Christmas',
        'primary': '#b3202a', 'secondary': '#1f6f43', 'soft': '#f6e3e3',
        'emojis': ['❄️', '🎄', '🎁', '⭐'],
        'direction': 'fall',
        'banner': '🎄 Merry Christmas',
    },
    # ---- single days ---------------------------------------------------
    'new_years_day': {
        'label': "New Year's Day",
        'primary': '#c9a227', 'secondary': '#1d2b53', 'soft': '#f7f0d8',
        'emojis': ['🎊', '✨', '🥂'],
        'direction': 'fall',
        'banner': '🥂 Happy New Year',
    },
    'valentines': {
        'label': "Valentine's Day",
        'primary': '#c9184a', 'secondary': '#ff8fab', 'soft': '#ffe5ec',
        'emojis': ['💕', '❤️', '💖', '🎈'],
        'direction': 'fall',
        'banner': "💘 Happy Valentine's Day",
    },
    'st_pattys': {
        'label': "St. Patrick's Day",
        'primary': '#1e8a3a', 'secondary': '#d4a017', 'soft': '#e3f4e7',
        'emojis': ['☘️', '🍀', '🪙'],
        'direction': 'fall',
        'banner': "☘️ Happy St. Patrick's Day",
    },
    'halloween_night': {
        'label': 'Halloween',
        'primary': '#6b3fa0', 'secondary': '#7cb518', 'soft': '#ece3f5',
        'emojis': ['🦇', '🎃', '🦇', '🍬', '👻'],
        'direction': 'fall',
        'banner': '🦇 Happy Halloween 🎃',  # dark banner, see house-theme.css
    },
    'new_years_eve': {
        'label': "New Year's Eve",
        'primary': '#c9a227', 'secondary': '#1d2b53', 'soft': '#f7f0d8',
        'emojis': ['🎉', '🎆', '✨'],
        'direction': 'fall',
        'banner': "🎆 Happy New Year's Eve",
    },
}

SINGLE_DAYS = {
    (1, 1): 'new_years_day',
    (2, 14): 'valentines',
    (3, 17): 'st_pattys',
    (10, 31): 'halloween_night',
    (12, 31): 'new_years_eve',
}

MONTHS = {
    2: 'black_history',
    6: 'pride',
    10: 'halloween',
    12: 'christmas',
}

SEASONS = {
    12: 'winter', 1: 'winter', 2: 'winter',
    3: 'spring', 4: 'spring', 5: 'spring',
    6: 'summer', 7: 'summer', 8: 'summer',
    9: 'fall', 10: 'fall', 11: 'fall',
}


def theme_key_for(day):
    """Map a date to a THEMES key (single day > month > season)."""
    return (SINGLE_DAYS.get((day.month, day.day))
            or MONTHS.get(day.month)
            or SEASONS[day.month])
