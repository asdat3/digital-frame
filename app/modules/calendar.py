from ics import Calendar
import requests
from datetime import datetime, timezone
from app.config.config import settings
from flask import jsonify


def _get_calendar_events(calendar_url: str, max_events: int = 5):
    if not calendar_url or calendar_url == "empty":
        return jsonify({
            "error": "Calendar URL is not set",
            "events": [],
        }), 200
    
    try:
        resp = requests.get(calendar_url, timeout=5)
        resp.raise_for_status()
        
        calendar = Calendar(resp.text)
        now = datetime.now(timezone.utc)
        start_of_today = now.replace(hour=0, minute=0, second=0, microsecond=0)

        events = []
        for event in sorted(calendar.events, key=lambda e: e.begin):
            if len(events) >= max_events:
                break
                
            event_begin = event.begin.datetime
            if event_begin.tzinfo is None:
                event_begin = event_begin.replace(tzinfo=timezone.utc)
            
            if event_begin >= start_of_today:
                events.append({
                    "name": event.name,
                    "begin": event.begin.datetime.isoformat(),
                    "end": event.end.datetime.isoformat() if event.end else None,
                })

        return jsonify({"events": events}), 200

    except Exception as e:
        print(f"Calendar error: {e}")
        return jsonify({
            "error": str(e),
            "events": [],
        }), 500

def return_calendar_events():
    calendars = {
        "personal": settings.calendar_ical_url,
        "holidays": settings.calendar_holidays_url,
        "garbage": settings.calendar_garbage_url,
    }

    results = {}
    for name, url in calendars.items():
        if len(url) > 5:
            response, status = _get_calendar_events(url)
            data = response.get_json()
            results[name] = data

    return jsonify({
        "calendars": results
    }), 200
