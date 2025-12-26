# Portfolio Site

Single-page personal portfolio built with Flask + SQLAlchemy + Authlib + JS. Includes:
- Hero with name, photo, contacts.
- Projects list (seeded from DB).
- About section.
- Auth via GitHub and Google.
- Comments (requires login).
- Yandex.Metrika + Google Tag Manager hooks.

## Setup
```bash
cd Projects/portfolio
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

Fill `.env` with secrets:
- `SECRET_KEY` — any random string.
- `DATABASE_URL` — defaults to `sqlite:///portfolio.db`.
- `GITHUB_CLIENT_ID` / `GITHUB_CLIENT_SECRET`
- `GOOGLE_CLIENT_ID` / `GOOGLE_CLIENT_SECRET`
- `YANDEX_METRIKA_ID`, `GTM_ID` — optional, leave empty to disable scripts.

## Run
```bash
flask --app app run --debug
```

## Notes
- Projects are seeded once on startup; update `seed_projects` in `app.py` to change.
- Replace `static/me.jpg` with your photo (any 1:1 image). Without it, a gradient placeholder is used.
- Comments: authenticated users only; latest 10 pre-rendered, new ones posted via `/comments`.
- Design intentionally diverges from fus1ond.ru: dark/teal/orange palette, grid layout, glassy cards.
- Social auth requires valid OAuth apps for GitHub/Google and matching redirect URLs:
  - `http://localhost:5000/auth/github/callback`
  - `http://localhost:5000/auth/google/callback`
