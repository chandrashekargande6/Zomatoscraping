from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import json

def scrape_zomato():
    # Set up Chrome options for headless mode
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    
    # Initialize driver
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()), 
        options=chrome_options
    )
    
    try:
        driver.get("https://www.zomato.com/hyderabad/restaurants")
        time.sleep(5)

        # ✅ Try closing login popup if it appears
        try:
            close_btn = driver.find_element(By.CSS_SELECTOR, "button[aria-label='Close'], .sc-1kx5g6g-2, .modal-close")
            close_btn.click()
            print("Popup closed ✅")
            time.sleep(2)
        except Exception as e:
            print(f"No popup found or couldn't close: {str(e)} ✅")

        # ✅ Auto scroll down to load more restaurants
        scroll_pause = 2
        screen_height = driver.execute_script("return window.innerHeight")
        scrolls = 0
        max_scrolls = 10
        
        while scrolls < max_scrolls:
            # Scroll down
            driver.execute_script("window.scrollBy(0, arguments[0]);", screen_height)
            time.sleep(scroll_pause)
            
            # Check if we've reached the bottom
            current_scroll = driver.execute_script("return window.pageYOffset")
            total_height = driver.execute_script("return document.body.scrollHeight")
            
            if current_scroll + screen_height >= total_height:
                break
                
            scrolls += 1

        # ✅ Try multiple selectors to find restaurant names
        restaurant_selectors = [
            "a.sc-1kx5g6g-0",  # New Zomato selector
            "h4.sc-1hp8d8a-0",  # Another common Zomato selector
            "[class*='restaurant-name']",  # Class contains restaurant-name
            "a[href*='/hyderabad/'] h4",  # Anchor with location and h4
            ".sc-1hp8d8a-0",  # Another potential class
        ]
        
        restaurants = []
        
        for selector in restaurant_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    print(f"Found {len(elements)} elements with selector: {selector}")
                    for element in elements:
                        name = element.text.strip()
                        if name and len(name) > 2:  # Filter out very short text
                            restaurants.append({"name": name})
                    break  # Stop if we found elements with this selector
            except Exception as e:
                print(f"Error with selector {selector}: {str(e)}")
                continue

        # If no restaurants found with specific selectors, try a more general approach
        if len(restaurants) == 0:
            print("Trying general text extraction...")
            # Look for all text elements that might be restaurant names
            all_elements = driver.find_elements(By.CSS_SELECTOR, "h1, h2, h3, h4, h5, h6, a, div, span")
            for element in all_elements:
                text = element.text.strip()
                # Heuristic: restaurant names are usually 2-10 words
                if text and 2 <= len(text.split()) <= 10 and len(text) > 3:
                    # Exclude common non-restaurant text
                    excluded_terms = ["home", "login", "sign up", "search", "filter", "sort", "zomato", "download app"]
                    if not any(term in text.lower() for term in excluded_terms):
                        restaurants.append({"name": text})
        
        # Remove duplicates while preserving order
        seen = set()
        unique_restaurants = []
        for r in restaurants:
            if r['name'] not in seen:
                seen.add(r['name'])
                unique_restaurants.append(r)
        
        return unique_restaurants

    except Exception as e:
        print(f"Error during scraping: {str(e)}")
        return {"error": str(e)}
    
    finally:
        # ✅ Quit browser
        driver.quit()

if __name__ == "__main__":
    # Run when executed directly
    restaurants = scrape_zomato()
    
    # ✅ Save to JSON
    with open("restaurants.json", "w", encoding="utf-8") as f:
        json.dump(restaurants, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Scraped {len(restaurants)} restaurants")
    print(json.dumps(restaurants[:20], indent=2, ensure_ascii=False))  # preview first 20