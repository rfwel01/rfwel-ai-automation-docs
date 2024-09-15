import os
import requests
from bs4 import BeautifulSoup
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException
from google.oauth2.credentials import Credentials

# Set up environment variables for Google Ads API and OpenAI API
DEVELOPER_TOKEN = os.getenv("DEVELOPER_TOKEN")
GCLIENT_ID = os.getenv("GCLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REFRESH_TOKEN = os.getenv("GCP_REFRESH_TOKEN")
ACCOUNT_ID = os.getenv("ACCOUNT_ID")
MANAGER_CUSTOMER_ID = os.getenv("MANAGER_CUSTOMER_ID")
API_KEY = os.getenv("OPENAI_API_KEY")

# Default location and language settings for keyword generation
_DEFAULT_LOCATION_IDS = ["2840"]  # United States
_DEFAULT_LANGUAGE_ID = "1000"  # English
EXCLUDE_KEYWORDS = [
    "amazon",
    "reddit",
]  # Examples of keywords to exclude from suggestions


def create_google_ads_client():
    """Initializes and returns the Google Ads API client."""
    credentials = Credentials.from_authorized_user_info(
        {
            "client_id": GCLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "refresh_token": REFRESH_TOKEN,
            "token_uri": "https://oauth2.googleapis.com/token",
        }
    )
    return GoogleAdsClient(
        credentials=credentials,
        developer_token=DEVELOPER_TOKEN,
        login_customer_id=MANAGER_CUSTOMER_ID,
    )


def clean_description(html_content):
    """Cleans HTML content and returns readable text."""
    soup = BeautifulSoup(html_content, "html.parser")
    cleaned_text = soup.get_text()
    return cleaned_text


def fetch_and_clean_url_content(url):
    """Fetches the URL content, cleans it, and returns the text."""
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors
        cleaned_text = clean_description(response.text)
        return cleaned_text
    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL content: {e}")
        return ""


def generate_keyword_ideas(url):
    """Generates keyword ideas from a URL using the Google Ads API."""
    client = create_google_ads_client()
    keyword_plan_idea_service = client.get_service("KeywordPlanIdeaService")
    request = client.get_type("GenerateKeywordIdeasRequest")

    # Set up the request parameters
    request.customer_id = ACCOUNT_ID
    request.language = client.get_service("GoogleAdsService").language_constant_path(
        _DEFAULT_LANGUAGE_ID
    )
    for location_id in _DEFAULT_LOCATION_IDS:
        request.geo_target_constants.append(
            client.get_service("GeoTargetConstantService").geo_target_constant_path(
                location_id
            )
        )
    request.include_adult_keywords = False
    request.keyword_plan_network = client.enums.KeywordPlanNetworkEnum.GOOGLE_SEARCH
    request.url_seed.url = url

    try:
        response = keyword_plan_idea_service.generate_keyword_ideas(request=request)
        keyword_ideas = [
            {
                "text": idea.text,
                "avg_monthly_searches": idea.keyword_idea_metrics.avg_monthly_searches,
            }
            for idea in response.results
            if not any(exclude_word in idea.text for exclude_word in EXCLUDE_KEYWORDS)
        ]

        # Print out the keywords (optional)
        print("Generated Keywords:")
        for keyword in keyword_ideas:
            print(
                f"Keyword: {keyword['text']}, Avg Monthly Searches: {keyword['avg_monthly_searches']}"
            )

        return keyword_ideas
    except GoogleAdsException as ex:
        print(f'Request with ID "{ex.request_id}" failed: {ex.error.message}')
        return []


def generate_responsive_search_ad(description, api_key, keyword_ideas):
    """Generates responsive search ad suggestions and a page title using GPT-4o."""
    keywords = [idea["text"] for idea in keyword_ideas]
    keyword_list = ", ".join(keywords)

    # Craft a detailed prompt for GPT-4o
    prompt = (
        f"Generate SEO-optimized Responsive Search Ad content using the provided keywords, emphasizing the most relevant keywords. "
        f"Ensure that the generated content strictly adheres to the following character limits, including spaces and punctuation:\n"
        f"1. Headlines: Create 15 brief headlines, each no longer than 29 characters, including spaces and punctuation. Do not include numbering; just list each headline as a separate sentence.\n"
        f"2. Descriptions: Create 4 descriptions, each no longer than 89 characters, including spaces and punctuation. Again, do not include numbering; just list each description as a separate sentence.\n"
        f"3. Broad Match Keywords: Recommend broad match keywords from the list.\n"
        f"4. Phrase Match Keywords: Recommend phrase match keywords from the list.\n"
        f"5. Exact Match Keywords: Recommend exact match keywords from the list.\n"
        f"6. Page Title: Suggest an SEO-optimized page title no longer than 60 characters, including spaces and punctuation, using the keywords.\n"
        f"\nKeywords: {keyword_list}\n\nProduct Description: {description}"
    )

    headers = {"Authorization": f"Bearer {api_key}"}
    data = {
        "model": "gpt-4o",
        "messages": [
            {
                "role": "system",
                "content": "Generate responsive search ad content and a page title based on the provided description and keywords.",
            },
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.9,
        "max_tokens": 1500,
    }

    try:
        response = requests.post(
            "https://api.openai.com/v1/chat/completions", json=data, headers=headers
        )
        response.raise_for_status()
        content = response.json()
        message_content = (
            content.get("choices", [{}])[0].get("message", {}).get("content", "")
        )
        return message_content
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err} - {http_err.response.text}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

    return ""


if __name__ == "__main__":
    # Get the URL to process from the user (or you can hardcode it here)
    url = input("Enter the URL to process: ")

    # Fetch and clean URL content
    cleaned_content = fetch_and_clean_url_content(url)
    if not cleaned_content:
        print("Failed to fetch and clean URL content.")
    else:
        # Generate keyword ideas from URL
        keyword_ideas = generate_keyword_ideas(url)
        if not keyword_ideas:
            print("Failed to generate keyword ideas.")
        else:
            # Generate responsive search ad suggestions and a page title using GPT-4
            ad_suggestions = generate_responsive_search_ad(
                cleaned_content, API_KEY, keyword_ideas
            )
            if ad_suggestions:
                print("Responsive Search Ad Suggestions and Page Title:")
                print(ad_suggestions)
            else:
                print(
                    "Failed to generate responsive search ad suggestions and page title."
                )
