"""Class that handles the simulation data for BRER simulations.
"""
import json
import typing

from .metadata import MetaData
from .pair_data import PairData


class GeneralParams(MetaData):
    """Stores the parameters that are shared by all restraints in a single
    simulation.

    These include some of the "Voth" parameters: tau, A, tolerance

    .. versionadded:: 2.0
        The *end_time* parameter is only available with sufficiently recent versions of
        https://github.com/kassonlab/brer_plugin (late 2.0 beta). Otherwise,
        *end_time* will always be 0.0

    """

    def __init__(self):
        super().__init__('general')
        self.set_requirements([
            'A',
            'end_time',
            'ensemble_num',
            'iteration',
            'num_samples',
            'phase',
            'production_time',
            'sample_period',
            'start_time',
            'tau',
            'tolerance',
        ])

    def set_to_defaults(self):
        """Sets general parameters to their default values."""
        self.set_from_dictionary(self.get_defaults())

    @staticmethod
    def get_defaults():
        return {
            'A': 50,
            'end_time': 0.,
            'ensemble_num': 1,
            'iteration': 0,
            'num_samples': 50,
            'phase': 'training',
            'production_time': 10000,  # 10 ns
            'sample_period': 100,
            'start_time': 0.,
            'tau': 50,
            'tolerance': 0.25,
        }


class PairParams(MetaData):
    """Stores the parameters that are unique to a specific restraint."""

    def __init__(self, name):
        super().__init__(name)
        self.set_requirements(['sites', 'logging_filename', 'alpha', 'target'])

    def set_to_defaults(self):
        self.set(alpha=0., target=3.)

    def load_sites(self, sites: list):
        """Loads the atom ids for the restraint. This also sets the logging
        filename, which is named using the atom ids.

        Parameters
        ----------
        sites : list
            A list of the atom ids for a single restraint.

        Example
        -------
        >>> load_sites([3673, 5636])
        """
        self.set(sites=sites, logging_filename="{}.log".format(self.name))


class SimulationInput:
    """Stores the simulation input parameters for all restraints."""
    schema_version: typing.ClassVar[int] = 2
    tpr_file: str
    checkpoint: typing.Optional[str]

    def __init__(self,
                 tpr_file: str,
                 checkpoint: typing.Optional[str] = None,
                 schema_version: typing.Optional[int] = None):
        if schema_version is not None:
            if schema_version != self.schema_version:
                raise ValueError(f'Unsupported schema version: {schema_version}')
        self.tpr_file = tpr_file
        self.checkpoint = checkpoint

    def asdict(self):
        return {
            'schema_version': self.schema_version,
            'tpr_file': self.tpr_file,
            'checkpoint': self.checkpoint
        }

    @classmethod
    def decode(cls, *args, **kwargs):
        usage = 'Provide either a mapping object or appropriate key word arguments.'
        if len(kwargs) == 0:
            if len(args) > 1:
                raise TypeError('Unexpected positional argument(s). ' + usage)
            else:
                kwargs = args[0]
        else:
            if len(args) != 0:
                raise TypeError(
                    'Cannot accept both positional and key word arguments.' + usage)
        return cls(**kwargs)


