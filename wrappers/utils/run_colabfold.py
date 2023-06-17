import os
import os.path
import re
import hashlib
import sys

from colabfold.download import download_alphafold_params, default_data_dir
from colabfold.utils import setup_logging
from colabfold.batch import get_queries, run, set_model_type
from pathlib import Path

#######################################################
###########      Sami Chaaban      ####################
########## ColabFold 1.5.2 compatible #################
#######################################################

import getopt
import shutil

opts, args = getopt.getopt(sys.argv[1:],"s:j:m:o:r:a:t:c:x:p:v:q:n:b:l",["sequence=", "jobname=", "num_models=", "output=", "num_recycles=", "use_amber=", "use_templates=", "custom_template=", "custom_msa=", "pair_mode=", "multimer_version=", "recycle_stop=", "max_msa=", "use_dropout=", "num_seeds="])

result_dir="." 
num_recycles="auto" 
recycle_stop="auto"
use_dropout=False
num_seeds=1

use_amber="False" 
use_templates = "False"
custom_template = "none"
custom_msa = "none"
pair_mode = "unpaired_paired"
model_type = "auto"
max_msa = "none"

#not added as options yet
stop_at_score=float(100) 
keep_existing_results = False
msa_mode = "mmseqs2_uniref_env"
use_msa = True
use_env = True
model_order = [1,2,3,4,5]
rank_by = "auto"

paramsdir = "/cephfs2/public/ColabFold5/colabfoldconda/envs/colabfold/lib/python3.8/site-packages/alphafold/data"

for opt,arg in opts:
    if opt == "--sequence":
        query_sequence = arg
    elif opt == "--jobname":
        jobname = arg
    elif opt == "--num_models":
        num_models = int(arg)
    elif opt == "--output":
        result_dir = arg
    elif opt == "--num_recycles":
        num_recycles = arg
    elif opt == "--use_amber":
        use_amber = arg
    elif opt == "--use_templates":
        use_templates = arg
    elif opt == "--custom_template":
        custom_template = arg
    elif opt == "--custom_msa":
        custom_msa = arg
    elif opt == "--pair_mode":
        pair_mode = arg
    elif opt == "--multimer_version":
        multimer_version = arg
    elif opt == "--recycle_stop":
        recycle_stop = arg
    elif opt == "--max_msa":
        max_msa = arg
    elif opt == "--use_dropout":
        use_dropout = arg
    elif opt == "--num_seeds":
        num_seeds = int(arg)

if num_recycles == "auto":
    num_recycles = None
else:
    num_recycles = int(num_recycles)

if recycle_stop == "auto":
    recycle_stop = None
else:
    recycle_stop = float(recycle_stop)

if use_amber in ["True", "true"]:
    num_relax = num_models
elif use_amber in ["False", "false"]:
    num_relax = 0

if use_templates in ["True", "true"]:
    use_templates = True
elif use_templates in ["False", "false"]:
    use_templates = False

if custom_template == "none":
    custom_template_path = None
else:
    custom_template_path = custom_template
    use_templates = True

if use_dropout in ["True", "true"]:
    use_dropout = True
elif use_dropout in ["False", "false"]:
    use_dropout = False

if max_msa == "none":
    max_msa = None
elif max_msa in ["16-32", "32-64", "64-128", "256-512", "512-1024"]:
    max_msa = max_msa.replace("-", ":")

#Only if multimer_version is not set to auto
if multimer_version == "1":
    model_type = "alphafold2_multimer_v1"
elif multimer_version == "2":
    model_type = "alphafold2_multimer_v2"
elif multimer_version == "3":
    model_type = "alphafold2_multimer_v3"

def add_hash(x,y):
  return x+"_"+hashlib.sha1(y.encode()).hexdigest()[:5]
# remove whitespaces
query_sequence = "".join(query_sequence.split())
# remove whitespaces
jobname = "".join(jobname.split())
jobname = re.sub(r'\W+', '', jobname)
jobname = add_hash(jobname, query_sequence)

