import pytest
from datetime import date, time
from webtris_client import *

class MockAPIConnector:
    
    def __init__(self, response_data=None, should_raise=None):
        
        self.response_data = response_data
        self.should_raise = should_raise
    
    def make_request(self, url: str) -> Dict[str, Any]:
        
        if self.should_raise:
            raise self.should_raise
        
        return self.response_data

    

@pytest.fixture
def valid_api_response():

    return {
        "Header": {
            "row_count": 4,
            "start_date": "19102025",
            "end_date": "19102025",
            "links": []
        },
        "Rows": [
            {
                "Site Name": "Example Site",
                "Report Date": "2025-10-19T00:00:00",
                "Time Period Ending": "00:14:00",
                "Avg mph": "65",
                "Total Volume": "182"
            },
            {
                "Site Name": "Example Site",
                "Report Date": "2025-10-19T00:00:00",
                "Time Period Ending": "00:29:00",
                "Avg mph": "70",
                "Total Volume": "150"
            },
            {
                "Site Name": "Example Site",
                "Report Date": "2025-10-19T00:00:00",
                "Time Period Ending": "00:44:00",
                "Avg mph": "68",
                "Total Volume": "120"
            },
            {
                "Site Name": "Example Site",
                "Report Date": "2025-10-19T00:00:00",
                "Time Period Ending": "01:14:00",
                "Avg mph": "55",
                "Total Volume": "200"
            }
        ]
    }


@pytest.fixture
def api_response_with_missing_data():

    return {
        "Header": {
            "row_count": 3,
            "start_date": "20102025",
            "end_date": "20102025"
        },
        "Rows": [
            {
                "Site Name": "Example Site",
                "Report Date": "2025-10-20T00:00:00",
                "Time Period Ending": "00:14:00",
                "Avg mph": "",  #empty string
                "Total Volume": "100"
            },
            {
                "Site Name": "Example Site",
                "Report Date": "2025-10-20T00:00:00",
                "Time Period Ending": "00:29:00",
                "Avg mph": "55",
                "Total Volume": ""  #empty string
            },
            {
                "Site Name": "Example Site",
                "Report Date": "2025-10-20T00:00:00",
                "Time Period Ending": "00:44:00",
                "Avg mph": "",  #both empty
                "Total Volume": ""
            }
        ]
    }

@pytest.fixture
def invalid_observations_api_response():

    return {
        "Header": {
            "row_count": 1,
            "start_date": "20102025",
            "end_date": "20102025"
        },
        #missing 'Rows' key
    }

@pytest.fixture
def invalid_date_api_response():

    return {
        "Header": {
            "row_count": 1,
            "start_date": "20102025",
            "end_date": "20102025"
        },
        "Rows": [
            {
                "Site Name": "Example Site",
                "Report Date": "2025/10/20",  #invalid format
                "Time Period Ending": "00:14:00",
                "Avg mph": "65",
                "Total Volume": "182"
            }
        ]
    }


@pytest.fixture
def api_response_single_record():

    return {
        "Header": {
            "row_count": 1,
            "start_date": "21102025",
            "end_date": "21102025"
        },
        "Rows": [
            {
                "Site Name": "Example Site",
                "Report Date": "2025-10-21T00:00:00",
                "Time Period Ending": "12:00:00",
                "Avg mph": "60",
                "Total Volume": "500"
            }
        ]
    }


@pytest.fixture
def api_response_empty():

    return {
        "Header": {
            "row_count": 0,
            "start_date": "22102025",
            "end_date": "22102025"
        },
        "Rows": []
    }


@pytest.fixture
def sample_observations():

    return [
        TrafficObservation(
            site_name="Example Site",
            report_date=date(2025, 10, 19),
            time_period_ending=time(0, 14, 0),
            avg_speed=65,
            total_volume=182
        ),
        TrafficObservation(
            site_name="Example Site",
            report_date=date(2025, 10, 19),
            time_period_ending=time(0, 29, 0),
            avg_speed=70,
            total_volume=150
        ),
        TrafficObservation(
            site_name="Example Site",
            report_date=date(2025, 10, 19),
            time_period_ending=time(0, 44, 0),
            avg_speed=None,  #missing data
            total_volume=120
        ),
        TrafficObservation(
            site_name="Example Site",
            report_date=date(2025, 10, 19),
            time_period_ending=time(1, 14, 0),
            avg_speed=55,
            total_volume=300
        ),
        TrafficObservation(
            site_name="Example Site",
            report_date=date(2025, 10, 19),
            time_period_ending=time(1, 29, 0),
            avg_speed=60,
            total_volume=320
        ),
        TrafficObservation(
            site_name="Example Site",
            report_date=date(2025, 10, 19),
            time_period_ending=time(8, 0, 0),
            avg_speed=45,
            total_volume=800  #peak hour
        ),
    ]

