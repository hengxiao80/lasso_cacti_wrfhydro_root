import os
from netCDF4 import Dataset as ds
import numpy as np

top_dir = "/ccs/home/h1x/scratchp/wrfhydro_cacti/wrfhydro2wrfinput/modified"
hydro_dir = "/ccs/home/h1x/scratchp/wrfhydro_cacti/wrfhydro_run"
days = {
        "20190122":{"gefs1deg_en18":["thom_k150ptop11_dzbot25_dzsts1.05_dzstu1.05"],
                    "gefs1deg_en14":["thom_k150ptop11_dzbot25_dzsts1.05_dzstu1.05"]},
        "20190123":{"era5eda_en02":["thom_k150ptop11_dzbot25_dzsts1.05_dzstu1.05"],
                    "gefs1deg_en06":["thom_k150ptop11_dzbot25_dzsts1.05_dzstu1.05"]},
        "20190125":{"era5eda_en01":["thom_k150ptop11_dzbot25_dzsts1.05_dzstu1.05"],
                    "era5eda_en00":["thom_k150ptop11_dzbot25_dzsts1.05_dzstu1.05"]},
        "20190129":{"era5eda_en00":["thom_k150ptop11_dzbot25_dzsts1.05_dzstu1.05"],
                    "era5eda_en08":["thom_k150ptop11_dzbot25_dzsts1.05_dzstu1.05"]},
    }

'''
Variables in wrfinput_d0* that need replacing:

EROD
TSLB
SMOIS
SH2O
SMCREL
SNOW
SNOWH
CANWAT
FNDSNOWH
FNDSOILW
FNDALBSI
FNDSNOWSI
FNDICEDEPTH
LAKE_DEPTH
TSK

TSLB lake values are just zero in wrfinput_d*.
SMOIS lake values are also zero.
SH2O and SMCREL are all just zero, so not used.
CANWAT is also zero.
BUT SNOW and SNOWH are not zero. WHY is SNOWC zero then?

Curious things observed:
1. The soil moisture and temperature in one of the wrfinput_d0* from EDA is noticably different from those in ERA5-land.
2. WRF-Hydro (with Noah-MP) also produces snow depth, snow water equivalent etc. but seems quite different from ERA5-EDA data in wrfinput_d0*.
3. Cannot initialize Noah-MP canopy water using ERA5-land.

The modification procedure is now as follows,
1. We repalce TSLB with SOIL_T, SMOIS with SOIL_M and TSK with TG from WRF-Hydro.
2. We also make use of the Lake mask, where it is lake, no replacement.
'''

for day, runs in days.items():
    for bdy, setups in runs.items():
        for setup in setups:
            run_dir = "run{:s}_{:s}".format(day, setup)
            for dom in ["d01", "d02"]:
                f = "wrfinput_{:s}".format(dom)
                wrfinput = ds(os.path.join(top_dir, day, bdy, run_dir, f), mode='r+')
                f = '{:s}0000.LDASOUT_DOMAIN{:s}'.format(day, dom[-1])
                hydro = ds(os.path.join(hydro_dir, 'run01_{:s}'.format(dom), 'out', f))
                soil_t = hydro['SOIL_T'][:]
                tg = hydro['TG'][:]
                soil_m = hydro['SOIL_M'][:]
                lakemask = wrfinput['LAKEMASK'][:]
                tslb = wrfinput['TSLB']
                smois = wrfinput['SMOIS']
                tsk = wrfinput['TSK']
                for i in range(4):
                    tslb[0,i,:,:] = np.where(lakemask < 0.1, soil_t[0,:,i,:], tslb[0,i,:,:])
                    smois[0,i,:,:] = np.where(lakemask < 0.1, soil_m[0,:,i,:], smois[0,i,:,:])
                tsk[0,:,:] = np.where(lakemask < 0.1, tg[0,:,:], tsk[0,:,:])
                hydro.close()
                wrfinput.close()