import pandas as pd
import numpy as np
import pvlib
from pvlib.temperature import sapm_cell
from pvlib.pvsystem import PVSystem
from pvlib.modelchain import ModelChain
from pvlib.location import Location

def simulate_energy_output(weather_df, lat, lon, tilt, azimuth, system_size_kw):
    """
    Simulate energy output using pvlib.
    Returns monthly energy output (kWh) and processed weather data.
    """

    # Parse datetime from weather
    weather_df['time'] = pd.to_datetime(weather_df[['Year', 'Month', 'Day', 'Hour']])
    weather_df.set_index('time', inplace=True)
    
    # Required weather inputs
    weather = weather_df.rename(columns={
        'G(i)': 'ghi', 
        'Gb(i)': 'dni', 
        'Gd(i)': 'dhi', 
        'T2m': 'temp_air', 
        'WS10m': 'wind_speed'
    })[['ghi', 'dni', 'dhi', 'temp_air', 'wind_speed']]

    # Define PV system
    module_parameters = {
        'pdc0': system_size_kw * 1000,  # W
        'gamma_pdc': -0.004  # 1/°C
    }
    temperature_model_parameters = pvlib.temperature.TEMPERATURE_MODEL_PARAMETERS['sapm']['open_rack_glass_glass']

    pv_system = PVSystem(
        surface_tilt=tilt,
        surface_azimuth=azimuth,
        module_parameters=module_parameters,
        temperature_model_parameters=temperature_model_parameters
    )

    # Define location
    location = Location(lat, lon, tz='UTC')

    # Model chain
    mc = ModelChain(pv_system, location, aoi_model='physical', spectral_model='no_loss')
    mc.run_model(weather)

    # AC output in watts → kWh
    ac_power = mc.ac.fillna(0)
    energy_kwh = ac_power.resample('M').sum() / 1000

    monthly_energy = energy_kwh.to_frame(name='Energy (kWh)')
    monthly_energy.index = monthly_energy.index.strftime('%B')

    return monthly_energy, weather

