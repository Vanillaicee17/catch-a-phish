from urllib.parse import urlparse
import tldextract
import requests
from bs4 import BeautifulSoup

def classify_url(main_url):
    try:
        response = requests.get(f"http://{main_url}" if not main_url.startswith("http") else main_url)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        embedded_urls = []
        for tag in ['img', 'script', 'iframe', 'link', 'video', 'audio']:
            for element in soup.find_all(tag):
                src = element.get('src') or element.get('href')
                if src:
                    embedded_urls.append(src)


        
        main_domain = tldextract.extract(main_url)
        main_domain = f"{main_domain.domain}.{main_domain.suffix}"
        
        external_requests = 0
        for url in embedded_urls:
            parsed_url = tldextract.extract(url)
   
            url_domain = f"{parsed_url.domain}.{parsed_url.suffix}"
            if url_domain and url_domain != main_domain:
                external_requests += 1
        
        total_requests = len(embedded_urls)
        
        if total_requests == 0:
            return -1
        
        external_percentage = (external_requests / total_requests) * 100
        
        if external_percentage < 30:  # Increased threshold
            return -1
        elif 30 <= external_percentage <= 75:  # Adjusted range
            return 0
        else:
            return 1
    
    except Exception as e:
        print(f"Error processing URL: {e}")
        return 1

