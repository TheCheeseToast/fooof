"""File I/O for FOOOF."""

import io
import os
import json
from json import JSONDecodeError

from fooof.utils import get_attribute_names
from fooof.utils import dict_array_to_lst, dict_select_keys, dict_lst_to_array

###################################################################################################
###################################################################################################

def save_fm(fm, save_file, save_path, save_results, save_settings, save_data, append):
    """Save a FOOOF object to a json file.

    Parameters
    ----------
    save_file : str or FileObject, optional
        File to which to save data.
    save_path : str, optional
        Path to directory to which the save. If not provided, saves to current directory.
    save_results : bool, optional
        Whether to save out FOOOF model fit results.
    save_settings : bool, optional
        Whether to save out FOOOF settings.
    save_data : bool, optional
        Whether to save out input data.
    append : bool, optional
        Whether to append to an existing file, if available. default: False
            This option is only valid (and only used) if save_file is a str.
    """

    # Convert object to dictionary & convert all arrays to lists - for JSON serializing
    obj_dict = dict_array_to_lst(fm.__dict__)

    # Set and select which variables to keep. Use a set to drop any potential overlap
    attributes = get_attribute_names()
    keep = set((attributes['results'] if save_results else []) + \
               (attributes['settings'] if save_settings else []) + \
               (attributes['dat'] if save_data else []))
    obj_dict = dict_select_keys(obj_dict, keep)

    # Save out - create new file, (creates a JSON file)
    if isinstance(save_file, str) and not append:
        with open(os.path.join(save_path, save_file + '.json'), 'w') as outfile:
            json.dump(obj_dict, outfile)

    # # Save out - append to file_name (appends to a JSONlines file)
    # elif isinstance(save_file, str) and append:
    #     with open(os.path.join(save_path, save_file + '.json'), 'a') as outfile:
    #         json.dump(obj_dict, outfile)
    #         outfile.write('\n')

    # Save out - append to given file object (appends to a JSONlines file)
    elif isinstance(save_file, io.IOBase):
        json.dump(obj_dict, save_file)
        save_file.write('\n')

    else:
        raise ValueError('Save file not understood.')


def save_fg(fg, save_file, save_path, save_results, save_settings, save_data):
    """Save a FOOOFGroup object to jsonlines file.

    Parameters
    ----------
    save_file : str or FileObject, optional
        File to which to save data.
    save_path : str, optional
        Path to directory to which the save. If not provided, saves to current directory.
    save_results : bool, optional
        Whether to save out FOOOF model fit results.
    save_settings : bool, optional
        Whether to save out FOOOF settings.
    save_data : bool, optional
        Whether to save out PSD data.
    """

    # Loops through group object, creating a FOOOF object per PSD, and saves from there
    with open(os.path.join(save_path, save_file + '.json'), 'w') as f_obj:
        for ind in range(len(fg.group_results)):
            fm = fg.get_fooof(ind, regenerate=False)
            save_fm(fm, save_file=f_obj, save_path='', save_results=save_results,
                    save_settings=save_settings, save_data=save_data, append=False)


def load_json(file_name, file_path):
    """Load json file.

    Parameters
    ----------
    load_file : str or FileObject, optional
            File from which to load data.
    file_path : str
        Path to directory from which to load. If not provided, loads from current directory.

    Returns
    -------
    dat : dict
        Dictionary of data loaded from file.
    """

    # Load data from file
    if isinstance(file_name, str):
        with open(os.path.join(file_path, file_name + '.json'), 'r') as infile:
            dat = json.load(infile)
    elif isinstance(file_name, io.IOBase):
        dat = json.loads(file_name.readline())

    # Get dictionary of available attributes, and convert specified lists back into arrays
    dat = dict_lst_to_array(dat, get_attribute_names()['arrays'])

    return dat


def load_jsonlines(file_name, file_path):
    """Load a jsonlines file, yielding data line by line.

    Parameters
    ----------
    load_file : str or FileObject, optional
            File from which to load data.
    file_path : str
        Path to directory from which to load. If not provided, loads from current directory.

    Yields
    ------
    dict
        Dictionary of data loaded from file.
    """

    with open(os.path.join(file_path, file_name + '.json'), 'r') as f_obj:

        while True:

            # Load each line, as JSON file
            try:
                yield load_json(f_obj, '')

            # Break off when get a JSON error - end of the file
            except JSONDecodeError:
                break
