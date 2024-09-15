import os
import datetime
import requests
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException
import time
from google.api_core.exceptions import ResourceExhausted
import sys

# Environment variables for authentication
DEVELOPER_TOKEN = os.getenv("DEVELOPER_TOKEN")
GCLIENT_ID = os.getenv("GCLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REFRESH_TOKEN = os.getenv("GCP_REFRESH_TOKEN")
MANAGER_CUSTOMER_ID = os.getenv("MANAGER_CUSTOMER_ID").replace(
    "-", ""
)  # Ensure no dashes
API_VERSION = "v16"

_DATE_FORMAT = "%Y%m%d"


def get_access_token():
    """Obtains a fresh access token using the refresh token."""
    url = "https://www.googleapis.com/oauth2/v4/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "client_id": GCLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "refresh_token": REFRESH_TOKEN,
        "grant_type": "refresh_token",
    }
    try:
        response = requests.post(url, headers=headers, data=data)
        response.raise_for_status()
        access_token = response.json().get("access_token")
        return access_token
    except requests.exceptions.HTTPError as e:
        print(f"Failed to obtain access token. HTTP error: {e.response.status_code}")
    except Exception as e:
        print(f"Failed to obtain access token. Unexpected error: {e}")
    return None


def create_google_ads_client():
    """Creates a Google Ads API client using the obtained access token."""
    access_token = get_access_token()
    if not access_token:
        print("No access token available. Exiting function.")
        return None

    credentials = {
        "developer_token": DEVELOPER_TOKEN,
        "client_id": GCLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "refresh_token": REFRESH_TOKEN,
        "login_customer_id": MANAGER_CUSTOMER_ID,
        "access_token": access_token,
        "use_proto_plus": True,
    }
    client = GoogleAdsClient.load_from_dict(credentials, version=API_VERSION)
    return client


def get_existing_campaign_id(client, customer_id, campaign_name):
    """Checks if a campaign with the given name already exists and returns its ID."""
    query = f"""
    SELECT
        campaign.id,
        campaign.name
    FROM
        campaign
    WHERE
        campaign.name = '{campaign_name}'
    """
    ga_service = client.get_service("GoogleAdsService")
    response = ga_service.search(customer_id=customer_id, query=query)
    for row in response:
        return row.campaign.id
    return None


def get_existing_ad_group_id(client, customer_id, campaign_id, ad_group_name):
    """Checks if an ad group with the given name exists within the campaign and returns its ID."""
    query = f"""
    SELECT
        ad_group.id,
        ad_group.name
    FROM
        ad_group
    WHERE
        ad_group.campaign = 'customers/{customer_id}/campaigns/{campaign_id}'
        AND ad_group.name = '{ad_group_name}'
    """
    ga_service = client.get_service("GoogleAdsService")
    response = ga_service.search(customer_id=customer_id, query=query)
    for row in response:
        return row.ad_group.id
    return None


def create_campaign_budget(client, customer_id, budget_amount):
    """Creates a new campaign budget with the specified amount."""
    budget_service = client.get_service("CampaignBudgetService")

    # Create a campaign budget.
    campaign_budget_operation = client.get_type("CampaignBudgetOperation")
    campaign_budget = campaign_budget_operation.create
    campaign_budget.name = f"Budget {datetime.datetime.now().isoformat()}"
    campaign_budget.amount_micros = budget_amount
    campaign_budget.delivery_method = client.enums.BudgetDeliveryMethodEnum.STANDARD

    try:
        budget_response = budget_service.mutate_campaign_budgets(
            customer_id=customer_id, operations=[campaign_budget_operation]
        )
        budget_id = budget_response.results[0].resource_name.split("/")[-1]
        print(f"Created budget with ID: {budget_id}")
        return budget_id
    except GoogleAdsException as ex:
        handle_googleads_exception(ex)
        return None


