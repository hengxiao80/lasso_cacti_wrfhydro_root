"""
This script preprocesses the .nc files generated from the *.fc_sfc.grib1 files
using grib_to_netcdf utility (eccodes) to conform with the requirements of the
WRF-Hydro MFE input.
"""

from datetime import datetime, timedelta
import subprocess
import os
from netCDF4 import Dataset
from numba import vectorize, float64
from cftime import date2num
import numpy as np


def td_to_sh_mfe(p, td):
    """
    function to calculate specific humidity (kg/kg) from pressure (p in Pa) and dewpoint
    temperature (td in K)

    follow the algorithm used in the MFE, which uses mixhum_ptrh in NCL, I think
    """
    T0 = 273.15
    EP = 0.622
    ONEMEP = 0.378
    ES0 = 6.11
    A = 17.269
    B = 35.86

    est = ES0 * np.exp(A * (td - T0) / (p / 100.0 - B))
    rst = (EP * est) / (p / 100.0 - ONEMEP * est)
    sh = rst / (1.0 + rst)
    return sh


start_time = datetime.strptime("201808010000", "%Y%m%d%H%M")
end_time = datetime.strptime("201809010000", "%Y%m%d%H%M")
interval = timedelta(seconds=3600)

"""
It is not clear to me what "mean" means in the MFE output.
For RAINRATE, we are supposed to provide a mean value.
I don't know if it is the mean over the previous hour or over the hour
centered on the current output time.
For DSWRF, DLWRF, we are supposed to provide a point value.
But ERA5-land 'ssrd' and 'strd' are accumulated over the forecast time. So to
provide an instantaneous value at the output time, I first calculate the mean
values in the hours just before and after the output time and then average the
two to get a value at the output time. But strictly speaking this value is
also a mean value. But we will have to live with that.
"""
# input acc: "point", "point", "point", "point", "point", "acc", "acc", "acc"
in_names = ["t2m", "d2m", "u10", "v10", "sp", "tp", "ssrd", "strd"]
conversion = [1.0, 1.0, 1.0, 1.0, 1.0, 1.0e3, 1.0, 1.0]
# averaging method choices
# output acc  "point", "point", "point", "point", "point", "mean", "point", "point"
out_names = ["T2D", "Q2D", "U10", "V10", "PRES", "RAINRATE", "DSWRF", "DLWRF"]
out_longnames = [
    "2-m Air Temperature",
    "2-m Specific Humidity",
    "10-m U-component of wind",
    "10-m V-component of wind",
    "Surface Pressure",
    "Surface Precipitation Rate",
    "Surface downward short-wave radiation flux",
    "Surface downward long-wave radiation flux",
]
out_units = ["K", "kg kg^-1", "m s^-1", "m s^-1", "Pa", "mm s^-1", "W m^-2", "W m^-2"]
no_avg, prev_hour_avg, curr_hour_avg = 0, 1, 2
out_avg = [
    no_avg,
    no_avg,
    no_avg,
    no_avg,
    no_avg,
    curr_hour_avg,
    curr_hour_avg,
    curr_hour_avg,
]

