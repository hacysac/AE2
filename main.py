from webtris_client import APIClient, APIConnector, SingleSite


def main():
    connector = APIConnector()
    client = APIClient(connector=connector)
    site = SingleSite(site_id=461, site_name="Example Site")
    day = "01"
    month = "01"
    year = "2024"
    date = day + month + year
    site.fetch_data(client, date)
    print(f"Average speed for {date}: {site.calculate_avg_speed()}")
    print(f"Total volume for {date}: {site.calculate_total_volume()}")
    hour = site.find_peak_hour()
    print(f"Peak hour: {hour}")
    print(f"Average speed for hour {hour}: {site.calculate_avg_speed_for_hour(hour)}")
    print(f"Total volume for hour {hour}: {site.calculate_total_volume_for_hour(hour)}")


if __name__ == "__main__":
    main()
