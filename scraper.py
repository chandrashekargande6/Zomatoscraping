from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.os_manager import ChromeType
import time
import json
import os

def scrape_zomato():
    # Set up Chrome options for headless mode
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    
    # Check if we're on Render (where Chrome is installed system-wide)
    if os.path.exists('/usr/bin/google-chrome-stable'):
        chrome_options.binary_location = '/usr/bin/google-chrome-stable'
    
    # Initialize driver
    try:
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()), 
            options=chrome_options
        )
    except Exception as e:
        print(f"Error initializing Chrome driver: {str(e)}")
        # Fallback: try with system Chrome
        try:
            driver = webdriver.Chrome(
                service=Service(ChromeDriverManager(chrome_type=ChromeType.GOOGLE).install()),
                options=chrome_options
            )
        except Exception as e2:
            print(f"Fallback also failed: {str(e2)}")
            return {"error": f"Chrome initialization failed: {str(e)}"}
    
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
        max_scrolls = 3  # Reduced to make it faster
        
        while scrolls < max_scrolls:
            # Scroll down
            driver.execute_script("window.scrollBy(0, arguments[0]);", screen_height)
            time.sleep(scroll_pause)
            scrolls += 1

        # ✅ Try multiple selectors to find restaurant names
        restaurant_selectors = [
            "a[href*='/r/']",  # Restaurant links
            "h4",  # Heading elements
            "[data-testid*='restaurant']",  # Test IDs
            ".sc-1hp8d8a-0",  # Common Zomato class
            "a.sc-1kx5g6g-0",  # Another common Zomato class
            ".sc-1hez2tp-0",  # Another potential Zomato class
        ]
        
        restaurants = []
        
        for selector in restaurant_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    print(f"Found {len(elements)} elements with selector: {selector}")
                    for element in elements:
                        try:
                            name = element.text.strip()
                            # Safely check if name exists and has valid content
                            if name and len(name) > 2 and name not in ["", " "]:  
                                restaurants.append({"name": name})
                        except Exception as e:
                            print(f"Error processing element text: {str(e)}")
                            continue
                    
                    # If we found a reasonable number of restaurants, break
                    if len(restaurants) >= 10:
                        break
            except Exception as e:
                print(f"Error with selector {selector}: {str(e)}")
                continue

        # If no restaurants found with specific selectors, try a more general approach
        if len(restaurants) == 0:
            print("Trying general text extraction...")
            # Look for all text elements that might be restaurant names
            all_elements = driver.find_elements(By.CSS_SELECTOR, "h1, h2, h3, h4, h5, h6, a, div, span")
            for element in all_elements:
                try:
                    text = element.text.strip() if element.text else ""
                    # Heuristic: restaurant names are usually 2-10 words
                    if text and 2 <= len(text.split()) <= 10 and len(text) > 3:
                        # Exclude common non-restaurant text
                        excluded_terms = ["home", "login", "sign up", "search", "filter", "sort", "zomato", "download app", "menu", "order", "cart"]
                        if not any(term in text.lower() for term in excluded_terms):
                            restaurants.append({"name": text})
                except Exception as e:
                    print(f"Error processing general element: {str(e)}")
                    continue
        
        # Remove duplicates while preserving order
        seen = set()
        unique_restaurants = []
        for r in restaurants:
            try:
                if r['name'] not in seen:
                    seen.add(r['name'])
                    unique_restaurants.append(r)
            except Exception as e:
                print(f"Error deduplicating: {str(e)}")
                continue
        
        return unique_restaurants

    except Exception as e:
        print(f"Error during scraping: {str(e)}")
        return {"error": str(e)}
    
    finally:
        # ✅ Quit browser
        try:
            driver.quit()
        except:
            pass

if __name__ == "__main__":
    # Run when executed directly
    restaurants = scrape_zomato()
    
    # ✅ Save to JSON
    with open("restaurants.json", "w", encoding="utf-8") as f:
        json.dump(restaurants, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Scraped {len(restaurants)} restaurants")
    if restaurants:
        print(json.dumps(restaurants[:20], indent=2, ensure_ascii=False))  # preview first 20
