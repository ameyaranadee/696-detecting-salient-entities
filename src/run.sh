#!/bin/bash
#SBATCH --partition=gpu            # Partition to submit to
#SBATCH --time=8:00:00             # Maximum job duration
#SBATCH --cpus-per-task=4          # Number of CPU cores
#SBATCH --mem=40G                  # Memory in GB
#SBATCH --gpus=1                   # Number of GPUs
#SBATCH --constraint=vram40        # Extra Slurm constraint
#SBATCH --output=slurm-%j.out      # Standard output and error log
#SBATCH --mail-type=BEGIN,END,FAIL # Notifications for job start, end, and failure
#SBATCH --mail-user=aranade@umass.edu

module load conda/latest
conda activate intro

echo "Running job on node: $(hostname)"
echo "Job ID: $SLURM_JOB_ID"

python pointwise_entity_linking.py \
  --input_csv data/WN-salience-val-NER-output.csv.csv \
  --kb_path kb/filtered_kb.json \
  --output_dir results/EL \
  --batch_size 7500