from flask import Flask, jsonify
from beautiful_scraper import scrape_zomato_beautiful
import json
import os
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({
        "message": "Zomato Scraper API",
        "endpoints": {
            "/scrape": "Scrape latest data from Zomato",
            "/data": "Get the last scraped data",
            "/status": "Get API status"
        },
        "note": "Using BeautifulSoup method (no Chrome required)"
    })

@app.route('/scrape')
def scrape():
    try:
        restaurants = scrape_zomato_beautiful()
        
        if isinstance(restaurants, dict) and "error" in restaurants:
            return jsonify({
                "success": False,
                "error": restaurants["error"],
                "message": "Scraping failed. Zomato's website structure may have changed."
            }), 500
        
        with open("restaurants.json", "w", encoding="utf-8") as f:
            json.dump({
                "last_updated": datetime.now().isoformat(),
                "count": len(restaurants),
                "restaurants": restaurants
            }, f, ensure_ascii=False, indent=2)
        
        return jsonify({
            "success": True,
            "message": f"Successfully scraped {len(restaurants)} restaurants",
            "count": len(restaurants),
            "last_updated": datetime.now().isoformat(),
            "restaurants": restaurants
        })
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "An unexpected error occurred during scraping."
        }), 500

@app.route('/data')
def get_data():
    try:
        if os.path.exists('restaurants.json'):
            with open('restaurants.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
            return jsonify(data)
        else:
            return jsonify({
                "message": "No data available. Please run /scrape first.",
                "count": 0,
                "restaurants": []
            })
    except Exception as e:
        return jsonify({
            "error": str(e),
            "message": "Error reading stored data."
        }), 500

@app.route('/status')
def status():
    return jsonify({
        "status": "active",
        "timestamp": datetime.now().isoformat(),
        "method": "BeautifulSoup"
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
