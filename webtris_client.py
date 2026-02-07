from datetime import date, datetime, time
from typing import List, Optional, Dict, Any
import requests

#15 minute traffic oservations from a single site
class TrafficObservation:

    site_name: str
    report_date: date
    time_period_ending: time
    avg_speed: Optional[int]
    total_volume: Optional[int]

    def __init__(self, site_name: str, report_date: date, time_period_ending: time, avg_speed: Optional[int], total_volume: Optional[int]):
        self.site_name = site_name
        self.report_date = report_date
        self.time_period_ending = time_period_ending
        self.avg_speed = avg_speed
        self.total_volume = total_volume
    
    def is_valid(self) -> bool:
        return self.avg_speed is not None and self.total_volume is not None
    
    def __lt__(self, other: 'TrafficObservation') -> bool:
        if self.report_date != other.report_date:
            return self.report_date < other.report_date
        return self.time_period_ending < other.time_period_ending
    
    def __eq__(self, other: 'TrafficObservation') -> bool:
        return (self.report_date == other.report_date and self.time_period_ending == other.time_period_ending and self.site_name == other.site_name)
    
    def __repr__(self) -> str:
        return (f"TrafficObservation(site={self.site_name}, date={self.report_date}, time={self.time_period_ending}, speed={self.avg_speed}, volume={self.total_volume})")

#when API can't be reached
class APIConnectionError(Exception):
    pass

#when API returns an error status code
class APIResponseError(Exception):
    pass

#handles API connections and error
class APIConnector:
    
    def make_request(self, url: str) -> Dict[str, Any]:

        try:
            response = requests.get(url)
            
            # Check for  errors
            if response.status_code == 404:
                raise APIResponseError(f"Site not found (404)")
            elif response.status_code == 500:
                raise APIResponseError(f"API server error (500)")
            elif response.status_code != 200:
                raise APIResponseError(f"API returned status code {response.status_code}")
            
            return response.json()
            
        except requests.exceptions.Timeout:
            raise APIConnectionError("Request timed out - API may be unavailable")
        except requests.exceptions.ConnectionError:
            raise APIConnectionError("Could not connect to API - check your internet connection")
        except requests.exceptions.RequestException as e:
            raise APIConnectionError(f"Network error: {str(e)}")
  
        
class APIClient:
    
    BASE_URL = "https://webtris.nationalhighways.co.uk/api/v1.0"
    connector: APIConnector
    
    def __init__(self, connector: APIConnector):
        self.connector = connector
    
    #fetch the daily data in 15 minute intervals
    def fetch_daily_data(self, site_id: int, date: str) -> List[TrafficObservation]:
        self.validate_date_format(date)
        url = self.construct_url(site_id, date, date)
        json_data = self.connector.make_request(url)
        observations = self.parse_json_response(json_data)
        observations.sort()
        
        return observations
    
    def construct_url(self, site_id: int, start_date: str, end_date: str) -> str:
        
        endpoint = f"{self.BASE_URL}/reports/daily?"
        params = f"sites={site_id}&start_date={start_date}&end_date={end_date}&page=1&page_size=500"
        return endpoint + params
    
    #parse the json response into a list of TrafficObservations
    def parse_json_response(self, json_data: Dict[str, Any]) -> List[TrafficObservation]:

        observations = []

        if "Rows" not in json_data:
            raise APIResponseError("Invalid API response - missing 'Rows'")
        
        rows = json_data["Rows"]
        
        for row in rows:
            #required fields
            site_name = row["Site Name"]
            report_date = self.parse_date(row["Report Date"])
            time_period_ending = self.parse_time(row["Time Period Ending"])
            avg_speed = self.parse_optional_int(row.get("Avg mph", ""))
            total_volume = self.parse_optional_int(row.get("Total Volume", ""))

            #create a TrafficObservation for each 15 minute interval
            observation = TrafficObservation(
                            site_name=site_name,
                            report_date=report_date,
                            time_period_ending=time_period_ending,
                            avg_speed=avg_speed,
                            total_volume=total_volume)
            
            observations.append(observation)
        
        return observations
    
    def parse_date(self, date_str: str) -> date:
        #API returns dates like "2025-10-19T00:00:00"
        dt = datetime.fromisoformat(date_str)
        return dt.date()
    
    def parse_time(self, time_str: str) -> time:
        #API returns times like "00:14:00"
        parts = time_str.split(":")
        return time(hour=int(parts[0]), minute=int(parts[1]), second=int(parts[2]))
    
    def parse_optional_int(self, value: str) -> Optional[int]:
        try:
            return int(value)
        except:
            return None
    
    def validate_date_format(self, date: str) -> None:
        if len(date) != 8:
            raise ValueError(f"Date must be 8 characters in format DDMMYYYY, got: {date}")
        
        try:
            #Try to parse it to check validity
            day = int(date[0:2])
            month = int(date[2:4])
            year = int(date[4:8])
            
            #Basic validation
            if not (1 <= day <= 31):
                raise ValueError(f"Invalid day: {day}")
            if not (1 <= month <= 12):
                raise ValueError(f"Invalid month: {month}")
            if year < 2020 or year > 2030:
                raise ValueError(f"Year out of reasonable range: {year}")
                
        except ValueError as e:
            raise ValueError(f"Invalid date format: {date}. Error: {str(e)}")
        
