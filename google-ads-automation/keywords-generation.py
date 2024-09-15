import os
import sys
import requests
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException


def get_access_token():
    """Obtains a fresh access token using the refresh token."""
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
        response.raise_for_status()  # Raise an exception for bad responses
        access_token = response.json().get("access_token")
        return access_token
    except (
        requests.exceptions.RequestException
    ) as e:  # Handle all request-related errors
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


def fetch_keyword_stats(client, customer_id):
    """Fetches keyword statistics for the past 7 days."""
    if not customer_id:
        print("Error: Customer ID (ACCOUNT_ID environment variable) is not set.")
        sys.exit(1)

    ga_service = client.get_service("GoogleAdsService")

    # Construct the Google Ads query
    query = """
        SELECT
            campaign.id,
            campaign.name,
            ad_group.id,
            ad_group.name,
            ad_group_criterion.criterion_id,
            ad_group_criterion.keyword.text,
            ad_group_criterion.keyword.match_type,
            metrics.impressions,
            metrics.clicks,
            metrics.cost_micros
        FROM keyword_view
        WHERE
            segments.date DURING LAST_7_DAYS
            AND campaign.advertising_channel_type = 'SEARCH'
            AND ad_group.status = 'ENABLED'
            AND ad_group_criterion.status IN ('ENABLED', 'PAUSED')
        ORDER BY metrics.impressions DESC
        LIMIT 50"""

    try:
        response = ga_service.search(customer_id=customer_id, query=query)

        for row in response:
            campaign = row.campaign
            ad_group = row.ad_group
            criterion = row.ad_group_criterion
            metrics = row.metrics

            # Format and print the keyword statistics
            print(
                f'Keyword: "{criterion.keyword.text}" '
                f"(Match Type: {criterion.keyword.match_type.name}, ID: {criterion.criterion_id}) "
                f'in Ad Group: "{ad_group.name}" (ID: {ad_group.id}) '
                f'in Campaign: "{campaign.name}" (ID: {campaign.id}) '
                f"had {metrics.impressions} impressions, {metrics.clicks} clicks, "
                f"and cost {metrics.cost_micros / 1000000:.2f} "
                f"in the last 7 days."
            )

    except GoogleAdsException as ex:
        handle_googleads_exception(ex)


def handle_googleads_exception(exception):
    """Prints detailed error information from a Google Ads exception."""
    print(
        f'Request with ID "{exception.request_id}" failed with status '
        f'"{exception.error.code().name}" and includes the following errors:'
    )
    for error in exception.failure.errors:
        print(f'\tError with message "{error.message}".')
        if error.location:
            for field_path_element in error.location.field_path_elements:
                print(f"\t\tOn field: {field_path_element.field_name}")


if __name__ == "__main__":
    # Initialize the Google Ads client
    client = create_google_ads_client()
    if not client:
        print("Failed to create Google Ads client. Check your credentials.")
        sys.exit(1)

    customer_id = os.getenv("ACCOUNT_ID")
    if not customer_id:
        print("Error: Customer ID (ACCOUNT_ID environment variable) is not set.")
        sys.exit(1)

    fetch_keyword_stats(client, customer_id)
