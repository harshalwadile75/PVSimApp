import requests
import pandas as pd
from io import StringIO

def fetch_pvgis_tmy(lat, lon):
    """
    Fetch TMY weather data from PVGIS.
    Returns: Pandas DataFrame or error message
    """
    url = (
        "https://re.jrc.ec.europa.eu/api/tmy?"
        f"lat={lat}&lon={lon}&outputformat=csv&browser=1"
    )
    try:
        response = requests.get(url)
        if response.status_code == 200:
            csv_data = response.text
            df = pd.read_csv(StringIO(csv_data), skiprows=10)
            return df
        else:
            return None
    except Exception as e:
        return None
