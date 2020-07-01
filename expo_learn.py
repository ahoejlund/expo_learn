# -*- coding: utf-8 -*-
"""
Script for analyzing early vs. late responses to words and pseudowords
@author: Andreas Højlund (& )
@email:  hojlund@cfin.au.dk
@github: https://github.com/ahoejlund/...
"""

#==============================================================================
# SYS PATH
#%%============================================================================

# adding the in-house versions of mne-python and stormdb-python to the sys path
import sys
sys.path.append('/projects/MINDLAB2018_MEG-Language-PD-DBS/misc/mne-python')

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
    group   = argv[1]
    sub     = argv[2]

proj_name = 'MINDLAB2018_MEG-Language-PD-DBS'
scratch_folder = join('/projects', proj_name, 'scratch')
misc_folder = join('/projects', proj_name, 'misc')
blockno = '_block' + str(block+1)#block number going from 1 to 7
# blockno = '_block' + str(1)#block number going from 1 to 7
cur_sub = sub[:4]
# cur_sub = '0004'
in_folder = join(scratch_folder, ['epoched_meg_' + cur_group + '_100ms_bl'])
in_files = [f for f in os.listdir(in_folder) if blockno+"_" in f]
print(in_files)
#in_file = join(in_folder, filename)
#raw = mne.io.Raw(in_file, preload = True)
#raw.plot()

targets = ['slitte', ]

# misc > bad_chans > cur_sub...
# raw.info['bads'] = ['EEG0', 'EEG0', 'EEG0', 'EEG0', 'EEG0', 'EEG0', 'EEG0', 'MEG', 'MEG0']
#specific to subj 0004
#raw.info['bads'] = ['EEG074', 'EEG019', 'EEG027', 'EEG051', 'EEG037', 'EEG029', 'EEG004', 'MEG1541', 'MEG0141']
mne.set_config('MNE_STIM_CHANNEL', 'STI101')

reject = dict(eeg=2500e-6, # uV (EEG channels)
              eog=3000e-6) # uV (EOG channels)
              #grad=2500e-13, # T / m(gradiometers)
              #mag=4e-12, # T (magnetometers)

events = mne.find_events(raw, stim_channel='STI101', min_duration=0.002)
picks = mne.pick_types(raw.info, meg=False, eeg=True, eog=True, ecg=True, stim=False, exclude=[])
epochs = mne.Epochs(raw, events, event_id=event_id, tmin=-0.1, tmax=0.9,
                    picks=picks, baseline=(-0.086,0.014), preload=True,
                    reject=reject, proj=False)
                    # reject=reject, add_eeg_ref=False, proj=False)# add average reference when i plot evoked [DEPRECATED?]
epochs.shift_time(tshift) # it's to correct for the 14ms delay of the auditory stimulation

target_epochs = epochs[targets[block]]
idx = np.arange(0, int(len(target_epochs)), int(np.round(len(target_epochs)/11)))
end_idx = idx[1:]
start_idx = idx[0:-1]
print(start_idx)
print(end_idx)
evokeds = {}

norm = mpl.colors.Normalize(vmin=0, vmax=len(start_idx)-1)
cmap = mpl.cm.ScalarMappable(norm=norm, cmap=mpl.cm.Blues)
cmap.set_array([])
colors = {}

for intervals, starts in enumerate(start_idx):
    evoked = target_epochs[starts:end_idx[intervals]-1].average()
    out_folder = join(scratch_folder, 'MMN_paradigm', 'exposure_learning', 'evoked_' + targets[block], cur_sub)
    if not os.path.exists(out_folder):
       os.makedirs(out_folder)
    out_file = join(out_folder, targets[block] + '_' + str(intervals) + '-ave.fif') #average per trigger code per block
    evoked.save(out_file) #to save averaged data
    #print(evoked)
    #print(out_folder)
    #print(out_file)
    colors[str(intervals)] = cmap.to_rgba(intervals)
    evoked.pick_types(meg=False, eeg=True)
    #evokeds.append(evoked)
    evokeds[str(intervals)] = evoked

#picks = mne.pick_types(evokeds["1"].info, meg=False, eeg=False, eog=False, ecg=False, stim=False, include=['EEG014'])
picks = mne.pick_types(evokeds["0"].info, meg=False, eeg=True, eog=False, ecg=False, stim=False)
erp_plot = mne.viz.plot_compare_evokeds(evokeds, picks=picks, colors=colors, title='all 10%-percentiles', show=False)
out_plot_erp = join(out_folder, targets[block] + '_' + str(intervals) + '_erp.pdf')
erp_plot[0].savefig(out_plot_erp)

extr_evokeds=["0", "1", str(len(start_idx)-2), str(len(start_idx)-1)]
extr_colors=["3", "4", str(len(start_idx)-2), str(len(start_idx)-1)]
extr_plot = mne.viz.plot_compare_evokeds([evokeds[x] for x in extr_evokeds], picks=picks,
                                         colors=[colors[x] for x in extr_colors],
                                         title='extreme 10%-percentiles', show=False)
plt.legend(["~10%", "~20%", "~80%", "~90%"])
out_plot_extr = join(out_folder, targets[block] + '_' + str(intervals) + '_extr.pdf')
extr_plot[0].savefig(out_plot_extr)