def create_campaign(client, customer_id, campaign_name, budget_id):
    """Creates a new search campaign with the specified name and budget."""
    campaign_service = client.get_service("CampaignService")
    campaign_operation = client.get_type("CampaignOperation")
    campaign = campaign_operation.create
    campaign.name = campaign_name
    campaign.advertising_channel_type = client.enums.AdvertisingChannelTypeEnum.SEARCH
    campaign.status = client.enums.CampaignStatusEnum.PAUSED
    campaign.manual_cpc.enhanced_cpc_enabled = True
    campaign.campaign_budget = client.get_service(
        "CampaignBudgetService"
    ).campaign_budget_path(customer_id, budget_id)
    campaign.network_settings.target_google_search = True
    campaign.network_settings.target_search_network = True
    campaign.network_settings.target_content_network = True
    campaign.network_settings.target_partner_search_network = False
    campaign.start_date = (
        datetime.datetime.now() + datetime.timedelta(days=1)
    ).strftime(_DATE_FORMAT)
    campaign.end_date = (
        datetime.datetime.now() + datetime.timedelta(days=365)
    ).strftime(_DATE_FORMAT)

    campaign_response = campaign_service.mutate_campaigns(
        customer_id=customer_id, operations=[campaign_operation]
    )
    campaign_id = campaign_response.results[0].resource_name.split("/")[-1]
    print(f"Created Campaign with ID: {campaign_id}")
    return campaign_id


def create_ad_group(client, customer_id, campaign_id, ad_group_name):
    """Creates a new ad group within the specified campaign."""
    ad_group_service = client.get_service("AdGroupService")
    ad_group_operation = client.get_type("AdGroupOperation")
    ad_group = ad_group_operation.create
    ad_group.name = ad_group_name
    ad_group.campaign = client.get_service("CampaignService").campaign_path(
        customer_id, campaign_id
    )
    ad_group.type = client.enums.AdGroupTypeEnum.SEARCH_STANDARD
    ad_group.cpc_bid_micros = 1000000  # Example bid value, $1 = 1,000,000 micros
    ad_group.status = client.enums.AdGroupStatusEnum.ENABLED

    ad_group_response = ad_group_service.mutate_ad_groups(
        customer_id=customer_id, operations=[ad_group_operation]
    )
    ad_group_id = ad_group_response.results[0].resource_name.split("/")[-1]
    print(f"Created Ad Group with ID: {ad_group_id}")
    return ad_group_id


def create_search_ad(
    client,
    customer_id,
    campaign_name,
    ad_group_name,
    final_url,
    headline_part1,
    headline_part2,
    headline_part3,
    description1,
    description2,
    keyword_list,
):
    ad_group_service = client.get_service("AdGroupService")
    ad_group_ad_service = client.get_service("AdGroupAdService")

    """Creates a new responsive search ad within the specified ad group."""

    # Get existing campaign ID
    campaign_id = get_existing_campaign_id(client, customer_id, campaign_name)
    if not campaign_id:
        budget_id = create_campaign_budget(
            client, customer_id, 10000000
        )  # Example budget amount
        campaign_id = create_campaign(client, customer_id, campaign_name, budget_id)

    # Get existing ad group ID
    ad_group_id = get_existing_ad_group_id(
        client, customer_id, campaign_id, ad_group_name
    )
    if not ad_group_id:
        ad_group_id = create_ad_group(client, customer_id, campaign_id, ad_group_name)

    # Create Responsive Search Ad
    ad_group_ad_operation = client.get_type("AdGroupAdOperation")
    ad_group_ad = ad_group_ad_operation.create
    ad_group_ad.ad_group = client.get_service("AdGroupService").ad_group_path(
        customer_id, ad_group_id
    )
    ad_group_ad.status = client.enums.AdGroupAdStatusEnum.PAUSED
    ad = ad_group_ad.ad
    ad.final_urls.append(final_url)

    # Properly create AdTextAsset instances
    headline_asset1 = client.get_type("AdTextAsset")
    headline_asset1.text = headline_part1
    headline_asset2 = client.get_type("AdTextAsset")
    headline_asset2.text = headline_part2
    headline_asset3 = client.get_type("AdTextAsset")
    headline_asset3.text = headline_part3
    description_asset1 = client.get_type("AdTextAsset")
    description_asset1.text = description1
    description_asset2 = client.get_type("AdTextAsset")
    description_asset2.text = description2

    ad.responsive_search_ad.headlines.extend(
        [headline_asset1, headline_asset2, headline_asset3]
    )
    ad.responsive_search_ad.descriptions.extend(
        [description_asset1, description_asset2]
    )

    ad_group_ad_response = ad_group_ad_service.mutate_ad_group_ads(
        customer_id=customer_id, operations=[ad_group_ad_operation]
    )

    print(
        f"Created Responsive Search Ad with ID: {ad_group_ad_response.results[0].resource_name.split('/')[-1]}"
    )

    # Add keywords to the ad group
    add_keywords(client, customer_id, ad_group_id, keyword_list)

    # Set location targeting to the United States
    set_geo_targeting(client, customer_id, campaign_id)


