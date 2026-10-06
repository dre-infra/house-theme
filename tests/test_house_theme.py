from datetime import date

import pytest
from flask import Flask, render_template_string

from house_theme import THEMES, get_active_theme, init_theme, parse_birthdays
from house_theme.colors import contrast


@pytest.mark.parametrize('day, key', [
    (date(2026, 1, 1), 'new_years_day'),
    (date(2026, 1, 15), 'winter'),
    (date(2026, 2, 3), 'black_history'),
    (date(2026, 2, 14), 'valentines'),
    (date(2026, 3, 17), 'st_pattys'),
    (date(2026, 4, 10), 'spring'),
    (date(2026, 6, 20), 'pride'),
    (date(2026, 7, 4), 'summer'),
    (date(2026, 9, 30), 'fall'),
    (date(2026, 10, 1), 'halloween'),
    (date(2026, 10, 5), 'halloween'),
    (date(2026, 10, 31), 'halloween_night'),
    (date(2026, 11, 1), 'fall'),
    (date(2026, 12, 10), 'christmas'),
    (date(2026, 12, 31), 'new_years_eve'),
])
def test_date_resolution(day, key):
    assert get_active_theme(day)['key'] == key


def test_every_day_of_the_year_resolves():
    d = date(2028, 1, 1)  # leap year
    while d.year == 2028:
        assert get_active_theme(d)['key'] in THEMES
        d = date.fromordinal(d.toordinal() + 1)


def test_october_is_not_fall_colors():
    assert get_active_theme(date(2026, 10, 5))['light']['--accent'] != THEMES['fall']['primary']


def test_no_two_themes_share_a_palette_unless_intended():
    # New Year's Day/Eve and Halloween/Halloween night intentionally match.
    allowed = {frozenset({'new_years_day', 'new_years_eve'}),
               frozenset({'halloween', 'halloween_night'})}
    seen = {}
    for key, t in THEMES.items():
        sig = (t['primary'], t['secondary'])
        if sig in seen:
            assert frozenset({key, seen[sig]}) in allowed, (key, seen[sig])
        seen[sig] = key


@pytest.mark.parametrize('key', sorted(THEMES))
def test_text_on_accents_is_readable(key):
    """Button text on --accent and banner text on both gradient stops,
    in light and dark mode, all clear WCAG large-text contrast (3:1)."""
    from house_theme.colors import palette
    for mode in palette(THEMES[key]):
        assert contrast(mode['--on-accent'], mode['--accent']) >= 3, key
        for stop in ('--banner-start', '--banner-end'):
            assert contrast(mode['--banner-text'], mode[stop]) >= 3, (key, stop)


@pytest.mark.parametrize('key', sorted(THEMES))
def test_tinted_page_is_readable(key):
    """Body text and muted text on the tinted background/cards stay readable
    (WCAG AA: 4.5:1 for muted, well above for body text)."""
    from house_theme.colors import palette
    for mode in palette(THEMES[key]):
        for bg in ('--bg', '--surface', '--surface-2'):
            assert contrast(mode['--text'], mode[bg]) >= 10, (key, bg)
            assert contrast(mode['--muted'], mode[bg]) >= 4.5, (key, bg)


def test_october_background_is_not_brown():
    from house_theme.colors import _rgb
    t = get_active_theme(date(2026, 10, 5))
    for mode in (t['light'], t['dark']):
        r, g, b = _rgb(mode['--bg'])
        assert b >= r, mode['--bg']  # purple-leaning, not warm/brown


def test_parse_birthdays():
    parsed = parse_birthdays(' 02-14:Alex , 07-03:Sam,07-03:Jo,bad,13-01:X,05-05: ')
    assert parsed == {(2, 14): ['Alex'], (7, 3): ['Sam', 'Jo']}
    assert parse_birthdays(None) == {}


def test_birthday_on_holiday_goes_first():
    t = get_active_theme(date(2027, 2, 14), parse_birthdays('02-14:Alex'))
    assert t['key'] == 'valentines'
    assert t['banner'] == "Happy Birthday, Alex! 🎂 · 💘 Happy Valentine's Day"
    assert '🎂' in t['emojis'] and '💕' in t['emojis']


def test_birthday_alone_on_plain_day():
    t = get_active_theme(date(2027, 7, 3), parse_birthdays('07-03:Sam,07-03:Jo'))
    assert t['key'] == 'summer'
    assert t['banner'] == 'Happy Birthday, Sam & Jo! 🎂'