class RunData:
    """Stores (and manipulates, to a lesser extent) all the metadata for a BRER
    run."""
    general_params: GeneralParams
    pair_params: typing.MutableMapping[str, PairParams]
    simulation_input: typing.Optional[SimulationInput] = None

    def __init__(self):
        """The full set of metadata for a single BRER run include both the
        general parameters and the pair-specific parameters."""
        self.general_params = GeneralParams()
        self.general_params.set_to_defaults()
        self.pair_params = {}
        self.__names = []

    def set(self, name=None, **kwargs):
        """method used to set either general or a pair-specific parameter.

        Parameters
        ----------
        name : str, optional
            restraint name.
            These are the same identifiers that are used in the RunConfig, by default None

        Raises
        ------
        ValueError
            if you provide a name and try to set a general parameter or
            don't provide a name and try to set a pair-specific parameter.
        """
        if len(kwargs) == 0:
            raise TypeError(
                f'Invalid signature: {self.__class__.__qualname__}.set() called without naming any '
                f'parameters.')

        for key, value in kwargs.items():
            # If a restraint name is not specified, it is assumed that the parameter is
            # a "general" parameter.
            if not name:
                if key in self.general_params.get_requirements():
                    self.general_params.set(key, value)
                else:
                    raise ValueError(
                        'You have not provided a name; this means you are probably trying '
                        'to set a '
                        'general parameter. {} is pair-specific'.format(key))
            else:
                if key in self.pair_params[name].get_requirements():
                    self.pair_params[name].set(key, value)
                else:
                    raise ValueError('{} is not a pair-specific parameter'.format(key)
                                     + ' but you have provided a name.')

    def get(self, key, *, name=None):
        """get either a general or a pair-specific parameter.

        Parameters
        ----------
        key : str
            the parameter to get.
        name : str
            if getting a pair-specific parameter, specify the restraint name. (Default
            value = None)

        Returns
        -------
            the parameter value.
        """
        if key in self.general_params.get_requirements():
            return self.general_params.get(key)
        elif name:
            return self.pair_params[name].get(key)
        else:
            raise ValueError(
                'You have not provided a name, but are trying to get a pair-specific '
                'parameter. '
                'Please provide a pair name')

    def as_dictionary(self):
        """Get the run metadata as a heirarchical dictionary:

        Returns
        -------
        type
            heirarchical dictionary of metadata
        
        Examples
        --------

        >>> ├── pair parameters
        >>> │   ├── name of pair 1
        >>> │   │   ├── alpha
        >>> │   │   ├── target
        >>> │   │   └── ...
        >>> │   ├── name of pair 2
        >>> |
        >>> ├── general parameters
        >>>     ├── A
        >>>     ├── tau
        >>>     ├── ...

        """
        pair_param_dict = {}
        for name in self.pair_params.keys():
            pair_param_dict[name] = self.pair_params[name].get_as_dictionary()

        return {
            'general parameters': self.general_params.get_as_dictionary(),
            'pair parameters': pair_param_dict,
            'simulation_input': self.simulation_input.asdict()
        }

    def from_dictionary(self, data: dict):
        """Loads metadata into the class from a dictionary.

        Parameters
        ----------
        data : dict
            RunData metadata as a dictionary.
        """
        self.general_params.set_from_dictionary(data['general parameters'])
        for name in data['pair parameters'].keys():
            self.pair_params[name] = PairParams(name)
            self.pair_params[name].set_from_dictionary(data['pair parameters'][name])
        simulation_input_dict = data.get('simulation_input', None)
        if simulation_input_dict is not None:
            self.simulation_input = SimulationInput.decode(**simulation_input_dict)

    def from_pair_data(self, pd: PairData):
        """Load some of the run metadata from a PairData object. Useful at the
        beginning of a run.

        Parameters
        ----------
        pd : PairData
            object from which metadata are loaded
        """
        name = pd.name
        self.pair_params[name] = PairParams(name)
        self.pair_params[name].load_sites(pd.get('sites'))
        self.pair_params[name].set_to_defaults()

    def clear_pair_data(self):
        """Removes all the pair parameters, replace with empty dict."""
        self.pair_params = {}

    def save_config(self, fnm='state.json'):
        """Saves the run parameters to a log file.

        Parameters
        ----------
        fnm : str, optional
            log file for state parameters, by default 'state.json'
        """
        with open(fnm, 'w') as fh:
            json.dump(self.as_dictionary(), fh, indent=4)

    def load_config(self, fnm='state.json'):
        """Load state parameters from file.

        Parameters
        ----------
        fnm : str, optional
            log file of state parameters, by default 'state.json'
        """
        with open(fnm, 'r') as fh:
            self.from_dictionary(json.load(fh))