#all 15 minute intervals from a single site for a given day
class SingleSite:
    site_id: int
    site_name: str
    observations: List[TrafficObservation]
    
    def __init__(self, site_id: int, site_name: str):
        self.site_id = site_id
        self.site_name = site_name
        self.observations = []
    
    def fetch_data(self, client: APIClient, date: str) -> None:
        self.observations = client.fetch_daily_data(self.site_id, date)
        
        #update site name from observations if it exists
        if self.observations:
            self.site_name = self.observations[0].site_name
    
    def calculate_avg_speed(self) -> Optional[float]:
        valid_speeds = [
            observation.avg_speed for observation in self.observations 
            if observation.avg_speed is not None
        ]
        
        if not valid_speeds:
            return None
        
        return sum(valid_speeds) / len(valid_speeds)
    
    def calculate_total_volume(self) -> int:
        total = sum(
            observation.total_volume for observation in self.observations 
            if observation.total_volume is not None
        )
        
        return total
    
    def calculate_avg_speed_for_hour(self, hour: int) -> Optional[float]:
        #catch invalid hour input
        if not (0 <= hour <= 23):
            raise ValueError(f"Hour must be between 0 and 23, got {hour}")
        
        hourly_records = [
            observation.avg_speed for observation in self.all_observations_for_hour(hour)
            if observation.avg_speed is not None
        ]
        
        if not hourly_records:
            return None
        
        return sum(hourly_records) / len(hourly_records)
    
    def calculate_total_volume_for_hour(self, hour: int) -> int:
        #catch invalid hour input
        if not (0 <= hour <= 23):
            raise ValueError(f"Hour must be between 0 and 23, got {hour}")

        hourly_records = [
            observation.total_volume for observation in self.all_observations_for_hour(hour) 
            if observation.total_volume is not None
        ]

        return sum(hourly_records)

    def all_observations_for_hour(self, hour: int) -> List[TrafficObservation]:
        #catch invalid hour input
        if not (0 <= hour <= 23):
            raise ValueError(f"Hour must be between 0 and 23, got {hour}")
        
        return [
            observation for observation in self.observations 
            if observation.time_period_ending.hour == hour
        ]
    
    def find_peak_hour(self) -> Optional[int]:
        #check for observations
        if not self.observations:
            return None
        
        # Calculate volume for each hour
        hourly_volumes = {}
        for hour in range(24):
            volume = self.calculate_total_volume_for_hour(hour)
            if volume > 0:  # Only include hours with actual traffic
                hourly_volumes[hour] = volume
        
        #find hour with max volume
        peak_hour = max(hourly_volumes, key=hourly_volumes.get) if hourly_volumes else None
        return peak_hour
    
    def __iter__(self):
        return iter(self.observations)
    
    def __len__(self) -> int:
        return len(self.observations)
    
    def __repr__(self) -> str:
        return (f"Site(id={self.site_id}, name='{self.site_name}', observations={len(self.observations)})")