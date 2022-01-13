import os
import os.path
import re
import hashlib
import sys

from colabfold.download import download_alphafold_params, default_data_dir
from colabfold.utils import setup_logging
from colabfold.batch import get_queries, run
from pathlib import Path

#######################################################
##########      Added by Sami      ####################
########## Colabfold 1.2.0 compatible #################
#######################################################

import getopt

opts, args = getopt.getopt(sys.argv[1:],"s:j:m:o:r:a:t",["sequence=", "jobname=", "num_models=", "output=", "num_recycles=", "use_amber=", "use_templates="])

result_dir="." 
num_recycles=3 
use_amber="False" 
use_templates = "False"
paramsdir = "/cephfs/public/ColabFold/colabfoldconda/envs/colabfold/lib/python3.8/site-packages/alphafold/data"

#not added as options yet
stop_at_score=float(100) 
zip_results = False
keep_existing_results = False
msa_mode = "MMseqs2 (UniRef+Environmental)"
use_msa = True
use_env = True 

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
         num_recycles = int(arg)
    elif opt == "--use_amber":
         use_amber = arg
    elif opt == "--use_templates":
         use_templates = arg

if use_amber == "True":
    use_amber = True
elif use_amber == "False":
    use_amber= False

if use_templates == "True":
    use_templates = True
elif use_templates == "False":
    use_templates = False

#######################################################
#######################################################

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

queries_path=f"{result_dir}/{jobname}.csv"

with open(f"{result_dir}/{jobname}.log", "w") as text_file: #Changed by Sami
    text_file.write("num_models=%s\n" % num_models)
    text_file.write("num_recycles=%s\n" % num_recycles)
    text_file.write("use_amber=%s\n" % use_amber)
    text_file.write("use_msa=%s\n" % use_msa)
    text_file.write("msa_mode=%s\n" % msa_mode)
    text_file.write("use_templates=%s\n" % use_templates)

a3m_file = f"{result_dir}/{jobname}.a3m" #Changed by Sami

#######################################################

setup_logging(Path(result_dir).joinpath("log.txt")) #Changed by Sami
queries, is_complex = get_queries(queries_path)

###
#Changed by Sami. we already have the params in alphafold/data/params. Set data_dir=paramsdir below
#download_alphafold_params(is_complex, Path(result_dir))
####

#Originally the order was models 3, 4, 5, 1, 2

run(
    queries=queries,
    result_dir=result_dir,
    use_templates=use_templates,
    use_amber=use_amber,
    msa_mode=msa_mode,
    model_type="auto",
    num_models=num_models,
    num_recycles=num_recycles,
    model_order=[1, 2, 3, 4, 5],
    is_complex=is_complex,
    data_dir=paramsdir,
    keep_existing_results=keep_existing_results,
    rank_by="auto",
    pair_mode="unpaired+paired",
    stop_at_score=stop_at_score,
    zip_results=zip_results,
)#Changed by Sami