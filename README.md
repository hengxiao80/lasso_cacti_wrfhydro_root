# LASSO CACTI WRF-Hydro workflow

## Create `wrfinput` for WRF-Hydro

See [README_create_wrfinput4wrf.md](README_create_wrfinput4wrf.md) for the steps to create `wrfinput` files for WRF-Hydro.

## Create meteorological forcing for WRF-Hydro

See [README_create_meteor_forcing_4_wrfhydro.md](README_create_meteor_forcing_4_wrfhydro.md) for the steps to create meteorological forcing files for WRF-Hydro.

## Running WRF-Hydro

This is actually the most straightforward step. The setup files used are all in the `wrfhydro_run` directory.

## Updating `wrfinput` for actual WRF runs using output from WRF-Hydro

This is done in the `wrfhydro4wrfinput` directory using `wrfinput_mod.py`.

## Validation

See [README_validation.md](README_validation.md) for various validations we have done.