@pytest.fixture
def sample_observations_no_speed_or_volume():

    return [
        TrafficObservation(
            site_name="Example Site",
            report_date=date(2025, 10, 19),
            time_period_ending=time(0, 14, 0),
            avg_speed=None,
            total_volume=None
        ),
        TrafficObservation(
            site_name="Example Site",
            report_date=date(2025, 10, 19),
            time_period_ending=time(0, 29, 0),
            avg_speed=None,
            total_volume=None
        )
    ]

@pytest.fixture
def sample_observations_diff_dates():

    return [
        TrafficObservation(
            site_name="Example Site",
            report_date=date(2025, 10, 18),
            time_period_ending=time(0, 14, 0),
            avg_speed=None,
            total_volume=None
        ),
        TrafficObservation(
            site_name="Example Site",
            report_date=date(2025, 10, 19),
            time_period_ending=time(0, 29, 0),
            avg_speed=None,
            total_volume=None
        )
    ]

@pytest.fixture
def sample_observations_same_time():

    return [
        TrafficObservation(
            site_name="Example Site",
            report_date=date(2025, 10, 19),
            time_period_ending=time(0, 14, 0),
            avg_speed=None,
            total_volume=None
        ),
        TrafficObservation(
            site_name="Example Site",
            report_date=date(2025, 10, 19),
            time_period_ending=time(0, 14, 0),
            avg_speed=None,
            total_volume=None
        )
    ]

@pytest.fixture
def populated_site(sample_observations):

    site = SingleSite(site_id=461, site_name="Example Site")
    site.observations = sample_observations
    return site

@pytest.fixture
def populated_site_no_speed_or_volume(sample_observations_no_speed_or_volume):

    site = SingleSite(site_id=461, site_name="Example Site")
    site.observations = sample_observations_no_speed_or_volume
    return site

class TestAPIClient:
    
    def test_parse_response_valid(self, valid_api_response):

        client = APIClient(connector=MockAPIConnector(response_data=valid_api_response))
        observations = client.parse_json_response(json_data=client.connector.response_data)

        assert len(observations) == 4
        assert observations[0].site_name == "Example Site"
        assert observations[0].report_date == date(2025, 10, 19)
        assert observations[0].time_period_ending == time(0, 14, 0)
        assert observations[0].avg_speed == 65
        assert observations[0].total_volume == 182
    
    def test_parse_response_missing_data(self, api_response_with_missing_data):

        client = APIClient(connector=MockAPIConnector(response_data=api_response_with_missing_data))
        observations = client.parse_json_response(json_data=client.connector.response_data)

        assert len(observations) == 3
        assert observations[0].avg_speed is None
        assert observations[1].total_volume is None
        assert observations[2].avg_speed is None
        assert observations[2].total_volume is None
    
    def test_parse_response_single_record(self, api_response_single_record):

        client = APIClient(connector=MockAPIConnector(response_data=api_response_single_record))
        observations = client.fetch_daily_data(site_id=461, date="21102025")

        assert len(observations) == 1
        assert observations[0].site_name == "Example Site"
        assert observations[0].report_date == date(2025, 10, 21)
        assert observations[0].time_period_ending == time(12, 0, 0)
        assert observations[0].avg_speed == 60
        assert observations[0].total_volume == 500

    def test_parse_response_empty(self, api_response_empty):

        client = APIClient(connector=MockAPIConnector(response_data=api_response_empty))
        observations = client.fetch_daily_data(site_id=461, date="21102025")

        assert len(observations) == 0
    
    def test_parse_invalid_date(self, invalid_date_api_response):

        client = APIClient(connector=MockAPIConnector(response_data=invalid_date_api_response))

        with pytest.raises(ValueError, match=f"Invalid day: 34"):
            client.fetch_daily_data(site_id=461, date="34102025")

        with pytest.raises(ValueError, match=f"Invalid month: 13"):
            client.fetch_daily_data(site_id=461, date="20132025")

        with pytest.raises(ValueError, match=f"Year out of reasonable range: 2019"):
            client.fetch_daily_data(site_id=461, date="20102019")

        with pytest.raises(ValueError, match=f"Date must be 8 characters in format DDMMYYYY, got: 2001020256"):
            client.fetch_daily_data(site_id=461, date="2001020256")
        
        with pytest.raises(ValueError, match=f"Invalid date format: 22102098"):
            client.fetch_daily_data(site_id=461, date="22102098")

