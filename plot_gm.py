# -*- coding: utf-8 -*-
"""
Script for analyzing early vs. late responses to words and pseudowords
@author: Andreas Højlund
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
out_folder = join(gm_folder, 'figures')
if not os.path.exists(out_folder):
   os.makedirs(out_folder)


kinds = ['pseudos', 'reals']
targets = {'pseudos': ['slukke', 'slitte', 'spykke', 'svaette']}
targets['reals'] = ['slutte', 'slikke', 'spytte', 'svaekke']

in_files = [f for f in os.listdir(gm_folder) if "{0:s}".format(group) in f]
print(in_files)

evokeds = {}

norm = mpl.colors.Normalize(vmin=0, vmax=len(in_files)-1)
cmap = mpl.cm.ScalarMappable(norm=norm, cmap=mpl.cm.Blues)
cmap.set_array([])
colors = {}

for fileno, fil in enumerate(in_files):
    evoked = mne.Evoked(join(gm_folder, fil))
    colors[str(fileno)] = cmap.to_rgba(fileno)
    evoked.pick_types(meg=True, eeg=False)
    #evokeds.append(evoked)
    evokeds[str(fileno)] = evoked

# GFP PLOTS
picks = mne.pick_types(evokeds["0"].info, meg=True, eeg=False, eog=False, ecg=False, stim=False)
gfp_plot = mne.viz.plot_compare_evokeds(evokeds, picks=picks, colors=colors, title=cond + ' | GFP all 10%-percentiles',
                                        show=False, ylim=dict(eeg=[0, 2.5]))
plt.legend(["0-10%", "10-20%", "20-30%", "30-40%", "40-50%", "50-60%", "60-70%", "70-80%", "80-90%", "90-100%"])
out_plot_gfp = join(out_folder, 'gfp_' + cond + '_' + group + '_' + str(len(in_files)) + '.pdf')
gfp_plot[0].savefig(out_plot_gfp)

# ONLY TWO MOST EXTREMES AT BOTH ENDS
extr_evokeds=["0", "1", str(len(in_files)-2), str(len(in_files)-1)]
extr_colors=["3", "4", str(len(in_files)-2), str(len(in_files)-1)]
extr_ev = [evokeds[x] for x in extr_evokeds]
#extr_ev = {(extr_evokeds[int(x)], evokeds[x]) for x in extr_evokeds}
extr_plot = mne.viz.plot_compare_evokeds(extr_ev, picks=picks,
                                         colors=[colors[x] for x in extr_colors],
                                         title=cond + ' | GFP: extreme 10%-percentiles', show=False, ci=True,
                                         ylim=dict(eeg=[0, 2.5]))
plt.legend(["0-10%", "10-20%", "80-90%", "90-100%"])
out_plot_extr = join(out_folder, 'gfp_extr_' + cond + '_' + group + '_' + str(len(in_files)) + '.pdf')
extr_plot[0].savefig(out_plot_extr)

# ERF PLOTS AT LEFT TEMP GRADS
left_picks = mne.pick_types(evokeds["0"].info, meg=False, eeg=False, eog=False, ecg=False, stim=False, include=['MEG0121', 'MEG0131', 'MEG0341', 'MEG0211'])
# erf_plot_img = mne.viz.plot_image(evokeds, picks=left_picks, title=cond + ' | Fz: all 10%-percentiles',
#                                         show=False, vmin=-2.5, vmax=2.5)
# out_plot_erf_img = join(out_folder, 'erp_img_' + cond + '_' + str(len(in_files)) + '.pdf')
# erp_plot_img[0].savefig(out_plot_erp)

left_plot = mne.viz.plot_compare_evokeds(evokeds, picks=left_picks, colors=colors, title=cond + ' | Left-temp: all 10%-percentiles',
                                       show=False, ylim=dict(eeg=[-2.5, 2.5]))
plt.legend(["0-10%", "10-20%", "20-30%", "30-40%", "40-50%", "50-60%", "60-70%", "70-80%", "80-90%", "90-100%"])
out_left_plot = join(out_folder, 'erp_' + cond + '_left_' + group + '_' + str(len(in_files)) + '.pdf')
left_plot[0].savefig(out_left_plot)

left_extr_plot = mne.viz.plot_compare_evokeds(extr_ev, picks=left_picks,
                                         colors=[colors[x] for x in extr_colors],
                                         title=cond + ' | Left-temp: extreme 10%-percentiles', show=False, ci=0.95,
                                         ylim=dict(eeg=[-2.5, 2.5]))
plt.legend(["0-10%", "10-20%", "80-90%", "90-100%"])
out_left_plot_extr = join(out_folder, 'erf_extr_' + cond + '_left_' + group + '_' + str(len(in_files)) + '.pdf')
left_extr_plot[0].savefig(out_left_plot_extr)


# ERF PLOTS AT RIGHT TEMP GRADS
right_picks = mne.pick_types(evokeds["0"].info, meg=False, eeg=False, eog=False, ecg=False, stim=False, include=['MEG1411', 'MEG1421', 'MEG1441', 'MEG1221'])
# erf_plot_img = mne.viz.plot_image(evokeds, picks=left_picks, title=cond + ' | Fz: all 10%-percentiles',
#                                         show=False, vmin=-2.5, vmax=2.5)
# out_plot_erf_img = join(out_folder, 'erp_img_' + cond + '_' + str(len(in_files)) + '.pdf')
# erp_plot_img[0].savefig(out_plot_erp)

right_plot = mne.viz.plot_compare_evokeds(evokeds, picks=right_picks, colors=colors, title=cond + ' | Right-temp: all 10%-percentiles',
                                       show=False, ylim=dict(eeg=[-2.5, 2.5]))
plt.legend(["0-10%", "10-20%", "20-30%", "30-40%", "40-50%", "50-60%", "60-70%", "70-80%", "80-90%", "90-100%"])
out_right_plot = join(out_folder, 'erf_' + cond + '_right_' + group + '_' + str(len(in_files)) + '.pdf')
right_plot[0].savefig(out_right_plot)

right_extr_plot = mne.viz.plot_compare_evokeds(extr_ev, picks=right_picks,
                                         colors=[colors[x] for x in extr_colors],
                                         title=cond + ' | Right-temp: extreme 10%-percentiles', show=False, ci=0.95,
                                         ylim=dict(eeg=[-2.5, 2.5]))
plt.legend(["0-10%", "10-20%", "80-90%", "90-100%"])
out_right_plot_extr = join(out_folder, 'erf_extr_' + cond + '_right_' + group + '_' + str(len(in_files)) + '.pdf')
right_extr_plot[0].savefig(out_right_plot_extr)
