#!/bin/tcsh
#
#SBATCH --job-name=Colabfold
#SBATCH --open-mode=append
##SBATCH --time=2-00:00:00
#SBATCH --mail-type=FAIL
#SBATCH --partition=gpu
#SBATCH --ntasks=1
##SBATCH --cpus-per-task=XXCPUSXX #set by user
##SBATCH --mem=XXMEMXX #set by user
##SBATCH --gres=gpu:XXGPUSXX #set by user
##SBATCH --error=XXERRORXX #set by user
##SBATCH --output=XXOUTPUTXX #set by user

##################
#CONSTANTS

set TOOLS = /cephfs/public/ColabFold/colabfoldconda
set ENV = $TOOLS/envs/colabfold
set PYTHONPATH = $ENV/bin/python3.8
set PYTHONSCRIPT = /cephfs/public/ColabFold/lmb/utils/run_colabfold.py

###################
#Dependencies

setenv MODULEPATH /public/com/modules
module load cuda/11.2.2

set NUMGPUS=$4

if ($NUMGPUS == 1) then
    set DEVICES = "0"
else if ($NUMGPUS == 2) then
    set DEVICES = "0,1"
else if ($NUMGPUS == 3) then
    set DEVICES = "0,1,2"
else if ($NUMGPUS == 4) then
    set DEVICES = "0,1,2,3"
endif

setenv CUDA_VISIBLE_DEVICES $DEVICES
setenv LD_LIBRARY_PATH $TOOLS/lib:$LD_LIBRARY_PATH
setenv TF_FORCE_UNIFIED_MEMORY 1
setenv XLA_PYTHON_CLIENT_MEM_FRACTION 4.0

#############
#Openmpi

if ("/public/EM/OpenMPI/openmpi-2.0.1/build/bin/mpirun" != "`which mpirun`") then
        set path=(/public/EM/OpenMPI/openmpi-2.0.1/build/bin $path)
endif

if ("1" == "$?LD_LIBRARY_PATH") then
        if ("$LD_LIBRARY_PATH" !~ */public/EM/OpenMPI/openmpi-2.0.1/build/lib*) then
                setenv LD_LIBRARY_PATH /public/EM/OpenMPI/openmpi-2.0.1/build/lib:$LD_LIBRARY_PATH
        endif
else
        setenv LD_LIBRARY_PATH /public/EM/OpenMPI/openmpi-2.0.1/build/lib
endif

###################
#Activate alphafold

$TOOLS/bin/activate $ENV

###################
#Get sequence

set SEQUENCE = `cat $1`

###################
#User info

echo
echo "------------------------------------------"
echo "Job parameters:"
echo "------------------------------------------"
echo
echo "Job name: "$2
echo
echo "Output directory: "$5
echo
echo "Stitched sequence:"
echo $SEQUENCE
echo
echo "Number of models: "$3
echo
echo "Number of recycles: "$6
echo
echo "Use amber: "$7
echo
echo "Use templates: "$8
echo
echo "------------------------------------------"
echo "Colabfold log:"
echo "------------------------------------------"
echo "(it may take a minute to start)"
echo
echo "Also check log.txt."
echo
echo "To cancel this job, use: scancel $SLURM_JOB_ID."
echo

###################
#Submit command

mpiexec --oversubscribe $PYTHONPATH $PYTHONSCRIPT --sequence=$SEQUENCE --jobname=$2 --num_models=$3 --output=$5 --num_recycles=$6 --use_amber=$7 --use_templates=$8

echo
echo "Memory usage:"
echo

sstat -j $SLURM_JOB_ID.batch --format="JobID,MaxRSS%20"

echo

exit 0
