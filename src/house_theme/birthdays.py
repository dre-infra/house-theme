"""Birthday banners from the BIRTHDAYS env var.

Format: comma-separated MM-DD:Name pairs, e.g.
    BIRTHDAYS=02-14:Name,07-03:Other Name

Same date twice -> one banner naming both ("Name & Other"). A 02-29
birthday shows on 02-28 in non-leap years. Malformed entries are skipped
(and logged) so a typo in .env can never take a page down.
"""

import calendar
import logging

log = logging.getLogger(__name__)


def parse_birthdays(raw):
    """'02-14:Name,07-03:Other' -> {(2, 14): ['Name'], (7, 3): ['Other']}"""
    result = {}
    for entry in (raw or '').split(','):
        entry = entry.strip()
        if not entry:
            continue
        try:
            when, name = entry.split(':', 1)
            month, day = (int(x) for x in when.strip().split('-'))
            name = name.strip()
            if not name or not (1 <= month <= 12) or not (1 <= day <= 31):
                raise ValueError
        except ValueError:
            log.warning('house_theme: skipping malformed BIRTHDAYS entry %r '
                        '(expected MM-DD:Name)', entry)
            continue
        result.setdefault((month, day), []).append(name)
    return result


def birthday_names(day, birthdays):
    names = list(birthdays.get((day.month, day.day), []))
    if (day.month, day.day) == (2, 28) and not calendar.isleap(day.year):
        names += birthdays.get((2, 29), [])
    return names


def birthday_banner(names):
    if not names:
        return None
    if len(names) == 1:
        who = names[0]
    else:
        who = ', '.join(names[:-1]) + ' & ' + names[-1]
    return f'Happy Birthday, {who}! 🎂'
