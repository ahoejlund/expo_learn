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
sys.path.append('/projects/MINDLAB2018_MEG-Language-PD-DBS/misc/mne-python/')
sys.path.append('/projects/MINDLAB2018_MEG-Language-PD-DBS/misc/stormdb-python/')

#==============================================================================
# IMPORTS
#%%============================================================================

import os
import subprocess
import socket
import numpy as np
import re
from os.path import join, basename
from mne.io import Raw
from stormdb.access import Query
import glob
from stormdb.cluster import ClusterBatch

#==============================================================================
# in-house versions of mne-python and stormdb-python - run only once!
#%%============================================================================

# cd /projects/MINDLAB2018_MEG-Language-PD-DBS/misc
# git clone https://github.com/mne-tools/mne-python.git
# cd mne-python
# git checkout -b snapshot_20190612
#
# cd /projects/MINDLAB2018_MEG-Language-PD-DBS/misc
# git clone https://github.com/meeg-cfin/stormdb-python.git
# cd stormdb-python
# git fetch origin refactor_submit:refactor_submit
# git checkout -b refactor_submit

#==============================================================================
# VARIABLES
#%%============================================================================

cmd = "submit_to_cluster"

# SETUP PATHS AND PREPARE RAW DATA
hostname = socket.gethostname()
#cmd = "/usr/local/common/meeg-cfin/stormdb-python/bin/submit_to_cluster"

# definning project's folders
proj_name = 'MINDLAB2018_MEG-Language-PD-DBS'
scratch_folder = join('/projects', proj_name, 'scratch')
scripts_folder = join('/projects', proj_name, 'scripts')
misc_folder = join('/projects', proj_name, 'misc')
scripts_path = join(scripts_folder, 'ah/exposure_learning')
log_folder = join(scripts_path, 'qsub_logs')

# CHANGE DIR TO SAVE FILES THE RIGTH PLACE
#os.chdir(scripts_path)
os.chdir(log_folder)

groups = ['eld', 'pd']

cb = ClusterBatch(proj_name)
#looping over groups and subjects' folders
for gr_ind, gr in enumerate(groups):
    # querying subject IDs based on folders in the epoch-folder
    epoch_folder = join(scratch_folder, 'epoched_meg_' + gr + '_100ms_bl')
    subs = os.listdir(epoch_folder)
    for sub_ind, sub in enumerate(subs):
        #print('\nCurrent subject: {0:s} (group: {1:s})\n'.format(sub, gr))
        submit_cmd = "python %s/expo_learn_sem.py %s %s" %(scripts_path, gr, sub)
        print(submit_cmd)
        #submit_cmd = "python expo_learn_sem.py %s %s" %(gr, sub)
        #print(submit_cmd)
        cb.add_job(cmd=submit_cmd, queue='short.q')
        # cb.add_job(cmd=submit_cmd, queue='short.q', n_threads=1)

    # for block_ind, block in enumerate(in_blocks):
    #     print('Current block: {0:s}'.format(block))
    #     submit_cmd = "python %s/expo_learn_sem.py %s %s" %(scripts_path, cur_sub, block_ind)
    #     if cur_sub=="0006" and block_ind==1:
    #         cb.add_job(cmd=submit_cmd, queue='short.q', n_threads=3)
    #     else:
    #         cb.add_job(cmd=submit_cmd, queue='short.q', n_threads=2)
    #         #cb.add_job(cmd=submit_cmd, queue='highmem.q', h_vmem='30G', job_name='ICA-wrapper')

cb.submit()
