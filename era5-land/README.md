# Making The Other Stew

This file documents the steps I take to produce the meteorological forcing files for WRF-Hydro. I modified the WRF-Hydro Meteorological Forcing Engine (MFE) code available [here](https://github.com/NCAR/WrfHydroForcing) to process ERA5-land data.

## Preprocessing

- run `get_era5_land.py` to fetch the data from CDS.
- run `grib_filter split.rule *.grib` to generate the `an` and `fc` grib files for each day. NOTE: do not process the grib files one by one, do it in one command because the downloaded files from CDS each contains one month worth of data but it starts on 00 UTC of the first day and ends on 23 UTC of the last day of the month. And `grib_filter` somehow takes OO UTC data to be the last record of a given day. So if you do not do all the months in one shot, the first output from a given month (1 record) would overwrite the last output from the previous month (23 records).
- run `grib1_to_unpacked_nc.py` to convert the `fc` grib data to .nc files and unpack them.
- run `preprocess_era5_land.py` to produce the input needed for MFE from the .nc files generated in the previous step.
- run `create_hgt.py` to generate the `hgt.nc` file for the surface height field needed by MFE for downscaling.

These are the variables needed in the so-called `LDASIN` files (according to MFE):

```python
        output_variable_attribute_dict = {
            'U2D': [0,'m s-1','x_wind','10-m U-component of wind','time: point',0.001,0.0,3],
            'V2D': [1,'m s-1','y_wind','10-m V-component of wind','time: point',0.001,0.0,3],
            'LWDOWN': [2,'W m-2','surface_downward_longwave_flux',
                       'Surface downward long-wave radiation flux','time: point',0.001,0.0,3],
            'RAINRATE': [3,'mm s^-1','precipitation_flux','Surface Precipitation Rate','time: mean',1.0,0.0,0],
            'T2D': [4,'K','air_temperature','2-m Air Temperature','time: point',0.01,100.0,2],
            'Q2D': [5,'kg kg-1','surface_specific_humidity','2-m Specific Humidity','time: point',0.000001,0.0,6],
            'PSFC': [6,'Pa','air_pressure','Surface Pressure','time: point',0.1,0.0,1],
            'SWDOWN': [7,'W m-2','surface_downward_shortwave_flux',
                       'Surface downward short-wave radiation flux','time: point',0.001,0.0,3],
            'LQFRAC': [8, '%', 'liquid_water_fraction', 'Fraction of precipitation that is liquid vs. frozen',
                       'time: point', 0.1, 0.0, 3]
```

The last one, `LQFRAC`, I am not sure whether it is actually needed. But `ERA5-land` data I downloaded should be able to provide it using `SNOWFALL` and `TOTAL PRECIPITATION`.

`ERA5-land` provides only 2-m dew point temperature. It is converted to specific humidity.

In MFE, `LWDOWN` and `SWDOWN` are output with the attribute `time:point`. But `ERA5-land` provides those two as accumulated values over the short forecast time (from 00 UTC to the current validity time). "RAINRATE" in MFE is output with "time:mean". But I wonder if it is the mean value over the time between the current output step and the previous one or some other mean value, e.g., the mean value over the hour centered on the current output time? 

For "LWDOWN" and "SWDOWN" we can first calculate the mean values over the ERA5-land forecast output steps (the step interval is one hour) and use those mean values as the mid-step or mid-hour values to interpolate to the step or hour values.

I have implemented both options for "LWDOWN", "SWDOWN" and "RAINRATE" in `preprocess_era5_land.py`. 

## MFE

### Bias-Correction

ERA5-land documentation claims that some bias correction to the forcing data driving the land surface model (lapse-rate correction) is already done.

### Downscaling

"Downscaling" seems to be doing similar things as "Bias-correction" but from the forcing data grid/elevation to the WRF-Hydro grid/elevation (from `geo_em_d*.nc`). I added code to read in the surface height from ERA5-land to MFE in case we need to use it for downscaling.