out_time = start_time
in_template = "no_lake_data/ecmf_{:s}_fc_sfc_unpacked.nc"
while out_time <= end_time:
    print(" Processing ", out_time, " ...")
    # open the input files
    if out_time.hour == 0:
        in_file = in_template.format((out_time - interval).strftime("%Y%m%d"))
        in_data = Dataset(in_file, "r")
        in_file_2 = in_template.format(out_time.strftime("%Y%m%d"))
        in_data_2 = Dataset(in_file_2, "r")
    else:
        in_file = in_template.format(out_time.strftime("%Y%m%d"))
        in_data = Dataset(in_file, "r")
        in_file_2 = None
        in_data_2 = None
    # print("in_data:", in_data)
    # print("in_data_2:", in_data_2)
    # now output files
    out_file = "mfe_input/era5land.hourly." + out_time.strftime("%Y%m%d%H") + ".nc"
    out_data = Dataset(out_file, "w")
    # create the dimensions and dimension variables in the output file
    for name, dimension in in_data.dimensions.items():
        if name == "time":
            _ = out_data.createDimension(name, None)
            _ = out_data.createVariable(
                name, in_data[name].datatype, in_data[name].dimensions
            )
            out_data[name].setncatts(in_data[name].__dict__)
            out_time_num = date2num(
                out_time,
                units=out_data["time"].units,
                calendar=out_data["time"].calendar,
            )
            out_data[name][:] = out_time_num
            out_ind = np.where(in_data[name] == out_time_num)[0]
        else:
            _ = out_data.createDimension(name, len(dimension))
            _ = out_data.createVariable(
                name, in_data[name].datatype, in_data[name].dimensions
            )
            out_data[name].setncatts(in_data[name].__dict__)
            # reverse the order in the y direction
            if name == "latitude":
                out_data[name][:] = in_data[name][::-1]
            else:
                out_data[name][:] = in_data[name][:]
    # loop through the output variables
    for i, out_name in enumerate(out_names):
        in_name = in_names[i]
        _ = out_data.createVariable(
            out_name, in_data[in_name].datatype, in_data[in_name].dimensions
        )
        # copy variable attributes all at once via dictionary
        out_data[out_name].setncatts(in_data[in_name].__dict__)
        out_data[out_name].units = out_units[i]
        out_data[out_name].long_name = out_longnames[i]
        if out_name in ["T2D", "U10", "V10", "PRES"]:
            out_data[out_name][:] = in_data[in_name][out_ind, ::-1, :] * conversion[i]
        elif out_name == "Q2D":
            out_data[out_name][:] = (
                td_to_sh_mfe(
                    in_data["sp"][out_ind, ::-1, :], in_data["d2m"][out_ind, ::-1, :]
                )
                * conversion[i]
            )
        elif out_name in ["DSWRF", "DLWRF", "RAINRATE"]:
            if out_avg[i] == prev_hour_avg:
                if out_time.hour == 1:
                    out_data[out_name][:] = (
                        in_data[in_name][out_ind, ::-1, :]
                        * conversion[i]
                        / float(interval.seconds)
                    )
                else:
                    out_data[out_name][:] = (
                        (
                            in_data[in_name][out_ind, ::-1, :]
                            - in_data[in_name][out_ind - 1, ::-1, :]
                        )
                        * conversion[i]
                        / float(interval.seconds)
                    )
            elif out_avg[i] == curr_hour_avg:
                if out_time.hour == 0:
                    out_data[out_name][:] = (
                        (
                            in_data[in_name][out_ind, ::-1, :]
                            - in_data[in_name][out_ind - 1, ::-1, :]
                            + in_data_2[in_name][0, ::-1, :]
                        )
                        * conversion[i]
                        / float(interval.seconds)
                        / 2.0
                    )
                elif out_time.hour == 1:
                    out_data[out_name][:] = (
                        in_data[in_name][out_ind + 1, ::-1, :]
                        * conversion[i]
                        / float(interval.seconds)
                        / 2.0
                    )
                else:
                    out_data[out_name][:] = (
                        (
                            in_data[in_name][out_ind + 1, ::-1, :]
                            - in_data[in_name][out_ind - 1, ::-1, :]
                        )
                        * conversion[i]
                        / float(interval.seconds)
                        / 2.0
                    )
        # zero out negative downward shortwave fluxes and rain rates 
        if out_name in ["DSWRF", "RAINRATE"]:
            out_data[out_name][:] = np.where(out_data[out_name][:] > 0.0, out_data[out_name][:], 0.0)
    # close the files
    in_data.close()
    if in_data_2 != None:
        in_data_2.close()
    out_data.close()
    # move forward
    out_time += interval
