from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
import os
import time
import requests
from urllib.parse import urljoin
import hashlib # <--- IMPORT THE HASHING LIBRARY

def download_image(image_url, page_number, cookies, folder_path="images"):
    """Downloads an image from a given URL using the browser's session cookies."""
    # This check is now inside the scrape_book function to handle folder creation there
    # if not os.path.exists(folder_path):
    #     os.makedirs(folder_path)

    try:
        session = requests.Session()
        for cookie in cookies:
            session.cookies.set(cookie['name'], cookie['value'])
        
        response = session.get(image_url, stream=True, headers={'User-Agent': 'Mozilla/5.0'})
        response.raise_for_status()

        image_name = f"{page_number:03d}.png"
        file_path = os.path.join(folder_path, image_name)

        with open(file_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        print(f"Image downloaded: {file_path}")
        return True

    except requests.exceptions.RequestException as e:
        print(f"Error downloading image: {e}")
        return False

def scrape_book(driver, base_url):
    """Scrapes all pages of the current book until no new images are found."""
    print("\n--- Starting to scrape a new book ---")
    downloaded_urls = set()
    page_number = 1
    folder_name = "" # Initialize folder_name

    while True:
        try:
            wait = WebDriverWait(driver, 10)
            css_selector = "svg.page-flip__image--active image"
            image_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, css_selector)))

            relative_url = image_element.get_attribute('href')
            if not relative_url:
                relative_url = driver.execute_script("return arguments[0].getAttribute('xlink:href');", image_element)

            if relative_url and relative_url not in downloaded_urls:
                absolute_url = urljoin(base_url, relative_url)
                print(f"Found image URL for page {page_number}: {absolute_url}")

                cookies = driver.get_cookies()
                
                # --- FIXED FOLDER NAME LOGIC ---
                if page_number == 1:
                    # Create a safe, unique folder name by hashing the URL
                    url_hash = hashlib.sha1(relative_url.encode()).hexdigest()[:10]
                    folder_name = f"book_{url_hash}"
                    print(f"Saving images to folder: ./{folder_name}/")
                    # Create the directory if it doesn't exist
                    if not os.path.exists(folder_name):
                        os.makedirs(folder_name)
                
                if download_image(absolute_url, page_number, cookies, folder_path=folder_name):
                    downloaded_urls.add(relative_url)
                    page_number += 1
                else:
                    print("Skipping page due to download error.")

            elif relative_url:
                print("Image already processed. Assuming end of book.")
                break
            else:
                print("Found the image element, but could not extract a URL.")

            driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ARROW_RIGHT)
            time.sleep(1.5)

        except TimeoutException:
            print("Could not find a new image on the page. Assuming the book is finished.")
            break
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            break
            
    print("--- Finished scraping the current book ---")

def main():
    page_url = "https://eduka.lt/"
    base_url = "https://eduka.lt/"

    driver = webdriver.Chrome()
    driver.get(page_url)

    input("Browser has opened. Please log in, then press Enter in this terminal to start scraping the first book...")

    while True:
        scrape_book(driver, base_url)

        user_input = input(
            "\nNavigate to the next book in the browser.\n"
            "Press 'n' and Enter to start scraping the new book, or 'q' and Enter to quit: "
        ).lower()

        if user_input == 'q':
            print("User requested to quit. Exiting.")
            break
        elif user_input != 'n':
            print("Invalid input. Quitting.")
            break

    print("\nScraping session finished. Closing browser.")
    driver.quit()

if __name__ == "__main__":
    main()