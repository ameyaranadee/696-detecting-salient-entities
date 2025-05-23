#!/bin/bash
#SBATCH --partition=gpu            # Partition to submit to
#SBATCH --time=6:00:00             # Maximum job duration
#SBATCH --cpus-per-task=4          # Number of CPU cores
#SBATCH --mem=40G                  # Memory in GB
#SBATCH --gpus=1                   # Number of GPUs
#SBATCH --constraint=vram40        # Extra Slurm constraint
#SBATCH --output=slurm-%j.out      # Standard output and error log
#SBATCH --mail-type=BEGIN,END,FAIL # Notifications for job start, end, and failure
#SBATCH --mail-user=aranade@umass.edu99

module load conda/latest
conda activate intro

cd $SLURM_SUBMIT_DIR/..

export PYTHONPATH=$PWD:$PYTHONPATH

echo "Running job on node: $(hostname)"
echo "Job ID: $SLURM_JOB_ID"

# python3 src/pointwise_entity_linking.py
python3 src/contextual_entity_linking.py