def add_keywords(client, customer_id, ad_group_id, keyword_list):
    """Adds keywords to the specified ad group with the given match type."""
    ad_group_criterion_service = client.get_service("AdGroupCriterionService")

    operations = []
    for keyword in keyword_list:
        criterion_operation = client.get_type("AdGroupCriterionOperation")
        criterion = criterion_operation.create
        criterion.ad_group = client.get_service("AdGroupService").ad_group_path(
            customer_id, ad_group_id
        )
        criterion.keyword.text = keyword
        criterion.keyword.match_type = client.enums.KeywordMatchTypeEnum.BROAD
        criterion.status = client.enums.AdGroupCriterionStatusEnum.ENABLED
        criterion.cpc_bid_micros = 140000  # Set the CPC bid in micros
        operations.append(criterion_operation)

    ad_group_criterion_service.mutate_ad_group_criteria(
        customer_id=customer_id, operations=operations
    )
    print(f"Added {len(operations)} keywords to Ad Group ID: {ad_group_id}")


def set_geo_targeting(client, customer_id, campaign_id):
    query = 'SELECT geo_target_constant.resource_name FROM geo_target_constant WHERE geo_target_constant.country_code = "US"'
    location_criteria = []
    ga_service = client.get_service("GoogleAdsService")
    response = ga_service.search(customer_id=customer_id, query=query)
    for row in response:
        location_criteria.append(row.geo_target_constant.resource_name)

    campaign_criterion_operations = []
    for location in location_criteria:
        criterion_operation = client.get_type("CampaignCriterionOperation")
        criterion = criterion_operation.create
        criterion.campaign = client.get_service("CampaignService").campaign_path(
            customer_id, campaign_id
        )
        criterion.location.geo_target_constant = location
        criterion.status = client.enums.CampaignCriterionStatusEnum.ENABLED
        campaign_criterion_operations.append(criterion_operation)

    campaign_criterion_service = client.get_service("CampaignCriterionService")
    try:
        campaign_criterion_service.mutate_campaign_criteria(
            customer_id=customer_id, operations=campaign_criterion_operations
        )
        print(f"Set geo-targeting for Campaign ID: {campaign_id}")
    except GoogleAdsException as ex:
        handle_googleads_exception(ex)


def handle_googleads_exception(exception):
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
        print("Failed to create Google Ads client.")
        sys.exit(1)

    customer_id = os.getenv("ACCOUNT_ID").replace("-", "")  # Ensure no dashes
    campaign_name = "Power control Solutions"
    ad_group_name = "Power Control"
    final_url = "https://www.rfwel.com/us/index.php/4g-lte-frequency-bands"
    headline_part1 = "Control Power Remotely"
    headline_part2 = "Smart Power Monitoring"
    headline_part3 = "Reliable Power Switches"
    description1 = "Manage power outlets with ease using our remote control solutions."
    description2 = "Ensure your devices are always powered with advanced monitoring."

    # Sample  Broad Match Keywords
    broad_match_keywords = [
        "remote power switch",
        "power monitor",
        "power switch",
        "remote power monitoring",
        "power outlet",
    ]

    # Sample Phrase Match Keywords
    phrase_match_keywords = [
        "remote power switch",
        "power monitor",
        "remote power monitoring",
        "power outlet",
    ]

    # Sample Exact Match Keywords
    exact_match_keywords = [
        "[remote power switch]",
        "[power monitor]",
        "[remote power monitoring]",
        "[power outlet]",
    ]

    # Combine all keywords into one list
    keyword_list = broad_match_keywords + phrase_match_keywords + exact_match_keywords

    try:
        create_search_ad(
            client,
            customer_id,
            campaign_name,
            ad_group_name,
            final_url,
            headline_part1,
            headline_part2,
            headline_part3,
            description1,
            description2,
            keyword_list,
        )
        print("Successfully created Google Responsive Search Ad.")
    except ResourceExhausted as e:
        print("Quota exceeded: Retrying after a delay.")
        time.sleep(60)  # Wait for 60 seconds before retrying
        # Retry the operation
        create_search_ad(
            client,
            customer_id,
            campaign_name,
            ad_group_name,
            final_url,
            headline_part1,
            headline_part2,
            headline_part3,
            description1,
            description2,
            keyword_list,
        )
