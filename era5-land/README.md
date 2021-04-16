# Making the other Stew

This file documents the steps I take to produce the meteorological forcing files for WRF-Hydro. I am modelling my workflow on the WRF-Hydro Meteorological Forcing Engine (MFE) code available [here](https://github.com/NCAR/WrfHydroForcing).

## Input-Output Mapping

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

`ERA5-land` provides only 2-m dew point temperature. I will have to convert that to specific humidity.

I have downloaded the land-sea mask and surface geopotential height for `ERA5-land` in case we need them for the subsequent steps.

In MFE, `LWDOWN` and `SWDOWN` are output with the attribute `time:point`. But `ERA5-land` provides those two as accumulated values over the short forecast time (from 00 UTC to the current validity time). "RAINRATE" in MFE is output with "time:mean". But I wonder if it is mean over the time between the current output step and the previous one or some other mean?

For "LWDOWN" and "SWDOWN" we can first calculate the mean values over the ERA5-land forecast output steps (the step interval is one hour) and use those mean values as the mid-step or mid-hour values to interpolate to the step or hour values.

## Regridding

I am not sure if I should just use `metgrid.exe` for regridding or adapt the regridding code in the `MFE`. Some considerations here are:

- ERA5-land data is already on a regular $0.1 \times 0.1$ deg lat-lon grid. I wonder how the regridding is done.
- There are more interpolation options in `metgrid`.
- But the regridding code in the `MFE` is cleaner with more controls available.

## Bias-Correction

ERA5-land documentation claims that some bias correction to the forcing data driving the land surface model (lapse-rate correction) is already done.

## Downscaling

"Downscaling" seems to be doing similar things as "Bias-correction" but from the forcing data grid/elevation to the WRF-Hydro grid/elevation.
