import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin

def extract_url_of_anchor(url):
    try:
        # Ensure the URL has a protocol
        if not url.startswith(('http://', 'https://')):
            url = 'http://' + url

        # Fetch the webpage content
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract base domain
        base_domain = urlparse(url).netloc
        if base_domain.startswith('www.'):
            base_domain = base_domain[4:]
        
        total_anchors = 0
        suspicious_anchors = 0
        
        # Iterate through all anchor tags
        for a in soup.find_all('a', href=True):
            total_anchors += 1
            href = a['href']
            
            # Check if the anchor is suspicious
            if href.startswith('#') or href.lower().startswith('javascript:'):
                suspicious_anchors += 1
            else:
                full_url = urljoin(url, href)
                anchor_domain = urlparse(full_url).netloc
                if anchor_domain.startswith('www.'):
                    anchor_domain = anchor_domain[4:]
                if anchor_domain != base_domain and anchor_domain != '':
                    suspicious_anchors += 1
        
        # Calculate percentage of suspicious anchors
        if total_anchors > 0:
            suspicious_percentage = (suspicious_anchors / total_anchors) * 100
        else:
            suspicious_percentage = 0
        
        # Classify based on the rule
        if suspicious_percentage < 31:
            return -1
        elif 31 <= suspicious_percentage <= 67:
            return 0
        else:
            return 1
    
    except Exception as e:
        return "Error", str(e)


