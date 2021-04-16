from netCDF4 import Dataset
import numpy as np

f_in = Dataset("sfc_geopot_global.nc", "r")
f_ex = Dataset("mfe_input/era5land.hourly.2018080100.nc", "r")
f_out = Dataset("mfe_input/hgt.nc", "w")

for name, dimension in f_ex.dimensions.items():
    if name == "time":
        _ = f_out.createDimension(name, None)
    else:
        _ = f_out.createDimension(name, len(dimension))
    _ = f_out.createVariable(name, f_ex[name].datatype, f_ex[name].dimensions)
    f_out[name].setncatts(f_ex[name].__dict__)
    f_out[name][:] = f_ex[name][:]

hgt = f_out.createVariable("hgt", f_in["z"].datatype, ("time", "latitude", "longitude"))
hgt.setncatts(f_in['z'].__dict__)
hgt.units = "m"
hgt.long_name = "surface height"
del hgt.standard_name

y_ind = np.logical_and(f_in['latitude'][::-1] >=-60.0, f_in['latitude'][::-1] <= -5.0)
x_ind = np.logical_and((f_in['longitude'][:] - 360.0) >=-105.0, (f_in['longitude'][:] - 360.0) <= -30.0)
hgt[0,:,:] = (f_in['z'][0,::-1,:])[np.ix_(y_ind, x_ind)]/9.81

f_out.close()
f_in.close()
f_ex.close()