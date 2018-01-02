#!/bin/bash
#SBATCH --job-name=trackWhiskers
#SBATCH --partition=savio2
#SBATCH --qos=savio_normal
#SBATCH --account=fc_adesnik
#SBATCH --ntasks=20
#SBATCH --mem-per-cpu=3G
#SBATCH --time=12:00:00
#SBATCH --mail-type=end
#SBATCH --mail-user=elyall@berkeley.edu
#SBATCH --output=/global/home/users/elyall/Logs/WT-%j.out
#SBATCH --error=/global/home/users/elyall/Errors/WT-%j.err
source /usr/Modules/init/bash
export PATH="/global/home/users/elyall/Code/whisk/build:$PATH" # add whisk binaries to path
cd ~/Code/whisk/ # change to main folder

# SET DIRECTORY TO ANALYZE
export DIR="/global/scratch/elyall/test"


# ANALYZE FILES
module load matlab
matlab -nodisplay << EOF
addpath('matlab');   % add parWhisk to path
parpool('local', 20);% start parallel pool
Dir = getenv('DIR'); % get folder name
parWhisk(Dir);       % process files in parallel
exit
EOF

# CONVERT FILES TO STANDARDIZED FORMATS
module load python/2.7.8 tables/3.1.1 # load python 2 & tables
export PYTHONPATH="/global/home/users/elyall/Code/:$PYTHONPATH" # add whisk python modules to path
# python python/batch.py $DIR -e "trace" -f "*.tif"
python python/whiskers2hdf5.py $DIR
python python/measurements2mat.py $DIR

