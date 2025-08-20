from flask import Flask, jsonify
from scraper import scrape_zomato
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
        "note": "If scraping fails, Chrome might not be properly installed on the server."
    })

@app.route('/scrape')
def scrape():
    try:
        restaurants = scrape_zomato()
        
        # Check if we got an error response
        if isinstance(restaurants, dict) and "error" in restaurants:
            return jsonify({
                "success": False,
                "error": restaurants["error"],
                "message": "Scraping failed. This could be due to Chrome not being installed on the server or Zomato's website structure changes."
            }), 500
        
        # Save to JSON
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
            "message": "An unexpected error occurred during scraping. Chrome might not be installed on the server."
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
        "chrome_installed": os.path.exists('/usr/bin/google-chrome-stable')
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
