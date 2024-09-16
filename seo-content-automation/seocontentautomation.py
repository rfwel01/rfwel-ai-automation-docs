import os
import requests
import openai
import json
from bs4 import BeautifulSoup
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException


# Helper functions
def get_access_token():
    """Obtains a fresh access token using the refresh token for Google Ads."""
    url = "https://www.googleapis.com/oauth2/v4/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "client_id": os.getenv("GCLIENT_ID"),
        "client_secret": os.getenv("CLIENT_SECRET"),
        "refresh_token": os.getenv("GCP_REFRESH_TOKEN"),
        "grant_type": "refresh_token",
    }
    try:
        response = requests.post(url, headers=headers, data=data)
        response.raise_for_status()
        return response.json().get("access_token")
    except requests.exceptions.RequestException as e:
        print(f"Error: Failed to obtain access token: {e}")
        return None


def create_google_ads_client():
    """Creates a Google Ads API client using the obtained access token."""
    access_token = get_access_token()
    if not access_token:
        print("Error: No access token available.")
        return None

    credentials = {
        "developer_token": os.getenv("DEVELOPER_TOKEN"),
        "client_id": os.getenv("GCLIENT_ID"),
        "client_secret": os.getenv("CLIENT_SECRET"),
        "refresh_token": os.getenv("GCP_REFRESH_TOKEN"),
        "login_customer_id": os.getenv("MANAGER_CUSTOMER_ID"),
        "access_token": access_token,
        "use_proto_plus": True,
    }
    client = GoogleAdsClient.load_from_dict(credentials, version="v16")
    return client


def fetch_keyword_ideas(client, customer_id):
    """Fetches keyword ideas from Google Ads API."""
    if not customer_id:
        print("Error: Customer ID is not set.")
        return []

    ga_service = client.get_service("GoogleAdsService")

    query = """
        SELECT
            ad_group_criterion.keyword.text,
            metrics.impressions,
            metrics.clicks
        FROM keyword_view
        WHERE
            segments.date DURING LAST_7_DAYS
            AND campaign.advertising_channel_type = 'SEARCH'
            AND ad_group.status = 'ENABLED'
            AND ad_group_criterion.status IN ('ENABLED', 'PAUSED')
        ORDER BY metrics.impressions DESC
        LIMIT 10
    """

    try:
        response = ga_service.search(customer_id=customer_id, query=query)
        keywords = [row.ad_group_criterion.keyword.text for row in response]
        return keywords

    except GoogleAdsException as ex:
        handle_googleads_exception(ex)
        return []


def handle_googleads_exception(exception):
    """Handles Google Ads exceptions."""
    print(f'Request with ID "{exception.request_id}" failed.')
    for error in exception.failure.errors:
        print(f'Error message: "{error.message}".')


# Function to extract product details using BeautifulSoup
def fetch_product_details(product_url):
    """
    Fetches the product details from a given product URL using BeautifulSoup.

    Args:
        product_url (str): The URL of the product page to scrape.

    Returns:
        dict: A dictionary containing product details like name, description, link, and more.
    """
    try:
        response = requests.get(product_url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        product_details = {
            "name": soup.find("h1").get_text(),
            "product_description": soup.find("meta", {"name": "description"})[
                "content"
            ],
            "product_link": product_url,
            "main_image": soup.find("img")[
                "src"
            ],  # Modify based on actual structure of the page
            "weight": soup.find(
                "span", {"class": "weight"}
            ).get_text(),  # Modify accordingly
            "search_keywords": soup.find("meta", {"name": "keywords"})["content"],
        }

        return product_details
    except Exception as e:
        print(f"An error occurred while fetching product details: {e}")
        return None


# GPT-4 interaction function
def rewrite_description_with_highlights(description, keywords):
    """Uses OpenAI API to rewrite a product description with keyword integration."""
    openai.api_key = os.getenv("OPENAI_API_KEY")

    prompt = f"Rewrite the following product description: {description}.\nEnsure that the following keywords are naturally integrated: {keywords}."

    try:
        response = openai.Completion.create(
            engine="gpt-4",
            prompt=prompt,
            max_tokens=600,
            n=1,
            stop=None,
            temperature=0.7,
        )
        return response.choices[0].text.strip()
    except Exception as e:
        print(f"Error using OpenAI API: {e}")
        return None


# Main function
def generate_optimized_product_details(product_url):
    """Fetch product details, generate keyword ideas, and enhance product description using GPT-4."""
    # Fetch product details
    product_details = fetch_product_details(product_url)
    if not product_details:
        print("Failed to fetch product details.")
        return

    # Create Google Ads client and fetch keywords
    client = create_google_ads_client()
    if not client:
        print("Failed to create Google Ads client.")
        return

    customer_id = os.getenv("ACCOUNT_ID")
    keyword_ideas = fetch_keyword_ideas(client, customer_id)

    if not keyword_ideas:
        print("Failed to fetch keyword ideas.")
        return

    # Rewrite product description using GPT-4
    enhanced_description = rewrite_description_with_highlights(
        product_details["product_description"], ", ".join(keyword_ideas)
    )
    if not enhanced_description:
        print("Failed to enhance product description.")
        return

    # Output the final result
    product_details["enhanced_description"] = enhanced_description
    product_details["keywords"] = keyword_ideas

    print("Final Enhanced Product Details:")
    print(json.dumps(product_details, indent=4))


if __name__ == "__main__":
    # Test URL (Replace with actual product page URL)
    product_url = "https://example.com/sample-product"
    generate_optimized_product_details(product_url)
