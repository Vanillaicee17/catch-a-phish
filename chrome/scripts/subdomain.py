import tldextract

def analyze_subdomain(url):
    """
    Analyzes the subdomain structure of a URL to determine if it's legitimate,
    suspicious, or phishing based on the number of subdomains.

    Args:
        url (str): The URL to analyze.

    Returns:
        str: "Legitimate", "Suspicious", or "Phishing" based on subdomain count.
    """

    # Extract the domain information using tldextract
    ext = tldextract.extract(url)

    # Reconstruct the relevant part of the domain (excluding the subdomain)
    registered_domain = ext.domain + "." + ext.suffix

    # Count the number of dots in the subdomain part
    num_dots = ext.subdomain.count('.')

    if num_dots > 1:
        return 1
    elif num_dots == 1:
        return 0
    else:
        return -1

