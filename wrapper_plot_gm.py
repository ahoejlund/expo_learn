# -*- coding: utf-8 -*-
"""
Wrapper-script for analyzing early vs. late responses to words and pseudowords
@author: Andreas Højlund
@email:  hojlund@cfin.au.dk
@github: https://github.com/ahoejlund/...
"""
#==============================================================================
# SYS PATH
#%%============================================================================

# adding the in-house versions of mne-python and stormdb-python to the sys path
import sys
sys.path.append('/projects/MINDLAB2015_MEG-Sememene/misc/mne-python')
sys.path.append('/projects/MINDLAB2015_MEG-Sememene/misc/stormdb-python')

#==============================================================================
# IMPORTS
#%%============================================================================

import os
import subprocess
import socket
import numpy as np
import re
from os.path import join, basename
from stormdb.access import Query
from mne.io import Raw
import glob
from stormdb.cluster import ClusterBatch

#==============================================================================
# in-house versions of mne-python and stormdb-python - run only once!
#%%============================================================================

# cd /projects/MINDLAB2015_MEG-Sememene/misc
# git clone https://github.com/mne-tools/mne-python.git
# cd mne-python
# git checkout -b snapshot_20190612
#
# cd /projects/MINDLAB2015_MEG-Sememene/misc
# git clone https://github.com/meeg-cfin/stormdb-python.git
# cd stormdb-python
# git fetch origin refactor_submit:refactor_submit
# git checkout -b refactor_submit

#==============================================================================
# VARIABLES
#%%============================================================================

# SETUP PATHS AND PREPARE RAW DATA
hostname = socket.gethostname()
#cmd = "/usr/local/common/meeg-cfin/stormdb-python/bin/submit_to_cluster"

# definning project's folders
proj_name = 'MINDLAB2015_MEG-Sememene'
scratch_folder = join('/projects', proj_name, 'scratch')
scripts_folder = join('/projects', proj_name, 'scripts')
misc_folder = join('/projects', proj_name, 'misc')

scripts_path = join(scripts_folder, 'exposure_learning')
log_folder = join(scripts_path, 'qsub_logs')

targets = ['bide', 'mide', 'gide', 'nide']

# CHANGE DIR TO SAVE FILES THE RIGTH PLACE
#os.chdir(scripts_path)
os.chdir(log_folder)

cb = ClusterBatch(proj_name)

for target_ind, target in enumerate(targets):
    print('\nCurrent condition: {0:s} '.format(target))
    if target_ind >= 0:
        submit_cmd = "python %s/plot_gm.py %s" %(scripts_path, target)
        cb.add_job(cmd=submit_cmd, queue='short.q', n_threads=1)
        #cb.add_job(cmd=submit_cmd, queue='highmem.q', h_vmem='30G', job_name='ICA-wrapper')

cb.submit()