with open(f"{result_dir}/{jobname}.csv", "w") as text_file: #Changed by Sami
    text_file.write(f"id,sequence\n{jobname},{query_sequence}")

a3m_file = f"{result_dir}/{jobname}.a3m"
queries_path=f"{result_dir}/{jobname}.csv" #this gets reassigned to a3m file later if using custom msa

if custom_msa == "none":
    msa_mode = "mmseqs2_uniref_env"
else:
    msa_mode = "custom"
    a3m_file = f"{result_dir}/{jobname}.custom.a3m"
    header = 0
    import fileinput
    for line in fileinput.FileInput(custom_msa,inplace=1):
        if line.startswith(">"):
            header = header + 1
        if not line.rstrip():
            continue
        if line.startswith(">") == False and header == 1:
            query_sequence = line.rstrip()
        print(line, end='')
    shutil.copy(custom_msa, a3m_file)
    queries_path=a3m_file

#######################################################

setup_logging(Path(result_dir).joinpath("log.txt"))

queries, is_complex = get_queries(queries_path)
model_type = set_model_type(is_complex, model_type) #useful when model_type is set to auto

if "multimer" in model_type and max_msa is not None:
    use_cluster_profile = False
else:
    use_cluster_profile = True

with open(f"{result_dir}/colabfoldoptions.txt", "w") as text_file: #added by Sami
    text_file.write("\nresult_dir: "+ result_dir)
    text_file.write("\nuse_templates: "+ str(use_templates))
    if custom_template_path == None:
        text_file.write("\ncustom_template_path: None")
    else:
        text_file.write("\ncustom_template_path: " + custom_template)
    text_file.write("\nnum_relax: "+ str(num_relax))
    text_file.write("\nmsa_mode: "+ msa_mode)
    text_file.write("\nmodel_type: "+ model_type)
    text_file.write("\nnum_models: "+ str(num_models))
    if num_recycles == None:
        text_file.write("\nnum_recycles: None")    
    else:
        text_file.write("\nnum_recycles: "+ str(num_recycles))
    if recycle_stop == None:
        text_file.write("\nrecycle_early_stop_tolerance: None")    
    else:
        text_file.write("\nrecycle_early_stop_tolerance: "+ str(recycle_stop))
    text_file.write("\nnum_seeds: "+ str(num_seeds))
    text_file.write("\nuse_dropout: "+ str(use_dropout))
    text_file.write("\nmodel_order: "+ str(model_order))
    text_file.write("\nis_complex: "+ str(is_complex))
    text_file.write("\ndata_dir: "+ paramsdir)
    text_file.write("\nkeep_existing_results: "+ str(keep_existing_results))
    text_file.write("\nrank_by: "+ rank_by)
    text_file.write("\npair_mode: "+ pair_mode)
    text_file.write("\nstop_at_score: "+ str(stop_at_score))
    if max_msa == None:
        text_file.write("\nmax_msa: None")    
    else:
        text_file.write("\nmax_msa: "+ str(max_msa))
    text_file.write("\nuse_cluster_profile: "+ str(use_cluster_profile))


run(
    queries=queries,
    result_dir=result_dir,
    use_templates=use_templates,
    custom_template_path=custom_template_path,
    num_relax=num_relax,
    msa_mode=msa_mode,
    model_type=model_type,
    num_models=num_models,
    num_recycles=num_recycles,
    recycle_early_stop_tolerance=recycle_stop,
    num_seeds=num_seeds,
    use_dropout=use_dropout,
    model_order=model_order,
    is_complex=is_complex,
    data_dir=paramsdir,
    keep_existing_results=keep_existing_results,
    rank_by=rank_by,
    pair_mode=pair_mode,
    stop_at_score=stop_at_score,
    max_msa=max_msa,
    use_cluster_profile=use_cluster_profile
    
)#Changed by Sami

#######################################################