class TestSingleSite:
    
    def test_fetch_data_populates_observations(self, valid_api_response):

        client = APIClient(connector=MockAPIConnector(response_data=valid_api_response))
        site = SingleSite(site_id=461, site_name="Example")
        site.fetch_data(client=client, date="19102025")

        assert len(site.observations) == 4
        assert site.observations[0].site_name == "Example Site"

    def test_calculate_avg_speed(self, populated_site):

        expected_avg = (65 + 70 + 55 + 60 + 45) / 5
        assert populated_site.calculate_avg_speed() == expected_avg
    
    def test_calculate_avg_speed_no_valid(self, populated_site_no_speed_or_volume):

        assert populated_site_no_speed_or_volume.calculate_avg_speed() is None
    
    def test_calculate_total_volume(self, populated_site):

        expected_total = 182 + 150 + 120 + 300 + 320 + 800
        assert populated_site.calculate_total_volume() == expected_total

    def test_calculate_total_volume_no_valid(self, populated_site_no_speed_or_volume):

        assert populated_site_no_speed_or_volume.calculate_total_volume() == 0

    def test_calculate_avg_speed_for_hour(self, populated_site):
        
        expected_avg = (55 + 60) / 2
        
        assert expected_avg == populated_site.calculate_avg_speed_for_hour(hour=1)
        assert None == populated_site.calculate_avg_speed_for_hour(hour=2)

    def test_calculate_total_volume_for_hour(self, populated_site):
        
        expected_total = 300 + 320
        
        assert expected_total == populated_site.calculate_total_volume_for_hour(hour=1)
        assert 0 == populated_site.calculate_total_volume_for_hour(hour=2)

    def test_calculate_avg_speed_for_hour_no_valid(self, populated_site_no_speed_or_volume):
        
        with pytest.raises(ValueError, match=f"Hour must be between 0 and 23, got -1"):
            populated_site_no_speed_or_volume.calculate_avg_speed_for_hour(hour=-1)
        with pytest.raises(ValueError, match=f"Hour must be between 0 and 23, got 24"):
            populated_site_no_speed_or_volume.calculate_avg_speed_for_hour(hour=24)

    def test_calculate_total_volume_for_hour_no_valid(self, populated_site_no_speed_or_volume):
        
        with pytest.raises(ValueError, match=f"Hour must be between 0 and 23, got -1"):
            populated_site_no_speed_or_volume.calculate_total_volume_for_hour(hour=-1)
        with pytest.raises(ValueError, match=f"Hour must be between 0 and 23, got 24"):
            populated_site_no_speed_or_volume.calculate_total_volume_for_hour(hour=24)

    def test_find_peak_hour(self, populated_site):
        
        peak_hour = populated_site.find_peak_hour()
        
        assert peak_hour == 8
    
    def test_find_peak_hour_no_data(self, populated_site_no_speed_or_volume):
        
        peak_hour = populated_site_no_speed_or_volume.find_peak_hour()
        
        assert peak_hour is None

    def test_iteration_over_observations(self, populated_site):

        assert list(iter(populated_site)) == list(iter(populated_site.observations))

    def test_length_of_site(self, populated_site):

        assert len(populated_site) == len(populated_site.observations)

    def test_representation(self, populated_site):

        repr_str = repr(populated_site)
        assert "SingleSite(id=461, name='Example Site', observations=6)" == repr_str

class TestTrafficObservation:
    
    def test_comparison(self, sample_observations):

        assert sample_observations[0] < sample_observations[1]
        assert not (sample_observations[1] < sample_observations[0])
        assert sample_observations[0] < sample_observations[2]

    def test_comparison_different_dates(self, sample_observations_diff_dates):

        assert sample_observations_diff_dates[0] < sample_observations_diff_dates[1]
        assert not (sample_observations_diff_dates[1] < sample_observations_diff_dates[0])

    def test_comparison_equal_dates(self, sample_observations_same_time):

        assert not (sample_observations_same_time[0] < sample_observations_same_time[1])
        assert not (sample_observations_same_time[1] < sample_observations_same_time[0])
        assert sample_observations_same_time[0] == sample_observations_same_time[1]

    def test_representation(self, sample_observations):

        repr_str = repr(sample_observations[0])
        assert "TrafficObservation(name=Example Site, date=2025-10-19, time=00:14:00, speed=65, volume=182)" == repr_str

