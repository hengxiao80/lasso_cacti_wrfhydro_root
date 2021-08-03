"""
This script uses a `wrfinput_d*` file from either `create_wrfinput.R` or
`real.exe` as a template and fills in variables from the output of metgrid.exe
to create a new `wrfinput_d*` file for WRF-Hydro run initial conditions.

As I have not run WRF-Hydro, I don't know all the details yet. But I want
to set up a framework for ingesting and manipulating the netcdf files
(either `wrfinput_d*` or `met_em*`).
"""

from netCDF4 import Dataset
import numpy as np
from scipy.interpolate import interp1d

# template = Dataset('wrfinput_d01.nc', 'r+')
# met_data = Dataset('../metgrid4wrfinput/met_em.d01.2018-08-01_00:00:00.nc', 'r')
template = Dataset('wrfinput_d02.nc', 'r+')
met_data = Dataset('../metgrid4wrfinput/met_em.d02.2018-08-01_00:00:00.nc', 'r')

tslb = template.variables['TSLB']
smois = template.variables['SMOIS']
tmn = template.variables['TMN']
tsk = template.variables['TSK']
snow = template.variables['SNOW']

tsk_met = met_data.variables['SKINTEMP']
snow_met = met_data.variables['SNOW']
st_met = met_data.variables['ST']
sm_met = met_data.variables['SM']

tsk[:] = tsk_met[:]
snow[:] = snow_met[:]

"""
linearly interpolate soil moisture and temperature following the code in
subroutines `optional_input`, `optional_lsm_levels` in
`share/module_optional_input.F`
and `process_soil_real` in `share/module_soil_pre.F`.
"""
dzs = template.variables['DZS']
zs = template.variables['ZS']
zs_1d = zs[0,:]

zsi_met = met_data.variables['SOIL_LAYERS']
zsi_met_1d = zsi_met[0,:,0,0]
zsi_met_1d_flipped = zsi_met_1d[::-1]

zsi1 = np.insert(zsi_met_1d_flipped, 0, 0.0)
z_met_expanded = np.zeros(len(zsi_met_1d)+2, dtype = zs.dtype)
z_met_expanded[-1] = 3.0
z_met_expanded[1:-1] = (zsi1[:-1] + zsi1[1:])/2.0/100.0

nt, nz, ny, nx = tslb.shape

# put in tsk for z = 0 and tmn for z = 3 m
# put metgrid output (flipped) in the levels in between
st_met_expanded = np.zeros((nt,nz+2, ny, nx), dtype=tslb[:].dtype)
st_met_expanded[0,0,:,:] = tsk_met[0,:,:]
st_met_expanded[0,-1,:,:] = tmn[0,:,:]
st_met_expanded[0,1:-1,:,:] = st_met[0,::-1,:,:]

# put in values from the closest levels for z=0 and 3 m
# put metgrid output (flipped) in the levels in between
sm_met_expanded = np.zeros((nt,nz+2, ny, nx), dtype=smois[:].dtype)
sm_met_expanded[0,0,:,:] = sm_met[0,-1,:,:]
sm_met_expanded[0,-1,:,:] = sm_met[0,0,:,:]
sm_met_expanded[0,1:-1,:,:] = sm_met[0,::-1,:,:]

# linear interpolations
f = interp1d(z_met_expanded, st_met_expanded, kind='linear', axis=1)
tslb[:] = f(zs)
del f
f = interp1d(z_met_expanded, sm_met_expanded, kind='linear', axis=1)
smois[:] = f(zs)
del f

template.close()
met_data.close()
