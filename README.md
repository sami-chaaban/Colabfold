# Colabfold Slurm setup

Instructions in `Installation Steps.txt`

The workflow is:
-bin/colabfold5 takes in user input and passes it to utils/submit_colabfold_cluster.csh
-utils/submit_colabfold_cluster.csh submits utils/run_colabfold.py to the cluster
-utils/run_colabfold.py runs the job

See also https://github.com/sokrypton/ColabFold
