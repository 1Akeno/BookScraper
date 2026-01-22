import sys
import requests
from bs4 import BeautifulSoup

def scrape_pegasas_page(url):
    """Scrape a Pegasas book page for metadata using current site layout."""
    data = {}
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code != 200:
            return {}
        soup = BeautifulSoup(resp.text, "html.parser")
        
        
        h1 = soup.find("h1", class_="product-title")
        if h1:
            data["book_name"] = h1.get_text(strip=True)
        
       
        author_span = soup.find("span", class_="product-author")
        if author_span:
            data["author"] = author_span.get_text(strip=True)
        
        
        specs = soup.select("ul.product-specs li")
        for li in specs:
            span = li.find("span")
            if not span:
                continue
            key = span.get_text(strip=True).lower()
            value = span.next_sibling
            if value:
                value = value.strip()
            else:
                
                value = li.get_text(strip=True).replace(span.get_text(strip=True), "").strip()
            if "leidykla" in key:
                data["publisher"] = value
            elif "leidimo metai" in key:
                data["year"] = value
            elif "puslapių skaičius" in key:
                data["total_pages"] = value
            elif "isbn" in key or "ean" in key:
                data["identifier"] = value
            elif "leidinio kalba" in key:
                data["language"] = value
            elif "serija" in key:
                data["series_name"] = value
        
        return data
    except Exception as e:
        print("Error scraping Pegasas:", e)
        return {}

def print_form(data):
    print(f"Book name: {data.get('book_name', '')}\n")
    print(f"Category: -- not selected -- (Dropdown)")
    print(f"Language: {data.get('language', '-- not selected --')} (Dropdown)")
    print(f"Type of content: -- not selected -- (Dropdown)")
    print(f"Publisher: {data.get('publisher', '')}")
    print(f"Series name: {data.get('series_name', '')}")
    print(f"Volume: ")
    print(f"Edition: ")
    print(f"Year: {data.get('year', '')}")
    print(f"Total pages: {data.get('total_pages', '')}")
    print(f"Book description: ")
    print(f"Author(s): {data.get('author', '')}")
    print(f"Identifier (e.g., ISBN): {data.get('identifier', '')}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python fetch_book.py <Pegasas URL>")
        return
    url = sys.argv[1]
    if not url.startswith("http") or "pegasas.lt" not in url:
        print("Please provide a valid Pegasas book URL.")
        return

    data = scrape_pegasas_page(url)
    if not data:
        print("Could not find book on Pegasas.")
        return

    print_form(data)

if __name__ == "__main__":
    main()
