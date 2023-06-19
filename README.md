# Colabfold Slurm setup

Instructions in `Installation Steps.txt`

The workflow is:

1. bin/colabfold5 takes in user input and passes it to utils/submit_colabfold_cluster.csh
2. utils/submit_colabfold_cluster.csh submits utils/run_colabfold.py to the cluster
3. utils/run_colabfold.py runs the job

See also https://github.com/sokrypton/ColabFold
