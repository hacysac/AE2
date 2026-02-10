from webtris_client import *

def main():
    connector = APIConnector()
    client = APIClient(connector=connector)
    site = SingleSite(site_id=461, site_name="Example Site")
    date = "01012024"
    site.fetch_data(client, date)
    print(repr(site))
    print(f"Average speed for {date}: {site.calculate_avg_speed()}")
    print(f"Total volume for {date}: {site.calculate_total_volume()}")
    hour = 8
    print(f"Average speed for hour {hour}: {site.calculate_avg_speed_for_hour(hour)}")
    print(f"Total volume for hour {hour}: {site.calculate_total_volume_for_hour(hour)}")

if __name__ == "__main__":
    main()