# -*- coding: utf-8 -*-
"""
Script for analyzing early vs. late responses to words and pseudowords
@author: Andreas Højlund (& Christelle Gansonre)
@email:  hojlund@cfin.au.dk
@github: https://github.com/ahoejlund/...
"""

#==============================================================================
# IMPORTS
#%%============================================================================

from os.path import join
import mne
from mne import io
import warnings
import os
import numpy as np
from matplotlib import pyplot as plt
import matplotlib as mpl
from pylab import*

%matplotlib wx

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

sub     = argv[1]
block   = argv[2]

proj_name = 'MINDLAB2015_MEG-Sememene'
scratch_folder = join('/projects', proj_name, 'scratch')
blockno = '_block' + str(block)#block number going from 1 to 7
# blockno = '_block' + str(1)#block number going from 1 to 7
filter_values = 'None-40.0Hz'
# cur_sub = '0004'
cur_sub = sub
blocktype = 'MMN'
filename = blocktype + blockno + '_raw_tsss.fif'
in_folder = join(scratch_folder, 'MMN_paradigm', 'filtered', 'tsss_st10_corr98', filter_values, cur_sub)
in_file = join(in_folder, filename)
raw = mne.io.Raw(in_file, preload = True)
print in_file
#raw.plot()

epoch_values = 'm-100-900ms'
event_ids = [dict(bide=10,
                bidet=15,
                biden=16,
                bidt=17,
                bondt=18,
                MRbide=19),

                dict(mide=20,
                midet=25,
                miden=26,
                midt=27,
                mondt=28,
                MRmide=29),

                dict(gide=30,
                gidet=35,
                giden=36,
                gidt=37,
                gondt=38,
                MRgide=39),

                dict(nide=40,
                nidet=45,
                niden=46,
                nidt=47,
                nondt=48,
                MRnide=49)]
event_id = event_ids[block]

# raw.info['bads'] = ['EEG0', 'EEG0', 'EEG0', 'EEG0', 'EEG0', 'EEG0', 'EEG0', 'MEG', 'MEG0']
#raw.info['bads'] = ['EEG074', 'EEG019', 'EEG027', 'EEG051', 'EEG037', 'EEG029', 'EEG004', 'MEG1541', 'MEG0141']
mne.set_config('MNE_STIM_CHANNEL', 'STI101')

reject = dict(grad=2500e-13, # T / m(gradiometers)
              mag=4e-12, # T (magnetometers)
              eeg=150e-6, # uV (EEG channels)
              eog=150e-6) # uV (EOG channels)

events = mne.find_events(raw, stim_channel='STI101', min_duration=0.002)
picks = mne.pick_types(raw.info, meg=True, eeg=True, eog=True, ecg=True, stim=False, exclude=[])
epochs = mne.Epochs(raw, events, event_id=event_id, tmin=-0.1, tmax=0.9,
                    picks=picks, baseline=(-0.086,0.014), preload=True,
                    reject=reject, proj=False)
                    # reject=reject, add_eeg_ref=False, proj=False)# add average reference when i plot evoked [DEPRECATED?]
epochs.times -= 0.014 # it's to correct for the 14ms delay

# epochs_data = epochs.get_data()
#epochs.plot_drop_log()
# for key in event_id:
#     evoked = epochs[key].average()
#     out_folder = join(scratch_folder, 'MMN_paradigm', 'evoked_bide', epoch_values, cur_sub)
#    if not os.path.exists(out_folder):
#        os.makedirs(out_folder)
#    out_file = join(out_folder, key + '-ave.fif') #average per trigger code per block
#    evoked.save(out_file) #to save averaged data
#    print(evoked)
#    print(out_folder)
#    print(out_file)

#for key in event_id:
#    print(key)
#    print(len(epochs[key]))

bide_epochs = epochs['bide']
idx = np.arange(0, len(bide_epochs), np.round(len(bide_epochs)/10))
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
    evoked = bide_epochs[starts:end_idx[intervals]-1].average()
    out_folder = join(scratch_folder, 'MMN_paradigm', 'evoked_bide', cur_sub)
    if not os.path.exists(out_folder):
       os.makedirs(out_folder)
    out_file = join(out_folder, 'bide_' + str(intervals) + '-ave.fif') #average per trigger code per block
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
erp_plot = mne.viz.plot_compare_evokeds(evokeds, picks=picks, colors=colors, title='all 10%-percentiles')

