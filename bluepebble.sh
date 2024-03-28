#!/bin/env bash

#SBATCH --account=sscm012844
#SBATCH --job-name=paper
#SBATCH --output=paper
#SBATCH --error=paper
#SBATCH --partition=short
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=28
#SBATCH --time=2-12:00:00
#SBATCH --mem=100000M
#SBATCH --array=1-8

# Load the modules/environment
module purge
module load lang/python/anaconda/3.7-2019.03


# Define working directory
export WORK_DIR=/user/work/fo18103/PredictionOfDHealthInSR

# Change into working directory
cd ${WORK_DIR}
source goat/bin/activate

# Do some stuff
echo JOB ID: ${SLURM_JOBID}
echo PBS ARRAY ID: ${SLURM_ARRAY_TASK_ID}
echo Working Directory: $(pwd)

cmds=('ml.py --no-export-hpc-string --study-id delmas --output-dir output/main_experiment/rbf/delmas_dataset4_mrnn_7day/delmas_dataset4_mrnn_7day_delmas_RepeatedKFold_1_2_QN_ANSCOMBE_LOG/2To2 --dataset-folder datasets/delmas_dataset4_mrnn_7day --n-imputed-days 1 --n-activity-days 2 --syhth-thresh 7 --n-job 1 --cv RepeatedKFold --preprocessing-steps QN --preprocessing-steps ANSCOMBE --preprocessing-steps LOG --class-healthy-label 1To1 --class-unhealthy-label 2To2 --meta-columns label --meta-columns id --meta-columns imputed_days --meta-columns date --meta-columns health --meta-columns target --classifiers rbf --enable-regularisation' 'ml.py --no-export-hpc-string --study-id cedara --output-dir output/main_experiment/rbf/cedara_datasetmrnn7_23/cedara_datasetmrnn7_23_cedara_RepeatedKFold_1_2_QN_ANSCOMBE_LOG/2To2 --dataset-folder datasets/cedara_datasetmrnn7_23 --n-imputed-days 1 --n-activity-days 2 --syhth-thresh 7 --n-job 1 --cv RepeatedKFold --preprocessing-steps QN --preprocessing-steps ANSCOMBE --preprocessing-steps LOG --class-healthy-label 1To1 --class-unhealthy-label 2To2 --meta-columns label --meta-columns id --meta-columns imputed_days --meta-columns date --meta-columns health --meta-columns target --classifiers rbf --enable-regularisation' 'ml.py --no-export-hpc-string --study-id delmas --output-dir output/main_experiment/rbf/delmas_dataset4_mrnn_7day/delmas_dataset4_mrnn_7day_delmas_RepeatedKFold_1_4_QN_ANSCOMBE_LOG/2To2 --dataset-folder datasets/delmas_dataset4_mrnn_7day --n-imputed-days 1 --n-activity-days 4 --syhth-thresh 7 --n-job 1 --cv RepeatedKFold --preprocessing-steps QN --preprocessing-steps ANSCOMBE --preprocessing-steps LOG --class-healthy-label 1To1 --class-unhealthy-label 2To2 --meta-columns label --meta-columns id --meta-columns imputed_days --meta-columns date --meta-columns health --meta-columns target --classifiers rbf --enable-regularisation' 'ml.py --no-export-hpc-string --study-id cedara --output-dir output/main_experiment/rbf/cedara_datasetmrnn7_23/cedara_datasetmrnn7_23_cedara_RepeatedKFold_1_4_QN_ANSCOMBE_LOG/2To2 --dataset-folder datasets/cedara_datasetmrnn7_23 --n-imputed-days 1 --n-activity-days 4 --syhth-thresh 7 --n-job 1 --cv RepeatedKFold --preprocessing-steps QN --preprocessing-steps ANSCOMBE --preprocessing-steps LOG --class-healthy-label 1To1 --class-unhealthy-label 2To2 --meta-columns label --meta-columns id --meta-columns imputed_days --meta-columns date --meta-columns health --meta-columns target --classifiers rbf --enable-regularisation' 'ml.py --no-export-hpc-string --study-id delmas --output-dir output/main_experiment/rbf/delmas_dataset4_mrnn_7day/delmas_dataset4_mrnn_7day_delmas_RepeatedKFold_1_7_QN_ANSCOMBE_LOG/2To2 --dataset-folder datasets/delmas_dataset4_mrnn_7day --n-imputed-days 1 --n-activity-days 7 --syhth-thresh 7 --n-job 1 --cv RepeatedKFold --preprocessing-steps QN --preprocessing-steps ANSCOMBE --preprocessing-steps LOG --class-healthy-label 1To1 --class-unhealthy-label 2To2 --meta-columns label --meta-columns id --meta-columns imputed_days --meta-columns date --meta-columns health --meta-columns target --classifiers rbf --enable-regularisation' 'ml.py --no-export-hpc-string --study-id cedara --output-dir output/main_experiment/rbf/cedara_datasetmrnn7_23/cedara_datasetmrnn7_23_cedara_RepeatedKFold_1_7_QN_ANSCOMBE_LOG/2To2 --dataset-folder datasets/cedara_datasetmrnn7_23 --n-imputed-days 1 --n-activity-days 7 --syhth-thresh 7 --n-job 1 --cv RepeatedKFold --preprocessing-steps QN --preprocessing-steps ANSCOMBE --preprocessing-steps LOG --class-healthy-label 1To1 --class-unhealthy-label 2To2 --meta-columns label --meta-columns id --meta-columns imputed_days --meta-columns date --meta-columns health --meta-columns target --classifiers rbf --enable-regularisation' 'ml.py --no-export-hpc-string --study-id delmas --output-dir output/main_experiment/rbf/delmas_dataset4_mrnn_7day/delmas_dataset4_mrnn_7day_delmas_RepeatedKFold_6_7_QN_ANSCOMBE_LOG/2To2 --dataset-folder datasets/delmas_dataset4_mrnn_7day --n-imputed-days 6 --n-activity-days 7 --syhth-thresh 7 --n-job 1 --cv RepeatedKFold --preprocessing-steps QN --preprocessing-steps ANSCOMBE --preprocessing-steps LOG --class-healthy-label 1To1 --class-unhealthy-label 2To2 --meta-columns label --meta-columns id --meta-columns imputed_days --meta-columns date --meta-columns health --meta-columns target --classifiers rbf --enable-regularisation' 'ml.py --no-export-hpc-string --study-id cedara --output-dir output/main_experiment/rbf/cedara_datasetmrnn7_23/cedara_datasetmrnn7_23_cedara_RepeatedKFold_6_7_QN_ANSCOMBE_LOG/2To2 --dataset-folder datasets/cedara_datasetmrnn7_23 --n-imputed-days 6 --n-activity-days 7 --syhth-thresh 7 --n-job 1 --cv RepeatedKFold --preprocessing-steps QN --preprocessing-steps ANSCOMBE --preprocessing-steps LOG --class-healthy-label 1To1 --class-unhealthy-label 2To2 --meta-columns label --meta-columns id --meta-columns imputed_days --meta-columns date --meta-columns health --meta-columns target --classifiers rbf --enable-regularisation' )
# Execute code
echo ${cmds[${SLURM_ARRAY_TASK_ID}]}
python ${cmds[${SLURM_ARRAY_TASK_ID}]} > ${WORK_DIR}/${SLURM_ARRAY_TASK_ID}.log
