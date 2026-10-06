# house-theme

Shared date-driven seasonal/holiday theme for the dre-infra family apps
(Recipe Box, Grocery Box, Focus Box, Flash Box, ...). Every app pins a tag,
so a new holiday or color fix is made once here.

## What it does

- Picks today's theme: **single day > whole month > season**
- Sets each theme's accent colors (`--accent`, `--accent-2`,
  `--accent-soft-light`, `--on-accent`, `--banner-*`) for light **and** dark
  mode. Neutrals stay with each app's `style.css`.
- Shows a banner, ambient emoji particles, and a burst on click
- Birthday banners from `.env`, birthday first when it lands on a holiday

| Theme | When | Primary | Secondary | Soft |
|---|---|---|---|---|
| Winter | Jan | `#3a7ca5` icy blue | `#9fb4c7` silver | `#e3eef6` |
| Black History Month | Feb | `#b3242e` | `#2d6a4f` | `#f4d9b0` |
| Valentine's | 2/14 | `#c9184a` rose | `#ff8fab` pink | `#ffe5ec` |
| St. Patrick's | 3/17 | `#1e8a3a` shamrock | `#d4a017` gold | `#e3f4e7` |
| Spring | Mar–May | `#4c9a2a` leaf green | `#e07a9f` blossom | `#eaf5e1` |
| Pride | Jun | `#e0245e` + rainbow banner | `#5b8def` | `#ffe1ea` |
| Summer | Jul–Aug | `#0f8b8d` ocean teal | `#f2b705` sun yellow | `#e0f4f4` |
| Fall | Sep, Nov | `#c4570f` burnt orange | `#7a4a24` brown | `#f6e6d6` |
| Halloween | Oct | `#6b3fa0` purple | `#7cb518` slime green | `#ece3f5` |
| Halloween night | 10/31 | same + dark banner, bats | | |
| Christmas | Dec | `#b3202a` red | `#1f6f43` pine | `#f6e3e3` |
| New Year's Eve / Day | 12/31, 1/1 | `#c9a227` gold | `#1d2b53` midnight | `#f7f0d8` |

Dark-mode accents and the text color on accents are derived in
`colors.py`; `tests/` checks every theme for readable contrast.

## Adding it to an app

`requirements.txt` (tarball URL, so the slim Docker image doesn't need git):

```
house-theme @ https://github.com/dre-infra/house-theme/archive/refs/tags/v1.0.0.tar.gz
```

`app.py`:

```python
from house_theme import init_theme

app = Flask(__name__)
init_theme(app)
```

Base template (after the app's own stylesheet):

```html
<head>
  <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
  {% include 'house_theme/head.html' %}
</head>
<body>
  ...header...
  {% include 'house_theme/banner.html' %}
  ...
  {% include 'house_theme/scripts.html' %}
</body>
```

`theme` is available in every template (`theme.key`, `theme.label`,
`theme.banner`, `theme.birthday`). The app's CSS should use the house-style
accent variables above instead of hard-coded colors.

## Settings (`.env`)

| Var | Example | Notes |
|---|---|---|
| `BIRTHDAYS` | `02-14:Name,07-03:Other` | `MM-DD:Name`, comma-separated. Same date twice → "Name & Other". 02-29 shows on 02-28 in non-leap years. Bad entries are skipped and logged. |
| `THEME_TZ` | `America/Phoenix` | Default. Containers run UTC, which flipped themes at 5 PM. |
| `HOUSE_THEME_DATE` | `2026-10-31` | Preview a date's theme. Logs a warning; unset when done. |

Read once at startup, so restart the container after editing (`docker compose
up -d` does that when `.env` changes).

## Changing a theme / releasing

1. Branch, edit `src/house_theme/themes.py` (dates in `SINGLE_DAYS` /
   `MONTHS`, colors/emoji/banner in `THEMES`), add a test, PR, merge.
2. Bump `version` in `pyproject.toml` and `__version__`, then tag:
   `git tag v1.1.0 && git push origin v1.1.0`
3. In each app, bump the tag in `requirements.txt`. (Dependabot doesn't
   track URL pins, so this step is manual.)

## Development

```bash
python -m venv .venv && . .venv/bin/activate
pip install -e ".[dev]"
ruff check . && pytest -q
```
