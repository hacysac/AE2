from datetime import date, datetime, time
from typing import Iterator, List, Dict, Any
import requests


class Observation:
    """
    Represents a 15 minute observation of traffic for a specific site, date, and time.
    """

    # required attributes
    site_name: str
    report_date: date
    time_period_ending: time
    avg_speed: int | None
    total_volume: int | None

    def __init__(
        self,
        site_name: str,
        report_date: date,
        time_period_ending: time,
        avg_speed: int | None,
        total_volume: int | None,
    ) -> None:
        """
        Initialises an Observation with the site name, report date, time period ending, average speed, and total vehicle volume.
        """
        self.site_name = site_name
        self.report_date = report_date
        self.time_period_ending = time_period_ending
        self.avg_speed = avg_speed
        self.total_volume = total_volume

    def __lt__(self, other: "Observation") -> bool:
        """
        Returns True if this observation happens before the other, comparing first by date and then by time.
        """
        if self.report_date != other.report_date:
            return self.report_date < other.report_date
        return self.time_period_ending < other.time_period_ending

    def __eq__(self, other: "Observation") -> bool:
        """
        Returns True if two observations share the same site name, report date, and time period ending.
        """
        return (
            self.report_date == other.report_date
            and self.time_period_ending == other.time_period_ending
            and self.site_name == other.site_name
        )

    def __repr__(self) -> str:
        """
        Returns a string representation of the observation including all attributes.
        """
        return f"Observation(name={self.site_name}, date={self.report_date}, time={self.time_period_ending}, speed={self.avg_speed}, volume={self.total_volume})"


class APIConnectionError(Exception):
    """
    Raised when the API connection fails
    """

    pass


class APIResponseError(Exception):
    """
    Raised when the API returns an error status code (e.g. 404, 500)
    """

    pass


class APIConnector:
    """
    Handles making API requests and API error handling
    """

    def make_request(self, url: str) -> Dict[str, Any]:
        """
        Make a GET request to the given URL and return the JSON response as a dictionary
        """
        try:
            # attempt to make the API request
            response = requests.get(url)

            # check for errors from site call
            if response.status_code == 404:
                raise APIResponseError("Site not found (404)")
            elif response.status_code == 500:
                raise APIResponseError("API server error (500)")
            elif response.status_code != 200:
                raise APIResponseError(
                    f"API returned status code {response.status_code}"
                )

            return response.json()  # return the json as a dictionary if no errors

        # errors if the request fails
        except requests.exceptions.Timeout:
            raise APIConnectionError("Request timed out, API may be unavailable")
        except requests.exceptions.ConnectionError:
            raise APIConnectionError(
                "Could not connect to API, check your internet connection"
            )
        except requests.exceptions.RequestException as e:
            raise APIConnectionError(f"Network error: {e}")


class APIClient:
    """
    Functions to get and parse traffic data from the Webtris API, using an APIConnector to handle the actual API requests and error handling.
    """

    BASE_URL = "https://webtris.nationalhighways.co.uk/api/v1.0/reports/daily?"
    connector: APIConnector

    def __init__(self, connector: APIConnector) -> None:
        """
        Initialises the APIClient with an APIConnector instance for making requests.
        """
        self.connector = connector

    def fetch_daily_data(self, site_id: int, date: str) -> List[Observation]:
        """
        Validates the date, fetches daily traffic data for the given site, and returns a sorted list of Observation objects.
        """
        self.validate_date_format(date)
        url = self.construct_url(site_id, date, date)
        json_data = self.connector.make_request(url)
        observations = self.parse_json_response(json_data)
        observations.sort()

        return observations

    def construct_url(self, site_id: int, start_date: str, end_date: str) -> str:
        """
        Constructs and returns the API request URL using the given site ID and date range.
        """
        params = f"sites={site_id}&start_date={start_date}&end_date={end_date}&page=1&page_size=500"
        return self.BASE_URL + params

    def parse_json_response(self, json_data: Dict[str, Any]) -> List[Observation]:
        """
        Parses a JSON response from the API into a list of Observation objects, raising an APIResponseError if not in the expected format.
        """
        observations = []

        if "Rows" not in json_data:
            raise APIResponseError("Invalid API response, missing 'Rows'")

        rows = json_data["Rows"]

        for row in rows:
            # required attributes for an observation
            site_name = row["Site Name"]
            report_date = self.parse_date(row["Report Date"])
            time_period_ending = self.parse_time(row["Time Period Ending"])
            avg_speed = self.parse_optional_int(row.get("Avg mph", ""))
            total_volume = self.parse_optional_int(row.get("Total Volume", ""))

            # create an Observation for each 15 minute interval
            observation = Observation(
                site_name=site_name,
                report_date=report_date,
                time_period_ending=time_period_ending,
                avg_speed=avg_speed,
                total_volume=total_volume,
            )

            # add the observation to the list
            observations.append(observation)

        return observations  # return the final list of observations

    def parse_date(self, date_str: str) -> date:
        """
        Converts a date string from the API into a Python date object.
        """
        # API returns dates like "2025-10-19T00:00:00"
        dt = date(month=int(date_str[5:7]), day=int(date_str[8:10]), year=int(date_str[0:4]))
        return dt

    def parse_time(self, time_str: str) -> time:
        """
        Converts a time string from the API into a Python time object.
        """
        # API returns times like "00:13:00"
        parts = time_str.split(":")
        return time(hour=int(parts[0]), minute=int(parts[1]), second=int(parts[2]))

    def parse_optional_int(self, value: str) -> int | None:
        """
        Attempts to convert a string from the API into an integer, returning None if the value is empty or invalid.
        """
        try:
            return int(value)
        except ValueError:
            return None

    def validate_date_format(self, date: str) -> None:
        """
        Validates that the date string is in DDMMYYYY format, represents a real calendar date, and is within a reasonable year range, raises a ValueError if not.
        """
        try:
            # this will automatically fail if the date is incorrectly formatted or doesnt exist
            year = datetime.strptime(date, "%d%m%Y").year
        except ValueError:
            raise ValueError(f"Invalid date: {date}")
        if year > 2025 or year < 2020:
            raise ValueError(f"Year out of reasonable range: {year}")


