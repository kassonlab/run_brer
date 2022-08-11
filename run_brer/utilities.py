"""Utility functions to provide conformational ensemble bootstrapping before any ensemble estimate.
See Also https://github.com/kassonlab/run_brer/issues/54
"""
import os
import json
import run_data
from run_brer.directory_helper import DirectoryHelper
from run_brer.plugin_configs import PluginConfig

ensemble_dir = os.path.abspath()  #insert ensemble_dir
if not os.path.exists(ensemble_dir):
    raise RuntimeError(f'Ensemble directory {ensemble_dir} does not exist!')

def get_state_data(iteration: int, allow_incomplete=False):
    """Collect necessary data from previous iter state.json files.
    """
    iter_info = {}
    prev_state = '{}/mem_{}/{}_prev_state.json'.format(ensemble_dir, run_data.get('ensemble_num'), iteration) # is this the correct call for absolute paths?
    if os.path.exists(prev_state):
        self.run_data.from_dictionary(json.load(open(prev_state)))
        iter_info[self.run_data.get('ensemble_num')] = ['simulation_input']['tpr_file']  # not sure i'm calling the json info correctly here
    elif allow_incomplete:
        state = '{}/mem_{}/state.json'.format(ensemble_dir, run_data.get('ensemble_num'))
        self.run_data.from_dictionary(json.load())
        iter_info[self.run_data.get('ensemble_num')] = ['simulation_input']['tpr_file']
    return iter_info



def get_ensemble_estimate(iteration: int, ensemble_list):
    """Collect conformational ensemble estimates through iteration i.
    If iteration i is not provided, collects all conformational ensemble production phase results.
    """
    ensemble_estimate_paths = {}
    trajectory_output = '{}/mem_{}/{}/production/*.tpr'.format(ensemble_dir, run_data.get('ensemble_num'), iteration)
    if os.path.exists(trajectory_output):
        ensemble_estimate_paths['{}-{}'.format(run_data.get('ensemble_num'), iteration)] = trajectory_output
    return ensemble_estimate_paths

def ensemble_estimate_construction(ensemble_collection):
    """Identify specific results from conformational ensemble estimates for analysis.
    """
    for ensemble in ensemble_collection:
        # still piecing this together
