#!/usr/bin/env python

from multiprocessing import Pool
from functools import partial
import cdsapi

def request_data(client, yr, mon):
    print("Requesting data for {}{:02d}".format(yr, mon))
    client.retrieve(
        'reanalysis-era5-land',
        {
            'format': 'grib',
            'year': str(yr),
            'variable': [
                '10m_u_component_of_wind', '10m_v_component_of_wind', '2m_dewpoint_temperature',
                '2m_temperature', 'evaporation_from_bare_soil', 'evaporation_from_open_water_surfaces_excluding_oceans',
                'evaporation_from_the_top_of_canopy', 'evaporation_from_vegetation_transpiration', 'forecast_albedo',
                'leaf_area_index_high_vegetation', 'leaf_area_index_low_vegetation',
                'potential_evaporation', 'runoff', 'skin_reservoir_content',
                'skin_temperature', 'snow_albedo', 'snow_cover',
                'snow_density', 'snow_depth', 'snow_depth_water_equivalent',
                'snow_evaporation', 'snowfall', 'snowmelt',
                'soil_temperature_level_1', 'soil_temperature_level_2', 'soil_temperature_level_3',
                'soil_temperature_level_4', 'sub_surface_runoff', 'surface_latent_heat_flux',
                'surface_net_solar_radiation', 'surface_net_thermal_radiation', 'surface_pressure',
                'surface_runoff', 'surface_sensible_heat_flux', 'surface_solar_radiation_downwards',
                'surface_thermal_radiation_downwards', 'temperature_of_snow_layer', 'total_evaporation',
                'total_precipitation', 'volumetric_soil_water_layer_1', 'volumetric_soil_water_layer_2',
                'volumetric_soil_water_layer_3', 'volumetric_soil_water_layer_4',
            ],
            'month': "{:02d}".format(mon),
            'day': [
                '01', '02', '03',
                '04', '05', '06',
                '07', '08', '09',
                '10', '11', '12',
                '13', '14', '15',
                '16', '17', '18',
                '19', '20', '21',
                '22', '23', '24',
                '25', '26', '27',
                '28', '29', '30',
                '31',
            ],
            'time': [
                '00:00', '01:00', '02:00',
                '03:00', '04:00', '05:00',
                '06:00', '07:00', '08:00',
                '09:00', '10:00', '11:00',
                '12:00', '13:00', '14:00',
                '15:00', '16:00', '17:00',
                '18:00', '19:00', '20:00',
                '21:00', '22:00', '23:00',
            ],
            'area': [
                -5, -105, -60,
                -30,
            ],
        },
        'era5_land.{}{:02d}.grib'.format(yr, mon))
    return

c = cdsapi.Client()

request_data_partial = partial(request_data, c)

y1, m1 = 2018, 7
y2, m2 = 2018, 7

stop = False
m2 += 1
if m2 == 13:
    y2 += 1
    m2 = 1
months = []
while not stop:
    months.append((y1, m1))
    m1 += 1
    if m1 == 13:
        y1 += 1
        m1 = 1
    stop = y1 == y2 and m1 == m2

print(months)

with Pool(len(months)) as p:
    p.starmap(request_data_partial, months)