extr_evokeds=["0", "1", "8", "9"]
extr_colors=["3", "4", "8", "9"]
extr_plot = mne.viz.plot_compare_evokeds([evokeds[x] for x in extr_evokeds], picks=picks,
                                         colors=[colors[x] for x in extr_colors],
                                         title='extreme 10%-percentiles')
#picks_test = evokeds["1"].pick_channels(['EEG015'])
#?mne.viz.plot_compare_evokeds

#picks_test
#evokeds["1"]


#picks = mne.pick_types(evokeds[0].info, meg=False, eeg=False, eog=False, ecg=False, stim=False, include=['EEG013'])
#picks = mne.pick_types(evokeds[0].info, meg=False, eeg=True, eog=False, ecg=False, stim=False)

#picks = mne.pick_types(evokeds[0].info, meg=False, eeg=True, eog=False, ecg=False, stim=False)
#erp_plot = mne.viz.plot_compare_evokeds(evokeds, picks=picks, colors=colors, title='all EEG channels')

#erp_plot.legend(range(10), arange(1,10))
#?erp_plot.legend
#?mne.viz.plot_compare_evokeds

extr_evokeds=["0", "1", "8", "9"]
extr_colors=["3", "4", "8", "9"]
extr_plot = mne.viz.plot_compare_evokeds([evokeds[x] for x in extr_evokeds], picks=picks,
                                         colors=[colors[x] for x in extr_colors],
                                         title='extreme 10%-percentiles')
plt.legend(["10%", "20%", "80%", "90%"])


#print(in_file)
#raw.info

##### BLOCK 2
#%reset
proj_name = 'MINDLAB2015_MEG-Sememene'
scratch_folder = join('/projects', proj_name, 'scratch')
blockno = '_block' + str(2)#block number going from 1 to 7
filter_values = 'None-40.0Hz'
cur_sub = '0004'
blocktype = 'MMN'
filename = blocktype + blockno + '_raw_tsss.fif'
in_folder = join(scratch_folder, 'MMN_paradigm', 'filtered', 'tsss_st10_corr98', filter_values, cur_sub)
in_file = join(in_folder, filename)
raw = mne.io.Raw(in_file, preload = True)
#raw.plot()

epoch_values = 'm-100-900ms'
proj_name = 'MINDLAB2015_MEG-Sememene'
scratch_folder = join('/projects', proj_name, 'scratch')
blockno = '_block' + str(2)#block number going from 1 to 7
filter_values = 'None-40.0Hz'
cur_sub = '0004'
blocktype = 'MMN'
filename = blocktype + blockno + '_raw_tsss.fif'
in_folder = join(scratch_folder, 'MMN_paradigm', 'filtered', 'tsss_st10_corr98', filter_values, cur_sub)
in_file = join(in_folder, filename)
#raw = mne.io.Raw(in_file, preload = True) #raw should already be loaded

event_id = dict(mide=20,
                midet=25,
                miden=26,
                midt=27,
                mondt=28,
                MRmide=29)
#raw.info['bads'] = ['EEG0', 'EEG0', 'EEG0', 'EEG0', 'EEG0', 'EEG0', 'EEG0', 'MEG', 'MEG0']
mne.set_config('MNE_STIM_CHANNEL', 'STI101')

reject = dict(grad=2500e-13, # T / m(gradiometers)
              mag=4e-12, # T (magnetometers)
              eeg=150e-6, # uV (EEG channels)
              eog=150e-6) # uV (EOG channels)


events = mne.find_events(raw, stim_channel='STI101', min_duration=0.002)
picks = mne.pick_types(raw.info, meg=True, eeg=True, eog=True, ecg=True, stim=False, exclude=[])
epochs = mne.Epochs(raw, events, event_id=event_id, tmin=-0.1, tmax=0.9,
                    picks=picks, baseline=(-0.086,0.014), preload=True,
                    reject=reject, proj=False)
#                    reject=reject, add_eeg_ref=False, proj=False)# add average reference when i plot evoked [DEPRECATED]

epochs.times -= 0.014 # it's to correct for the 14ms delay


event_id = dict(gide=30,
                gidet=35,
                giden=36,
                gidt=37,
                gondt=38,
                MRgide=39)

event_id = dict(nide=40,
                nidet=45,
                niden=46,
                nidt=47,
                nondt=48,
                MRnide=49)
