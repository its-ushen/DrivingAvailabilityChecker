import json
import requests
import time
import logging
import cloudscraper

logger = logging.getLogger("cloudflare_bypass")

def bypass_cloudflare(url, method="GET", headers=None, data=None, params=None, retries=3, backoff=2):
    """
    Bypass Cloudflare protection using cloudscraper
    
    Args:
        url (str): URL to request
        method (str): HTTP method (GET, POST, PUT, DELETE, etc.)
        headers (dict): Request headers
        data (dict/str): Request data for POST, PUT, etc.
        params (dict): URL parameters
        retries (int): Number of retry attempts
        backoff (int): Backoff multiplier for retries
    
    Returns:
        dict/list: JSON response
    """
    scraper = cloudscraper.create_scraper(
        browser={
            'browser': 'chrome',
            'platform': 'android',
            'desktop': False
        }
    )
    
    # Initialize headers if None
    if headers is None:
        headers = {}
    
    # Ensure content-type is set for requests with data
    if data is not None and "Content-Type" not in headers:
        headers["Content-Type"] = "application/json"
    
    # Convert dict data to JSON string
    if isinstance(data, dict) or isinstance(data, list):
        data_str = json.dumps(data)
    else:
        data_str = data
    
    attempt = 0
    last_error = None
    
    while attempt < retries:
        try:
            if method.upper() == "GET":
                response = scraper.get(url, headers=headers, params=params)
            elif method.upper() == "POST":
                response = scraper.post(url, headers=headers, data=data_str, params=params)
            elif method.upper() == "PUT":
                response = scraper.put(url, headers=headers, data=data_str, params=params)
            elif method.upper() == "DELETE":
                response = scraper.delete(url, headers=headers, data=data_str, params=params)
            elif method.upper() == "PATCH":
                # Use request() to handle PATCH method
                response = scraper.request(method="PATCH", url=url, headers=headers, data=data_str, params=params)
            else:
                # Use generic request for any other methods
                response = scraper.request(method=method.upper(), url=url, headers=headers, data=data_str, params=params)
            
            # Check if the response is valid
            if response.status_code == 200:
                # Try to parse JSON response
                try:
                    return response.json()
                except ValueError:
                    # Not a JSON response
                    return response.text
            elif response.status_code == 403 and "cloudflare" in response.text.lower():
                # Cloudflare challenge detected
                logger.warning(f"Cloudflare challenge detected. Retrying... (Attempt {attempt+1}/{retries})")
                attempt += 1
                time.sleep(backoff * attempt)  # Exponential backoff
                continue
            else:
                error_text = response.text[:200] + "..." if len(response.text) > 200 else response.text
                error_msg = f"Request failed with status code {response.status_code}: {error_text}"
                logger.error(error_msg)
                return {"error": error_msg, "status_code": response.status_code, "response_text": response.text}
                
        except Exception as e:
            last_error = str(e)
            logger.warning(f"Error during request: {last_error}. Retrying... (Attempt {attempt+1}/{retries})")
            attempt += 1
            time.sleep(backoff * attempt)
    
    # All retries failed
    error_msg = f"All {retries} attempts failed. Last error: {last_error}"
    logger.error(error_msg)
    return {"error": error_msg}

if __name__ == "__main__":
    # Set up logging for standalone testing
    logging.basicConfig(level=logging.INFO)
    
    # Example usage
    result = bypass_cloudflare("https://example.com")
    print(result)
