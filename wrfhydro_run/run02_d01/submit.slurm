#!/usr/bin/bash

#SBATCH -A cli120
#SBATCH -J test
#SBATCH -N 1
#SBATCH -t 1:00:00
#SBATCH -o test.out
#SBATCH -e test.err

cd /ccs/home/h1x/scratchp/wrfhydro_cacti/wrfhydro_run/run02
date
srun -n 32 -N 1 ./wrf_hydro_NoahMP.exe
date
