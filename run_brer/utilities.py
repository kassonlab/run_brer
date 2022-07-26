"""Utility functions to provide conformational ensemble bootstrapping before any ensemble estimate.
See Also https://github.com/kassonlab/run_brer/issues/54
"""
import os
import pathlib
from typing import Union
from run_brer.directory_helper import DirectoryHelper
from run_brer.plugin_configs import PluginConfig

#_Path = Union[str, pathlib.Path]
    directory = os.getcwd()  # under the assumption that the current directory is the main directory
    # what if it's not?
    if os.path.exists(os.path.join(directory, 'mem_1')):
        next()
    else:
       directory = os.chdir()

def get_state_data(iteration: int, allow_incomplete=False):
    """Collect necessary data from state.json files.
    """
    ensemble_list = os.listdir(os.path.join(directory, 'mem_'))  # create a list of all mem_* directories
    for i in range(len(ensemble_list)):
        with open(os.path.join(ensemble_list[i], 'state.json', 'r')):
          # pull necessary data
    return ensemble_list



def get_ensemble_estimate(iteration: int, ensemble_list):
    """Collect conformational ensemble estimates through iteration i.
    If iteration i is not provided, collects all conformational ensemble production phase results.
    """
    if iteration is not None:
        for i in range(len(ensemble_list)):
            os.chdir(os.path.join(ensemble_list[i], iteration, 'production'))
            # collect latest xtc file and place in another directory?
    else:
        for i in range(len(ensemble_list)):
            iterations = os.listdir(os.path.join(directory, 'mem_'))
            for j in len(iterations):
                os.chdir(os.path.join(ensemble_list[i], iterations[j], 'production'))
            # collect latest xtc file from all iterations and place in another directory?



def ensemble_estimate_analysis(iteration: int):
    """Identify specific results from conformational ensemble estimates for analysis.
    """