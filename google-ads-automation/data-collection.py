import requests
from bs4 import BeautifulSoup


def fetch_and_clean_url_content(url):
    """
    Fetches content from the specified URL and cleans it using BeautifulSoup.

    Args:
        url (str): The URL of the product page.

    Returns:
        str: The cleaned text content of the page, or an empty string if an error occurs.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad HTTP status codes

        soup = BeautifulSoup(response.content, "html.parser")

        # Remove unwanted elements like scripts, styles, and navigation
        for script in soup(["script", "style", "nav", "header", "footer"]):
            script.extract()

        # Get the cleaned text, joining elements with spaces and stripping extra whitespace
        cleaned_text = soup.get_text(separator=" ", strip=True)
        return cleaned_text

    except requests.exceptions.RequestException as e:
        print(f"Error fetching or cleaning URL content: {e}")
        return ""
