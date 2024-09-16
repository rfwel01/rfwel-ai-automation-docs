# Product Details Optimization Script

This script fetches product details from a product page using web scraping, retrieves keyword ideas using the Google Ads API, and uses the OpenAI GPT-4 model to rewrite and optimize product descriptions by integrating the fetched keywords. It is designed to help you improve SEO performance by generating enhanced product descriptions with relevant keywords.

## Table of Contents

- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Environment Variables](#environment-variables)
- [Usage](#usage)
- [Project Structure](#project-structure)

## Features

- **Web Scraping**: Fetches product details like title, description, weight, and image from a given product URL using BeautifulSoup.
- **Google Ads API**: Retrieves keyword ideas based on product information.
- **OpenAI GPT-4 Integration**: Rewrites and enhances the product description with the retrieved keywords to optimize it for SEO.
- **Error Handling**: Provides detailed error handling for network requests, API calls, and scraping.

## Prerequisites

Ensure you have the following installed:

- **Python 3.8+**
- **Google Ads API Credentials**
- **OpenAI API Key**
- **BeautifulSoup 4**
- **Requests**

You'll also need accounts with:

- **Google Ads API** for generating keyword ideas.
- **OpenAI GPT-4 API** for rewriting product descriptions.

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/rfwel01/rfwel-ai-automation-docs.git
    ```

2. Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

    The `requirements.txt` file should contain:

    ```text
    google-ads
    google-auth
    openai
    beautifulsoup4
    requests
    ```

3. Make sure you have Google Ads API, OpenAI, and web scraping credentials ready.

## Environment Variables

The script relies on several environment variables for secure credential handling. Set the following environment variables in your system or within a `.env` file:

```bash
# Google Ads API
export GCLIENT_ID="your-google-client-id"
export CLIENT_SECRET="your-client-secret"
export GCP_REFRESH_TOKEN="your-refresh-token"
export DEVELOPER_TOKEN="your-developer-token"
export MANAGER_CUSTOMER_ID="your-manager-customer-id"
export ACCOUNT_ID="your-google-ads-account-id"

# OpenAI API
export OPENAI_API_KEY="your-openai-api-key"
```

You can add these to a `.env` file in your project root:

```bash
GCLIENT_ID=your-google-client-id
CLIENT_SECRET=your-client-secret
GCP_REFRESH_TOKEN=your-refresh-token
DEVELOPER_TOKEN=your-developer-token
MANAGER_CUSTOMER_ID=your-manager-customer-id
ACCOUNT_ID=your-google-ads-account-id
OPENAI_API_KEY=your-openai-api-key
```

Use `python-dotenv` to load these variables if needed.

## Usage

Once everything is set up, you can run the script to generate optimized product details by scraping a product page and enhancing the description.

1. Modify the `product_url` variable in the script to the product page URL you want to scrape.
2. Run the script:
    ```bash
    python seocontentautomation.py
    ```

This will fetch the product details, retrieve keyword ideas from Google Ads, and enhance the description using GPT-4. The final enhanced product details will be printed to the console.

### Example Output

```json
{
    "name": "Mitsubishi PAC-USWHS003-TH-1, Kumo Cloud Wireless Temperature & Humidity Sensor",
    "sku": "PAC-USWHS003-TH-1",
    "enhanced_description": "The Mitsubishi PAC-USWHS003-TH-1 is a high-performance wireless temperature and humidity sensor designed for seamless integration with your HVAC system. With its capability to communicate with the Kumo Cloud App, it allows for precise temperature and humidity monitoring in any room, ensuring optimal comfort. Equipped with a CR2477 coincell battery for reliable operation and easy installation via the Kumo Cloud App, this sensor is a perfect addition for efficient climate control.",
    "product_features": [
        "Compatible with PAC-USWHS002-WF-2",
        "Includes Wireless Temperature & Humidity Sensor and double-sided adhesive disc",
        "Installation and configuration through Kumo Cloud App",
        "CR2477 coincell battery (1000 mAH at 3V)",
        "Supports remote sensing and control"
    ],
    "meta_title": "Mitsubishi PAC-USWHS003-TH-1 Wireless Temperature & Humidity Sensor - Optimize Home Comfort",
    "meta_description": "Discover the Mitsubishi PAC-USWHS003-TH-1 Wireless Temperature & Humidity Sensor for enhanced home climate control. Compatible with the Kumo Cloud App, this sensor ensures precise monitoring and adjustment of temperature and humidity. Buy now to improve your HVAC system efficiency.",
    "meta_keywords": ["Mitsubishi PAC-USWHS003-TH-1", "wireless temperature sensor", "HVAC humidity sensor", "Kumo Cloud sensor", "temperature and humidity control"],
    "product_link": "https://shop.rfwel.com/mitsubishi-pac-uswhs003-th-1-kumo-cloud-wireless-temperature-humidity-sensor/",
    "main_image": "https://example.com/sample-product.jpg",
    "weight": "0.09 lbs",
    "search_keywords": ["wireless temperature sensor", "PAC-USWHS003-TH-1", "HVAC humidity sensor", "Mitsubishi sensor"]
}

```

## Project Structure

```
product-optimization/
│
├── product_optimization.py    # Main script
├── requirements.txt           # Python dependencies
└── README.md                  # Project documentation
```

