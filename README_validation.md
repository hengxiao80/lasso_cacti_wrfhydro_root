# README

## Data for validation of WRF-Hydro output against ERA5-land

- ERA5-land original data
    - `/ccs/home/h1x/scratchp/wrfhydro_cacti/era5-land/no_lake_data/`
        - Forecast, e.g., `ecmf_20190312_fc_sfc_unpacked.nc`
        - Analysis, e.g., `ecmf_20190312_an_sfc_unpacked.nc`

- ERA5-land data regridded on to WRF grid (created by [this code](https://code.arm.gov/lasso/lasso-cacti/regrid_era5land.git))
    - `/ccs/home/h1x/scratchp/wrfhydro_cacti/era5-land/regridded`
        - e.g., `swvl3_201808121800.nc`

- WRF-Hydro test simulation
    - `/ccs/home/h1x/scratchp/wrfhydro_cacti/wrfhydro_run/out`
        - e.g., `201808240100.LDASOUT_DOMAIN1`

## Forcing data used by WRF-Hydro

- Input to MFE (created from ERA5-land data by `preprocess_era5_land.py`)
    - `/ccs/home/h1x/scratchp/wrfhydro_cacti/era5-land/mfe_input`
        - e.g., `era5land.hourly.2018081610.nc`

- Output from MFE (input to WRF-Hydro)
    - `/ccs/home/h1x/scratchp/wrfhydro_cacti/wrfhydro_forcing/2018080100`
        - e.g., `201808231900.LDASIN_DOMAIN1`

## Topography data from WRF and ERA5-land

- Geogrid output from CACTI WRF setup
    - `/ccs/home/h1x/scratchp/wrfhydro_cacti/geogrid`
        - e.g., `geo_em.d01.nc`

- topography in ERA5-land:
    - `/ccs/home/h1x/scratchp/wrfhydro_cacti/era5-land/mfe_input/hgt.nc`

## Initial condition used by WRF-hydro

- `wrfinput_d01`
    - `/ccs/home/h1x/scratchp/wrfhydro_cacti/create_wrfinput`

- `metgrid.exe` output used for `wrfinput_d01` generation (created from ERA5-land data using the usual WPS procedure)
    - `/ccs/home/h1x/scratchp/wrfhydro_cacti/metgrid4wrfinput/met_em.d01.2018-08-01_01:00:00.nc`

## WRF-Hydro soil layers

- From `namelist.hrldas`

```
! Soil layer specification
NSOIL=4
soil_thick_input(1) = 0.10
soil_thick_input(2) = 0.30
soil_thick_input(3) = 0.60
soil_thick_input(4) = 1.00
```

- From `hydro.namelist`

```
! Specify the number of soil layers (integer) and the depth of the bottom of each layer... (meters)
! Notes: In Version 1 of WRF-Hydro these must be the same as in the namelist.input file.
!      Future versions will permit this to be different.
NSOIL=4
ZSOIL8(1) = -0.10
ZSOIL8(2) = -0.40
ZSOIL8(3) = -1.00
ZSOIL8(4) = -2.00
```

- From the `wrfinput_d01` file created by `create_wrfinput.py`

```
 DZS =
  0.1, 0.3, 0.6, 1 ;
```

## ERA5-land soil layers

- From ERA5-land online documentation

```
The ECMWF Integrated Forecasting System model has a four-layer representation of soil:
Layer 1: 0 - 7cm
Layer 2: 7 - 28cm
Layer 3: 28 - 100cm
Layer 4: 100 - 289cm
```

