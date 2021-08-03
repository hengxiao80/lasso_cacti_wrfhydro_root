import subprocess
import os

src_top_dir = "/gpfs/wolf/cli120/proj-shared/d3m088/cacti/domains/setup4_smoothedPass1-1000/"
desc_top_dir = "/ccsopen/home/h1x/scratch/wrfhydro_cacti/sensitivity_to_wrfhydro"
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

for day, runs in days.items():
    for bdy, setups in runs.items():
        for setup in setups:
            run_dir = "run{:s}_{:s}".format(day, setup)
            for f in ["wrfinput_d01", "wrfinput_d02"]:
                src = os.path.join(src_top_dir, day, bdy, run_dir, f)
                desc_dir = os.path.join(desc_top_dir, day, bdy, run_dir)
                desc = os.path.join(desc_dir, f)
                # print(src)
                # print(desc_dir)
                # print(desc)
                subprocess.call(['mkdir', '-p', desc_dir])
                subprocess.call(['cp', src, desc])