def test_leap_day_birthday_shows_feb_28_in_common_years():
    bdays = parse_birthdays('02-29:Lee')
    assert get_active_theme(date(2027, 2, 28), bdays)['birthday']
    assert not get_active_theme(date(2028, 2, 28), bdays)['birthday']
    assert get_active_theme(date(2028, 2, 29), bdays)['birthday']


def test_no_birthday_keeps_holiday_banner():
    t = get_active_theme(date(2027, 2, 14), {})
    assert t['banner'] == "💘 Happy Valentine's Day" and not t['birthday']


PAGE = """<html><head>{% include 'house_theme/head.html' %}</head><body>
{% include 'house_theme/banner.html' %}{% include 'house_theme/scripts.html' %}
</body></html>"""


def make_app(**config):
    app = Flask(__name__)
    app.config.update(TESTING=True, **config)
    init_theme(app)

    @app.route('/')
    def page():
        return render_template_string(PAGE)
    return app


def test_flask_integration_renders_everything():
    app = make_app(HOUSE_THEME_DATE='2026-02-14', BIRTHDAYS='02-14:<b>Alex</b>')
    client = app.test_client()
    html = client.get('/').get_data(as_text=True)

    assert '--accent: #c9184a;' in html
    assert '@media (prefers-color-scheme: dark)' in html
    assert 'Happy Birthday, &lt;b&gt;Alex&lt;/b&gt;! 🎂 · 💘' in html  # escaped
    assert 'data-emojis=' in html and 'window.HOUSE_THEME' not in html
    assert '/_house-theme/house-theme.js' in html

    for asset in ('house-theme.css', 'house-theme.js'):
        resp = client.get(f'/_house-theme/{asset}')
        assert resp.status_code == 200, asset
        resp.close()


def test_halloween_night_banner():
    html = make_app(HOUSE_THEME_DATE='2026-10-31').test_client().get('/').get_data(as_text=True)
    assert 'theme-banner halloween_night' in html
    assert 'Happy Halloween' in html


def test_bad_timezone_fails_at_startup():
    with pytest.raises(Exception):
        make_app(THEME_TZ='Not/AZone')


def test_timezone_is_used(monkeypatch):
    import house_theme
    seen = []
    monkeypatch.setattr(house_theme, 'today_in',
                        lambda tz: seen.append(tz) or date(2026, 10, 5))
    make_app(THEME_TZ='America/Phoenix').test_client().get('/')
    assert seen == ['America/Phoenix']


def test_accent_keys_for_favicons():
    t = get_active_theme(date(2026, 10, 5))
    assert t['accent'] == THEMES['halloween']['primary']
    assert t['accent2'] == THEMES['halloween']['secondary']


def test_accent_soft_in_both_modes():
    t = get_active_theme(date(2026, 10, 5))
    assert t['light']['--accent-soft'] == THEMES['halloween']['soft']
    assert t['dark']['--accent-soft'].startswith('color-mix(')


def test_scheme_auto_emits_both_modes():
    html = make_app(HOUSE_THEME_DATE='2026-10-05').test_client().get('/').get_data(as_text=True)
    assert '@media (prefers-color-scheme: dark)' in html


def test_scheme_dark_only_emits_dark():
    app = Flask(__name__)
    app.config.update(TESTING=True, HOUSE_THEME_DATE='2026-10-05')
    init_theme(app, scheme='dark')
    app.add_url_rule('/', 'page', lambda: render_template_string(PAGE))
    html = app.test_client().get('/').get_data(as_text=True)
    dark_bg = get_active_theme(date(2026, 10, 5))['dark']['--bg']
    assert f'--bg: {dark_bg};' in html
    assert 'color-scheme: dark' in html
    assert '@media (prefers-color-scheme: dark)' not in html


def test_bad_scheme_rejected():
    with pytest.raises(ValueError):
        init_theme(Flask(__name__), scheme='purple')


def test_bad_preview_date_is_ignored():
    resp = make_app(HOUSE_THEME_DATE='not-a-date').test_client().get('/')
    assert resp.status_code == 200


def test_no_inline_script_for_strict_csp():
    """Apps with script-src 'self' (PDF Box) must still get particles."""
    import re
    html = make_app(HOUSE_THEME_DATE='2026-10-31').test_client().get('/').get_data(as_text=True)
    inline = [m for m in re.findall(r'<script([^>]*)>', html) if 'src=' not in m]
    assert inline == []
    assert "data-emojis='[" in html
