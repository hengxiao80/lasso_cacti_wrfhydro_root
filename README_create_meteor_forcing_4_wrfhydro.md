# README

This file documents the steps I take to (1) download and preprocess the ERA5-land data and (2) produce the meteorological forcing files for WRF-Hydro using the WRF-Hydro Meteorological Forcing Engine (MFE) code available [here](https://github.com/NCAR/WrfHydroForcing) with my own modifications.


## Download and preprocess ERA5-land

- run `get_era5_land.py` to fetch the data from CDS.

- I also downloaded the ERA5-land land mask (`lsm_global.nc`) and surface geopotential (`sfc_geopot_global.nc`) data from CDS (by hand).

- run `grib_filter split.rule *.grib` to generate the `an` and `fc` grib files for each day. NOTE: do not process the grib files one by one, do it in one command because the downloaded files from CDS each contains one month worth of data but it starts on 00 UTC of the first day and ends on 23 UTC of the last day of the month. And `grib_filter` somehow takes OO UTC data to be the last record of a given day. So if you do not do all the months in one shot, the first output from a given month (1 record) would overwrite the last output from the previous month (23 records).

- run `grib1_to_unpacked_nc.py` to convert the `fc` grib data to .nc files and unpack them.

- run `preprocess_era5_land.py` to produce the input needed for MFE from the .nc files generated in the previous step.

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

- run `create_hgt.py` to generate the `hgt.nc` file for the surface height field needed by MFE for downscaling.

## MFE

My version of the WRF-Hydro Meteorological Forcing Engine (MFE) code is [here](https://code.arm.gov/lasso/lasso-cacti/wrfhydro_forcing_preparation.git).

### Bias-Correction

ERA5-land documentation claims that some bias correction to the forcing data driving the land surface model (lapse-rate correction) is already done.

### Downscaling

"Downscaling" seems to be doing similar things as "Bias-correction" but from the forcing data grid/elevation to the WRF-Hydro grid/elevation (from `geo_em_d*.nc`). I added code to read in the surface height from ERA5-land to MFE.

### `test.config`

This is the configuration file for MFE run. The version I am currently using is [here](https://code.arm.gov/lasso/lasso-cacti/wrfhydro_forcing_preparation/-/blob/era5land/test_d01.config?ref_type=heads). I don't quite understand the differences among `retrospective`, `forecast`, `reforecast` modes. I also don't think the code is actually fully setup to support all these modes. Currently, I just do the following:

```[Retrospective]
# Specify to process forcings in retrospective mode
# 0 - No
# 1 - Yes
RetroFlag = 0

# Choose the beginning date of processing forcing files.
# NOTE - Dates are given in YYYYMMDDHHMM format
# If in real-time forecasting mode, leave as -9999.
# These dates get over-ridden in lookBackHours.
BDateProc = 201808010000
EDateProc = 201809010000

[Forecast]
# Specify if this is an Analysis and Assimilation run (AnA).
# If this is AnA run, set AnAFlag = 1, otherwise 0.
# Setting this flag will change the behavior of some Bias Correction routines as well
# as the ForecastInputOffsets options (see below for more information)
AnAFlag = 0

# ONLY for realtime forecasting.
# - Specify a lookback period in minutes to process data.
#   This overrides any BDateProc/EDateProc options passed above.
#   If no LookBack specified, please specify -9999.
#LookBack = 4320
LookBack = -9999

# If running reforecasts, specify a window below. This will override 
# using the LookBack value to calculate a processing window.
# Specify -9999 if this is a real-time forecastinng instance
RefcstBDateProc = 201808010000
RefcstEDateProc = 201808010100

# Specify a forecast frequency in minutes. This value specifies how often
# to generate a set of forecast forcings. If generating hourly retrospective
# forcings, specify this value to be 60. 
ForecastFrequency = 60

# Forecast cycles are determined by splitting up a day by equal 
# ForecastFrequency interval. If there is a desire to shift the
# cycles to a different time step, ForecastShift will shift forecast
# cycles ahead by a determined set of minutes. For example, ForecastFrequency
# of 6 hours will produce forecasts cycles at 00, 06, 12, and 18 UTC. However,
# a ForecastShift of 1 hour will produce forecast cycles at 01, 07,
# 13, and 18 UTC. NOTE - This is only used by the realtime instance 
# to calculate forecast cycles accordingly. Re-forecasts will use the beginning
# and ending dates specified in conjunction with the forecast frequency
# to determine forecast cycle dates.  
ForecastShift = 0

# Specify how much (in minutes) of each input forcing is desires for each 
# forecast cycle. See documentation for examples. The length of
# this array must match the input forcing choices.
ForecastInputHorizons = [44640]

# This option is for applying an offset to input forcings to use a different
# forecasted interval. For example, a user may wish to use 4-5 hour forecasted
# fields from an NWP grid from one of their input forcings. In that instance
# the offset would be 4 hours, but 0 for other remaining forcings.
#
# In AnA runs, this value is the offset from the available forecast and 00z
# For example, if forecast are available at 06z and 18z, set this value to 6
ForecastInputOffsets = [0]
```

Both `RetroFlag` and `AnAFlag` are set to zero. `RefcstBDateProc`, `RefcstEDateProc` and `ForecastFrequency` are set so that we are just running one forecast cycle starting from `RefcstEDateProc`. `ForecastInputHorizons` actually controls the time period for which we are generating forcing. `OutputFrequency` seems to control the frequency of output. 

Probably should change this part of the original code to make it easier to understand and configure.