class SingleSite:
    """
    Stores and analyses a full day of traffic observations for a single sensor site.
    """

    # required attributes
    site_id: int
    site_name: str
    observations: List[Observation]

    def __init__(self, site_id: int, site_name: str) -> None:
        """
        Initialises a SingleSite with a site ID and site name, with an empty observations list.
        """
        self.site_id = site_id
        self.site_name = site_name
        self.observations = []

    def fetch_data(self, client: APIClient, date: str) -> None:
        """
        Uses an APIClient to fetch and store observations for this site on the given date, updating the site name if a new one is found in the response.
        """
        self.observations = client.fetch_daily_data(self.site_id, date)

        # update site name from observations if it exists
        if self.observations:
            self.site_name = self.observations[0].site_name

    def calculate_avg_speed(self) -> float | None:
        """
        Calculates the average speed across all observations with valid speed data, returns None if no valid data exists.
        """
        valid_speeds = [
            observation.avg_speed
            for observation in self.observations
            if observation.avg_speed is not None
        ]

        if not valid_speeds:
            return None

        return sum(valid_speeds) / len(valid_speeds)

    def calculate_total_volume(self) -> int:
        """
        Calculates the total vehicle volume across all observations with valid volume data.
        """
        total = sum(
            observation.total_volume
            for observation in self.observations
            if observation.total_volume is not None
        )

        return total

    def calculate_avg_speed_for_hour(self, hour: int) -> float | None:
        """
        Calculates the average speed for a specific hour, returns None if no valid data exists for that hour, raises a ValueError for invalid hour input.
        """
        # catch invalid hour
        if not (0 <= hour <= 23):
            raise ValueError(f"Hour must be between 0 and 23, got {hour}")

        hourly_records = [
            observation.avg_speed
            for observation in self.all_observations_for_hour(hour)
            if observation.avg_speed is not None
        ]

        if not hourly_records:
            return None

        return sum(hourly_records) / len(hourly_records)

    def calculate_total_volume_for_hour(self, hour: int) -> int:
        """
        Calculates the total vehicle volume for a specific hour of the day, raises a ValueError for invalid hour input.
        """
        # catch invalid hour input
        if not (0 <= hour <= 23):
            raise ValueError(f"Hour must be between 0 and 23, got {hour}")

        hourly_records = [
            observation.total_volume
            for observation in self.all_observations_for_hour(hour)
            if observation.total_volume is not None
        ]

        return sum(hourly_records)

    def all_observations_for_hour(self, hour: int) -> List[Observation]:
        """
        Returns a list of all observations within the given hour, raises a ValueError for invalid hour input.
        """
        # catch invalid hour input
        if not (0 <= hour <= 23):
            raise ValueError(f"Hour must be between 0 and 23, got {hour}")

        return [
            observation
            for observation in self.observations
            if observation.time_period_ending.hour == hour
        ]

    def find_peak_hour(self) -> int | None:
        """
        Returns the hour with the highest total vehicle volume, returns None if there are no observations or all volume data is missing.
        """
        # check for observations
        if not self.observations:
            return None

        # calculate volume for each hour
        hourly_volumes = {}
        for hour in range(24):
            volume = self.calculate_total_volume_for_hour(hour)
            if volume > 0:  # Only include hours with actual traffic
                hourly_volumes[hour] = volume

        # find hour with max volume
        peak_hour = (
            max(hourly_volumes, key=hourly_volumes.get) if hourly_volumes else None
        )
        return peak_hour

    def __iter__(self) -> Iterator[Observation]:
        """
        Allows iteration over all observations.
        """
        return iter(self.observations)

    def __len__(self) -> int:
        """
        Returns the total observations stored in this site.
        """
        return len(self.observations)
