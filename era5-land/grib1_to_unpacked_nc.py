import glob
import subprocess
import os.path

# for file in sorted(glob.glob("no_lake_data/*_fc_sfc.grib1")):
for file in sorted(glob.glob("no_lake_data/*_an_sfc.grib1")):
    print(' Processing '+file)
    head, ext = os.path.splitext(file)
    subprocess.call(['grib_to_netcdf', '-o', head+'.nc', file])
    subprocess.call(['ncpdq', '-U', '-o', head+'_unpacked.nc', head+'.nc'])