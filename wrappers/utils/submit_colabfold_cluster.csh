#!/bin/tcsh
#
#SBATCH --job-name=ColabFold5
#SBATCH --open-mode=append
##SBATCH --time=2-00:00:00
#SBATCH --mail-type=FAIL
#SBATCH --ntasks=1
##SBATCH --partition=gpu
##SBATCH --cpus-per-task=XXCPUSXX #set by user
##SBATCH --mem=XXMEMXX #set by user
##SBATCH --gres=gpu:XXGPUSXX #set by user
##SBATCH --error=XXERRORXX #set by user
##SBATCH --output=XXOUTPUTXX #set by user

##################
#CONSTANTS

set TOOLS = /cephfs2/public/ColabFold5/colabfoldconda
set ENV = $TOOLS/envs/colabfold
set PYTHONPATH = $ENV/bin/python3.8
set PYTHONSCRIPT = /cephfs2/public/ColabFold5/lmb/utils/run_colabfold.py
set COLABFOLDVERSION = "ColabFold 1.5.2"

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

#nvidia-smi -L

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

echo $COLABFOLDVERSION
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
echo "Recycle stop: "${13}
echo
echo "Max MSA: "${14}
echo
echo "Use dropout: "${15}
echo
echo "Number of seeds: "${16}
echo
echo "Use amber: "$7
echo
echo "Use templates: "$8
echo
echo "Custom template: "$9
echo
echo "Custom MSA: "${10}
echo
echo "Pair mode: "${11}
echo
echo "Multimer version: "${12}
echo
echo "------------------------------------------"
echo "Colabfold log:"
echo "------------------------------------------"
echo
echo "This file will update as the prediction proceeds"
echo "It may take a minute to start"
echo
echo "It is useful to run tail -f Colabfold.out to watch the log as it updates"
echo "You can also check log.txt and colabfoldoptions.txt"
echo
echo "If you want to cancel this job, run scancel $SLURM_JOB_ID"
echo

###################
#Submit command

echo >> $5/submitcommand.txt
echo "mpiexec command:" >> $5/submitcommand.txt
echo "mpiexec --oversubscribe" $PYTHONPATH $PYTHONSCRIPT "--sequence="$SEQUENCE" --jobname="$2" --num_models="$3" --output="$5" --num_recycles="$6" --use_amber="$7" --use_templates="$8" --custom_template="$9" --custom_msa="${10}" --pair_mode="${11}" --multimer_version="${12}" --recycle_stop="${13}" --max_msa="${14}" --use_dropout="${15}" --num_seeds="${16}  >> $5/submitcommand.txt

mpiexec --oversubscribe $PYTHONPATH $PYTHONSCRIPT --sequence=$SEQUENCE --jobname=$2 --num_models=$3 --output=$5 --num_recycles=$6 --use_amber=$7 --use_templates=$8 --custom_template=$9 --custom_msa=${10} --pair_mode=${11} --multimer_version=${12} --recycle_stop=${13} --max_msa=${14} --use_dropout=${15} --num_seeds=${16}

echo

exit 0
