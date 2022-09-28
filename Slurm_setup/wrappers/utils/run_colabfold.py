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
########## Colabfold 1.3.0 compatible #################
#######################################################

import getopt
import shutil

opts, args = getopt.getopt(sys.argv[1:],"s:j:m:o:r:a:t:c:x:p:v",["sequence=", "jobname=", "num_models=", "output=", "num_recycles=", "use_amber=", "use_templates=", "custom_template=", "custom_msa=", "pair_mode=", "multimer_version="])

result_dir="." 
num_recycles=3 
use_amber="False" 
use_templates = "False"
custom_template = "none"
custom_msa = "none"
pair_mode = "unpaired+paired"
model_type = "auto"

#not added as options yet
stop_at_score=float(100) 
zip_results = False
keep_existing_results = False
msa_mode = "MMseqs2 (UniRef+Environmental)"
use_msa = True
use_env = True

paramsdir = "/cephfs/public/ColabFold2/colabfoldconda/envs/colabfold/lib/python3.8/site-packages/alphafold/data"

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
    elif opt == "--custom_template":
         custom_template = arg
    elif opt == "--custom_msa":
         custom_msa = arg
    elif opt == "--pair_mode":
         pair_mode = arg
    elif opt == "--multimer_version":
         multimer_version = arg

if use_amber in ["True", "true"]:
    use_amber = True
elif use_amber in ["False", "false"]:
    use_amber = False

if use_templates in ["True", "true"]:
    use_templates = True
elif use_templates in ["False", "false"]:
    use_templates = False

if custom_template == "none":
    custom_template_path = None
else:
    custom_template_path = custom_template
    use_templates = True

if pair_mode == "unpaired-paired":
    pair_mode = "unpaired+paired"

if multimer_version == "1":
    model_type = "AlphaFold2-multimer-v1"
elif multimer_version == "2":
    model_type = "AlphaFold2-multimer-v2"

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
    msa_mode = "MMseqs2 (UniRef+Environmental)"
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

###
#We already have the params in alphafold/data/params. Set data_dir=paramsdir below
#download_alphafold_params(is_complex, Path(result_dir))
####

run(
    queries=queries,
    result_dir=result_dir,
    use_templates=use_templates,
    use_amber=use_amber,
    msa_mode=msa_mode,
    model_type=model_type,
    num_models=num_models,
    num_recycles=num_recycles,
    model_order=[1,2,3,4,5],
    is_complex=is_complex,
    data_dir=paramsdir,
    keep_existing_results=keep_existing_results,
    rank_by="auto",
    pair_mode=pair_mode,
    stop_at_score=stop_at_score,
    zip_results=zip_results,
    custom_template_path=custom_template_path
)#Changed by Sami

#Model order used to be 3, 4, 5, 1, 2

#######################################################
