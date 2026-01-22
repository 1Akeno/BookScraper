from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
import os
import time
import requests
import keyboard
from urllib.parse import urljoin

# --- MODIFIED FUNCTION ---
# It now accepts a 'cookies' parameter
def download_image(image_url, page_number, cookies, folder_path="images"):
    """Downloads an image from a given URL using the browser's session cookies."""
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    try:
        # --- NEW: Create a session and load the cookies into it ---
        session = requests.Session()
        for cookie in cookies:
            session.cookies.set(cookie['name'], cookie['value'])
        # --- END NEW ---
        
        # Make the request using the authenticated session
        response = session.get(image_url, stream=True, headers={'User-Agent': 'Mozilla/5.0'})
        response.raise_for_status()

        # --- MODIFIED: Corrected the file extension to .png ---
        image_name = f"{page_number:03d}.png"
        file_path = os.path.join(folder_path, image_name)

        with open(file_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        print(f"Image downloaded: {file_path}")

    except requests.exceptions.RequestException as e:
        print(f"Error downloading image: {e}")

def main():
    # --- IMPORTANT ---
    # Make sure these URLs are correct.
    page_url = "https://eduka.lt/"
    base_url = "https://eduka.lt/"
    # --- END IMPORTANT ---

    driver = webdriver.Chrome()
    driver.get(page_url)

    input("Browser has opened. Please log in, then press Enter in this window to start scraping...")

    print("\nScraping started. Press and hold 'q' to quit.")
    downloaded_urls = set()
    page_number = 1

    while True:
        try:
            if keyboard.is_pressed('q'):
                print("'q' key pressed. Exiting.")
                break

            wait = WebDriverWait(driver, 10)
            css_selector = "svg.page-flip__image--active image"
            image_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, css_selector)))

            relative_url = image_element.get_attribute('href')
            if not relative_url:
                relative_url = driver.execute_script("return arguments[0].getAttribute('xlink:href');", image_element)

            if relative_url and relative_url not in downloaded_urls:
                absolute_url = urljoin(base_url, relative_url)
                print(f"Found image URL: {absolute_url}")

                # --- NEW: Get cookies from the browser BEFORE downloading ---
                cookies = driver.get_cookies()
                
                # --- MODIFIED: Pass the cookies to the download function ---
                download_image(absolute_url, page_number, cookies)
                
                downloaded_urls.add(relative_url)
                page_number += 1
            elif relative_url:
                print("Image already downloaded. Skipping.")
            else:
                print("Found the image element, but could not extract a URL.")

        except TimeoutException:
            print("Could not find a new image on the page. Assuming the book is finished.")
            break

        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            break

        driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ARROW_RIGHT)
        print("Right arrow key pressed.")
        time.sleep(1.5)

    print("Scraping finished. Closing browser.")
    driver.quit()

if __name__ == "__main__":
    main()