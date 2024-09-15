# rfwel-ai-automation-docs
This repository offers developers free access to reference materials, tutorials, and code examples for Rfwel's AI automation solutions. 

# Responsive Search Ad Generator

This project uses python scripts to generate keyword ideas using the Google Ads API from a given URL and creates responsive search ad suggestions, along with an SEO-optimized page title, using OpenAI's GPT-4 API and finally you could push the Responsive Search Ad to Google Ads using Google Ads API endpoint.

## Features

- Fetches content from a provided URL and cleans the HTML.
- Uses the Google Ads API to generate keyword ideas.
- Filters out unwanted keywords (e.g., "amazon", "reddit").
- Uses OpenAI's GPT-4 API to generate responsive search ad suggestions based on the keyword ideas and the cleaned URL content.

## Prerequisites

- Python 3.x
- Google Ads API credentials
- OpenAI API key

## Installation

1. Clone this repository or download the script.
2. Install the required Python libraries:
    ```bash
    pip install requests beautifulsoup4 google-ads google-auth
    ```

## Environment Variables

Before running the script, set the following environment variables for authentication:

- `DEVELOPER_TOKEN`: Your Google Ads developer token.
- `GCLIENT_ID`: Google client ID for OAuth2 authentication.
- `CLIENT_SECRET`: Google client secret for OAuth2 authentication.
- `GCP_REFRESH_TOKEN`: Google refresh token.
- `ACCOUNT_ID`: Google Ads account ID.
- `MANAGER_CUSTOMER_ID`: Google Ads manager customer ID.
- `OPENAI_API_KEY`: OpenAI API key for generating ads with GPT-4.

## Usage

1. Set up your environment variables:
    ```bash
    export DEVELOPER_TOKEN="your_developer_token"
    export GCLIENT_ID="your_client_id"
    export CLIENT_SECRET="your_client_secret"
    export GCP_REFRESH_TOKEN="your_refresh_token"
    export ACCOUNT_ID="your_account_id"
    export MANAGER_CUSTOMER_ID="your_manager_customer_id"
    export OPENAI_API_KEY="your_openai_api_key"
    ```

2. Run the script:
    ```bash
    ai-ads-automation.py
    ```

3. Input the URL when prompted. The script will:
   - Fetch and clean the content from the URL.
   - Generate keyword ideas using the Google Ads API.
   - Use OpenAI's GPT-4 API to generate responsive search ad suggestions and an SEO-optimized page title.

## Code Overview

### Functions

- **`create_google_ads_client()`**: Initializes and returns a Google Ads API client.
- **`clean_description(html_content)`**: Cleans HTML content and returns readable text.
- **`fetch_and_clean_url_content(url)`**: Fetches the URL content and returns cleaned text.
- **`generate_keyword_ideas(url)`**: Uses the Google Ads API to generate keyword ideas for the provided URL.
- **`generate_responsive_search_ad(description, api_key, keyword_ideas)`**: Generates responsive search ad suggestions using GPT-4 based on keyword ideas and cleaned content.

### Main Process

- The script first fetches and cleans the HTML content of the provided URL.
- It then generates keyword ideas using the Google Ads API.
- Finally, it uses the GPT-4 API to generate responsive search ad content and an SEO-optimized page title.

## Example Output

```bash
Enter the URL to process: https://example.com
Generated Keywords:
Keyword: example keyword 1, Avg Monthly Searches: 1200
Keyword: example keyword 2, Avg Monthly Searches: 800

Responsive Search Ad Suggestions and Page Title:
...
```
