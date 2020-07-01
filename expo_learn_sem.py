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

if __name__ == '__main__':  # only looks for command line inputs if script is called from command line
    group   = argv[1]
    sub     = argv[2]

proj_name = 'MINDLAB2018_MEG-Language-PD-DBS'
scratch_folder = join('/projects', proj_name, 'scratch')
misc_folder = join('/projects', proj_name, 'misc')
cur_sub = sub[:4]
# cur_sub = '0004'
in_file = join(scratch_folder, 'epoched_meg_' + group + '_100ms_bl', sub, cur_sub + '_sem-epo.fif')
print(in_file)

epochs = mne.read_epochs(in_file)

kinds = ['pseudos', 'reals']
targets = {'pseudos': ['slukke', 'slitte', 'spykke', 'svaette']}
targets['reals'] = ['slutte', 'slikke', 'spytte', 'svaekke']
ntrials = {}

for k, kind in enumerate(kinds):
    for t, target in enumerate(targets[kind]):
        # print(target)
        target_epochs = epochs[target]
        # print(target_epochs.get_data(picks=['mag', 'grad']))
        idx = np.arange(0, int(len(target_epochs)), int(np.round(len(target_epochs)/11)))
        if (len(target_epochs) % 10) > 4:
            idx = np.append(idx, len(target_epochs))
        elif (len(target_epochs) % 10) > 0:
            idx[-1] = len(target_epochs)
        end_idx = idx[1:]
        start_idx = idx[0:-1]
        print(start_idx)
        print(end_idx)
        evokeds = {}
        evoked = {}

        norm = mpl.colors.Normalize(vmin=0, vmax=len(start_idx)-1)
        cmap = mpl.cm.ScalarMappable(norm=norm, cmap=mpl.cm.Blues)
        cmap.set_array([])
        colors = {}

        evo_epo = np.empty([len(start_idx), target_epochs.get_data(picks=['mag', 'grad']).shape[1], len(target_epochs.times)])

        for intervals, starts in enumerate(start_idx):
            evoked[str(intervals)] = target_epochs[starts:end_idx[intervals]-1].average()
            evo_epo[intervals] = evoked[str(intervals)].data
            # list comprehension way of doing this from mne - requires conditions, tho
            #evokeds = [epochs[cond].average() for cond in ['Left', 'Right']]
            colors[str(intervals)] = cmap.to_rgba(intervals)
            evoked[str(intervals)].pick_types(meg=True, eeg=False, eog=False)

            out_folder = join(scratch_folder, 'intervals_meg_' + group + '_100ms_bl', sub)
            if not os.path.exists(out_folder):
               os.makedirs(out_folder)
            out_file = join(out_folder, cur_sub + '_' + target + '-' + str(intervals) + '_sem-ave.fif') #average per trigger code per block
            print(out_file)
            evoked[str(intervals)].save(out_file) #to save averaged data

        evokeds[target] = evoked

        ch_names = evoked[str(intervals)].info['ch_names']
        sfreq = evoked[str(intervals)].info['sfreq']
        ch_types = evoked[str(intervals)].get_channel_types()
        info = mne.create_info(ch_names=ch_names, sfreq=sfreq, ch_types=ch_types)
        evoked_epochs = mne.EpochsArray(evo_epo, info) #, events=range(len(start_idx)))
        print(evoked_epochs)
        out_file = join(out_folder, cur_sub + '_' + target + '_sem_evo-epo.fif')
        evoked_epochs.save(out_file)

        fig_folder = join(scratch_folder, 'intervals_meg_' + group + '_100ms_bl', sub, 'figures')
        if not os.path.exists(fig_folder):
           os.makedirs(fig_folder)

        picks = mne.pick_types(evokeds[target]["0"].info, meg=True, eeg=False, eog=False, ecg=False, stim=False)

        img_plot_gfp = target_epochs.plot_image(picks='meg', sigma=1.5, combine='gfp', evoked=True)
        fig_name = join(fig_folder, 'gfp_img_' + kind + '_' + target + '.png')
        img_plot_gfp[0].savefig(fig_name)

        left_picks = mne.pick_types(evokeds[target]["0"].info, meg=False, eeg=False, eog=False, ecg=False, stim=False, include=['MEG0121', 'MEG0131', 'MEG0341', 'MEG0211'])
        img_plot_med = target_epochs.plot_image(picks=left_picks, sigma=1.5, combine='median', evoked=True)
        fig_name = join(fig_folder, 'med_img_' + kind + '_' + target + '.png')
        img_plot_med[0].savefig(fig_name)

        # img_plot_right = target_epochs.plot_image(picks='meg', sigma=1.5, combine='median', evoked=True)
        # fig_name = join(fig_folder, 'right_img_' + kind + '_' + target + '.png')
        # img_plot_med[0].savefig(fig_name)
        #
        # img_plot_left = target_epochs.plot_image(picks='meg', sigma=1.5, combine='median', evoked=True)
        # fig_name = join(fig_folder, 'left_img_' + kind + '_' + target + '.png')
        # img_plot_med[0].savefig(fig_name)

        erp_plot = mne.viz.plot_compare_evokeds(evokeds[target], picks=left_picks, colors=colors, title='all 10%-percentiles', show=False)
        out_plot_erp = join(fig_folder, 'erp_' + kind + '_' + target + '_' + str(intervals) + '.png')
        erp_plot[0].savefig(out_plot_erp)

        extr_evokeds=["0", "1", str(len(start_idx)-2), str(len(start_idx)-1)]
        extr_colors=["3", "4", str(len(start_idx)-2), str(len(start_idx)-1)]
        extr_plot = mne.viz.plot_compare_evokeds([evokeds[target][x] for x in extr_evokeds], picks=picks,
                                                 colors=[colors[x] for x in extr_colors],
                                                 title='extreme 10%-percentiles', show=False)
        plt.legend(["~10%", "~20%", "~80%", "~90%"])
        out_plot_extr = join(fig_folder, 'extr_' + kind + '_' + target + '_' + str(intervals) + '.png')
        extr_plot[0].savefig(out_plot_extr)

        close('all')

print(evokeds)
