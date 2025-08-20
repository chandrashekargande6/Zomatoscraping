import requests
from bs4 import BeautifulSoup
import json
import re

def scrape_zomato_beautiful():
    """
    Scrape Zomato using requests + BeautifulSoup (no browser needed)
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        url = "https://www.zomato.com/hyderabad/restaurants"
        response = requests.get(url, headers=headers, timeout=30)
        
        if response.status_code != 200:
            return {"error": f"Failed to fetch page. Status code: {response.status_code}"}
        
        soup = BeautifulSoup(response.content, 'html.parser')
        restaurants = []
        
        # Look for restaurant names in various elements
        patterns = [
            # Look for h4 elements (common for restaurant names)
            lambda: [{"name": h4.get_text(strip=True)} for h4 in soup.find_all('h4') if h4.get_text(strip=True)],
            
            # Look for a elements with restaurant links
            lambda: [{"name": a.get_text(strip=True)} for a in soup.find_all('a', href=re.compile(r'/r/')) if a.get_text(strip=True)],
            
            # Look for elements with specific classes
            lambda: [{"name": div.get_text(strip=True)} for div in soup.find_all(class_=re.compile(r'restaurant')) if div.get_text(strip=True)],
            
            # General text extraction (fallback)
            lambda: [{"name": elem.get_text(strip=True)} for elem in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'a']) 
                    if elem.get_text(strip=True) and len(elem.get_text(strip=True)) > 3 and len(elem.get_text(strip=True).split()) <= 5]
        ]
        
        for pattern in patterns:
            try:
                results = pattern()
                if results:
                    restaurants.extend(results)
                    if len(restaurants) >= 20:  # If we found enough, break early
                        break
            except:
                continue
        
        # Filter out non-restaurant text
        excluded_terms = ["home", "login", "sign up", "search", "filter", "sort", "zomato", 
                         "download app", "menu", "order", "cart", "account", "more", "view all"]
        
        filtered_restaurants = []
        for restaurant in restaurants:
            name = restaurant['name'].lower()
            if (len(name) > 3 and 
                not any(term in name for term in excluded_terms) and
                not name.isdigit() and
                not name.startswith('http')):
                filtered_restaurants.append(restaurant)
        
        # Remove duplicates
        seen = set()
        unique_restaurants = []
        for r in filtered_restaurants:
            if r['name'] not in seen:
                seen.add(r['name'])
                unique_restaurants.append(r)
        
        return unique_restaurants[:100]  # Limit to 100 results
        
    except Exception as e:
        return {"error": str(e)}
