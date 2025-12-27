import requests
import xml.etree.ElementTree as ET
from flask import jsonify

def _get_daily_word():
    """Fetch the current Merriam-Webster Word of the Day and its short definition."""
    try:
        url = "https://www.merriam-webster.com/wotd/feed/rss2"
        response = requests.get(url)
        response.raise_for_status()

        root = ET.fromstring(response.content)

        main_element = root.find(".//channel/item")
        if main_element is None:
            return None, None

        title = main_element.findtext("title")
        word = title.strip() if title else None

        namespaces = {'merriam': 'http://www.merriam-webster.com/2006/rss'}
        shortdef = main_element.findtext("merriam:shortdef", namespaces=namespaces)
        
        if shortdef is None:
            for elem in main_element.iter():
                if 'shortdef' in elem.tag:
                    shortdef = elem.text
                    break
        
        definition = shortdef.strip() if shortdef else None

        if word:
            return word, definition
        else:
            return None, None
            
    except Exception as e:
        print(f"Error fetching daily word: {str(e)}")
        return None, None

def return_daily_word():
    word, definition = _get_daily_word()
    if word:
        return jsonify({
            "daily_word": word,
            "definition": definition
        }), 200
    else:
        return jsonify({
            "error": "Couldn't fetch the word of the day.",
            "daily_word": None,
            "definition": None
        }), 500