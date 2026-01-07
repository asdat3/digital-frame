# Digital Frame Dashboard

A personal smart picture frame web dashboard built with Flask.

## Features

- Weather display (two cities)
- Calendar events
- Crypto prices & charts
- Clock & countdown timer
- Daily word
- Nextcloud background images

## Setup

1. Copy `example.env` to `.env` and configure
2. Run with Docker: `docker-compose up -d`

Or run:
```bash
pip install -r requirements.txt
python -m app.main
```

## Device Setup

I am just using a Raspberry Pi Zero W2 or something. Running Kiosk OS to display the Page. And schedule rebooting every 24h.
