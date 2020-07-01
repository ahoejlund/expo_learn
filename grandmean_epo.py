# -*- coding: utf-8 -*-
"""
Script for analyzing early vs. late responses to words and pseudowords
@author: Andreas Højlund (& Christelle Gansonre)
@email:  hojlund@cfin.au.dk
@github: https://github.com/ahoejlund/...
"""

#==============================================================================
# SYS PATH
#%%============================================================================

# adding the in-house versions of mne-python and stormdb-python to the sys path
import sys
sys.path.append('/projects/MINDLAB2018_MEG-Language-PD-DBS/misc/mne-python')
sys.path.append('/projects/MINDLAB2018_MEG-Language-PD-DBS/misc/stormdb-python')

#==============================================================================
# IMPORTS
#%%============================================================================

from os.path import join
import mne
from mne import io
import warnings
import os
import numpy as np
import matplotlib as mpl
mpl.use('Agg')
from matplotlib import pyplot as plt
from pylab import *
from sys import argv
from stormdb.access import Query

#%matplotlib wx

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

if __name__ == '__main__':  # only looks for command line inputs if script is called from command line
    gr   = int(argv[1])

groups = ['eld', 'pd']
group = groups[gr]
proj_name = 'MINDLAB2018_MEG-Language-PD-DBS'
scratch_folder = join('/projects', proj_name, 'scratch')
gm_folder = join(scratch_folder, 'intervals_GM')
misc_folder = join('/projects', proj_name, 'misc')
in_folder = join(scratch_folder, 'epoched_meg_' + group + '_100ms_bl')
subs = os.listdir(in_folder)

kinds = ['pseudos', 'reals']
targets = {'pseudos': ['slukke', 'slitte', 'spykke', 'svaette']}
targets['reals'] = ['slutte', 'slikke', 'spytte', 'svaekke']

for k, kind in enumerate(kinds):
    for t, target in enumerate(targets[kind]):
        epochs_list = []
        ntrials = []
        for s, cur_sub in enumerate(subs):
            epochs_folder = join(in_folder, cur_sub)
            epochs_path = join(epochs_folder, cur_sub[:4] + '_' + target + '_sem-epo.fif')
            epochs = mne.read_evokeds(epochs_path)[0]
            epochs_list.append(epochs)
            ntrials[s] = len(epochs)
        gm = mne.grand_average(evoked_list, interpolate_bads=True, drop_bads=False)
        out_file = join(gm_folder, target + '_10-ave.fif')
        gm.save(out_file)



        out_epo = join(gm_folder, target + '_10-epo.fif')
        gm.save(out_epo)
