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

1. Clone the repository:
    ```bash
    git clone https://github.com/rfwel01/rfwel-ai-automation-docs.git
    ```

2. Install the required Python libraries:
    ```bash
    pip install requirements.txt
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
Enter the URL to process: https://hcomp.rfwel.com/smart-hvac/
First 10 of the Top 100 Generated Keywords:
Keyword: hv ac, Avg Monthly Searches: 301000
Keyword: hvac system, Avg Monthly Searches: 22200
Keyword: conditioning air, Avg Monthly Searches: 14800
Keyword: optimal humidity in home, Avg Monthly Searches: 8100
Keyword: humidity recommendations home, Avg Monthly Searches: 8100
Keyword: optimal humidity inside home, Avg Monthly Searches: 8100
Keyword: best humidity inside home, Avg Monthly Searches: 8100
Keyword: best home humidity, Avg Monthly Searches: 8100
Keyword: indoor air monitor, Avg Monthly Searches: 6600
Keyword: best humidity indoor, Avg Monthly Searches: 6600

**Headlines:**
Optimal Home Humidity
Best Indoor Humidity
HVAC System Sensors
Indoor Air Monitor
Humidity Recommendations Home
Best Home Humidity
Optimal Humidity Inside
Conditioning Air Sensors
HVAC Wireless Interface
Indoor Air Quality
Best Humidity Indoor
Humidity Sensors Home
Temperature Monitoring HVAC
HVAC Control Systems
Energy Efficient HVAC

**Descriptions:**
Ensure optimal humidity in your home with our advanced HVAC sensors.
Monitor indoor air quality and maintain the best home humidity levels.
Upgrade your HVAC system with wireless sensors for energy efficiency.
Get expert recommendations for the best humidity inside your home.

**Broad Match Keywords:**
hvac, hvac system, conditioning air, optimal humidity, home humidity, indoor air monitor, best humidity

**Phrase Match Keywords:**
"hvac system", "optimal humidity in home", "humidity recommendations home", "best home humidity", "indoor air monitor"

**Exact Match Keywords:**
[hvac system], [optimal humidity in home], [best humidity indoor], [indoor air monitor]

**Page Title:**
Optimize Home Comfort with Advanced HVAC Sensors & Humidity Control
...
```

