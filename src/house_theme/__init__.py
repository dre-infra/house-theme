"""house-theme: shared date-driven seasonal/holiday theme for Flask apps.

Usage in an app:

    from house_theme import init_theme
    init_theme(app)

and in the base template (after the app's own stylesheet):

    <head>  ... {% include 'house_theme/head.html' %}
    <body>  ... {% include 'house_theme/banner.html' %}   (where the banner goes)
            ... {% include 'house_theme/scripts.html' %}  (end of body)

`theme` is then available in every template (theme.key, theme.label,
theme.banner, ...).

Settings (env vars, read once at startup):
    BIRTHDAYS         MM-DD:Name pairs, comma-separated (see birthdays.py)
    THEME_TZ          IANA zone for "today" (default America/Phoenix;
                      containers run UTC, which flipped themes at 5 PM)
    HOUSE_THEME_DATE  YYYY-MM-DD to preview a date's theme (leave unset)
"""

import logging
import os
from datetime import date, datetime
from zoneinfo import ZoneInfo

from flask import Blueprint

from .birthdays import birthday_banner, birthday_names, parse_birthdays
from .colors import palette
from .themes import THEMES, theme_key_for

__version__ = '1.2.0'
__all__ = ['init_theme', 'get_active_theme', 'parse_birthdays', 'THEMES']

log = logging.getLogger(__name__)

BIRTHDAY_EMOJIS = ['🎂', '🎈']


def today_in(tz_name):
    return datetime.now(ZoneInfo(tz_name)).date()


def get_active_theme(today=None, birthdays=None):
    """Resolve a date (default: today) to a theme dict for the templates.

    `birthdays` is the dict from parse_birthdays(). On a birthday the
    greeting goes first in the banner, ahead of any holiday banner.
    """
    today = today or date.today()
    key = theme_key_for(today)
    base = THEMES[key]
    light, dark = palette(base)

    theme = {
        'key': key,
        'label': base['label'],
        # Plain hex values, for places CSS variables can't reach (favicons).
        'accent': light['--accent'],
        'accent2': light['--accent-2'],
        'emojis': list(base['emojis']),
        'direction': base['direction'],
        'light': light,
        'dark': dark,
        'birthday': False,
    }

    holiday_banner = base['banner']
    bday = birthday_banner(birthday_names(today, birthdays or {}))
    if bday:
        theme['birthday'] = True
        theme['banner'] = f'{bday} · {holiday_banner}' if holiday_banner else bday
        theme['emojis'] += BIRTHDAY_EMOJIS
    else:
        theme['banner'] = holiday_banner
    return theme


SCHEMES = ('auto', 'light', 'dark')


def init_theme(app, scheme='auto'):
    """Register the static files/templates and inject `theme` into every
    template. Settings can also be set on app.config with the same names.

    scheme: 'auto' follows the device's light/dark setting; 'dark' or
    'light' always uses that palette (for apps designed in one mode only).
    """
    if scheme not in SCHEMES:
        raise ValueError(f'scheme must be one of {SCHEMES}, not {scheme!r}')

    def setting(name, default=None):
        return app.config.get(name) or os.environ.get(name) or default

    birthdays = parse_birthdays(setting('BIRTHDAYS'))
    tz_name = setting('THEME_TZ', 'America/Phoenix')
    ZoneInfo(tz_name)  # fail at startup, not per request, on a bad zone

    preview = (setting('HOUSE_THEME_DATE') or '').strip()
    preview_date = None
    if preview:
        try:
            preview_date = date.fromisoformat(preview)
        except ValueError:
            log.warning('house_theme: ignoring HOUSE_THEME_DATE=%r '
                        '(expected YYYY-MM-DD)', preview)
    if preview_date:
        log.warning('house_theme: HOUSE_THEME_DATE=%s set -- every page shows '
                    "that date's theme. Unset it when done previewing.", preview)

    bp = Blueprint('house_theme', __name__,
                   static_folder='static', static_url_path='/_house-theme',
                   template_folder='templates')
    app.register_blueprint(bp)

    @app.context_processor
    def inject_house_theme():
        day = preview_date or today_in(tz_name)
        theme = get_active_theme(day, birthdays)
        theme['scheme'] = scheme
        return {'theme': theme}

    return app
