#!/bin/bash

#SBATCH -A cli120
#SBATCH -J wrfhydro
#SBATCH -p priority_batch
#SBATCH -N 2
#SBATCH -t 6:00:00
#SBATCH -o wrfhydro.out
#SBATCH -e wrfhydro.err

cd  /gpfs/wolf/cli120/proj-shared/h1x/wrfhydro_cacti/wrfhydro_run/run01_d03
date
srun -n 72 -N 2 ./wrf_hydro_NoahMP.exe
date
