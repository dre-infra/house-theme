"""Small color helpers so dark-mode accents and on-accent text are derived
from each theme's three colors instead of being hand-kept per theme."""

LIGHT_TEXT = '#fffaf5'
DARK_TEXT = '#1a130e'


def _rgb(hex_color):
    h = hex_color.lstrip('#')
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def _hex(rgb):
    return '#' + ''.join(f'{max(0, min(255, round(c))):02x}' for c in rgb)


def mix(a, b, amount):
    """Blend `amount` (0-1) of color b into color a."""
    ra, rb = _rgb(a), _rgb(b)
    return _hex(x + (y - x) * amount for x, y in zip(ra, rb))


def lighten(color, amount):
    return mix(color, '#ffffff', amount)


def darken(color, amount):
    return mix(color, '#000000', amount)


def luminance(color):
    def channel(c):
        c /= 255
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (channel(c) for c in _rgb(color))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(a, b):
    la, lb = sorted((luminance(a), luminance(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def best_text_on(*backgrounds):
    """Light or dark text, whichever has the better worst-case contrast
    across every background it will sit on (e.g. both gradient stops)."""
    def worst(text):
        return min(contrast(text, bg) for bg in backgrounds)
    return LIGHT_TEXT if worst(LIGHT_TEXT) >= worst(DARK_TEXT) else DARK_TEXT


def palette(theme):
    """CSS custom-property values for light and dark mode."""
    p, s = theme['primary'], theme['secondary']

    light_banner_end = darken(p, 0.22)
    light = {
        '--accent': p,
        '--accent-2': s,
        '--accent-soft-light': theme['soft'],
        '--on-accent': best_text_on(p),
        '--banner-start': p,
        '--banner-end': light_banner_end,
        '--banner-text': best_text_on(p, light_banner_end),
    }

    # Lift accents in dark mode so they don't go muddy on dark surfaces.
    # Darker primaries get lifted more.
    lift = 0.38 if luminance(p) < 0.12 else 0.22
    dp, ds = lighten(p, lift), lighten(s, 0.18)
    dark_banner_start = darken(p, 0.15)
    dark = {
        '--accent': dp,
        '--accent-2': ds,
        '--on-accent': best_text_on(dp),
        '--banner-start': dark_banner_start,
        '--banner-end': darken(p, 0.4),
        '--banner-text': best_text_on(dark_banner_start, darken(p, 0.4)),
    }
    return light, dark
