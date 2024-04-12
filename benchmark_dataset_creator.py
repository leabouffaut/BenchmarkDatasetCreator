# Benchmark Dataset Creator functions
#
# Léa Bouffaut, Ph.D. -- K. Lisa Yang Center for Conservation Bioacoustics, Cornell University
# lea.bouffaut@cornell.edu

import os
import sys
import shutil

import numpy as np
# from scipy import signal
import pandas as pd
import librosa
import soundfile as sf
#from tqdm.notebook import tqdm
from tqdm import tqdm


# ---------------------------
#  User interaction functions
def query_yes_no(question, default="yes"): # TODO moved to create_folders_functions -- delete
    """
    Ask a yes/no question via raw_input() and return their answer.

    Inputs:
        - question: A string that is presented to the user.
        - default: The presumed answer if the user just hits <Enter>. It must be "yes" (the default), 
        "no", or None (meaning an answer is required from the user).

    Return value:
        - True for "yes" or False for "no".
    """
    # Dictionary mapping valid yes/no responses to boolean values
    valid = {"yes": True, "y": True, "ye": True, "no": False, "n": False}

    # Set the prompt based on the default answer
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        # Raise a ValueError for an invalid default answer
        raise ValueError("invalid default answer: '%s'" % default)

    # Loop until a valid response is provided
    while True:
        # Display the question and prompt the user for a response
        sys.stdout.write(question + prompt)
        choice = input().lower()
        # If the default answer is provided and not empty, return the corresponding boolean value
        if default is not None and choice == "":
            return valid[default]
        # If the user's choice is in the valid responses, return the corresponding boolean value
        elif choice in valid:
            return valid[choice]
        else:
            # If the response is invalid, prompt the user to respond with 'yes' or 'no'
            sys.stdout.write("Please respond with 'yes' or 'no' (or 'y' or 'n').\n")


def path_print(start_path): # TODO moved to create_folders_functions -- delete
    """
    Prints the content of the folder designated by startpath
    """
    # Iterate through the directory tree starting from 'startpath'
    for root, dirs, files in os.walk(start_path):

        # Determine the depth of the current directory relative to 'startpath'
        level = root.replace(start_path, '').count(os.sep)

        # Calculate the indentation for displaying directory structure
        indent = ' ' * 4 * (level)

        # Print the name of the current directory
        print('{}{}/'.format(indent, os.path.basename(root)))

        # Calculate the indentation for displaying files within the directory
        sub_indent = ' ' * 4 * (level + 1)

        # Iterate through the files in the current directory
        for f in files:
            # Print the name of each file within the directory
            print('{}{}'.format(sub_indent, f))


def create_path(export_settings): # TODO moved to create_folders_functions -- delete
    """
    Function to create export folders following this architecture:
    Export folder/
    |... Original project name/
    |... |... audio/
    |... |... annotations/

    Displays a warning if the folders already exist, which can be overwritten based on user input.
    """
    # Construct paths for audio and annotations folders based on export settings
    audio_path = os.path.join(export_settings['Export folder'], export_settings['Original project name'], 'audio')
    annot_path = os.path.join(export_settings['Export folder'], export_settings['Original project name'], 'annotations')

    # If the audio folder does not exist in path
    if not os.path.exists(audio_path):
        # Create the audio and annotations folders
        os.makedirs(audio_path)
        os.makedirs(annot_path)
        # Update export settings with the paths
        export_settings['Audio export folder'] = audio_path
        export_settings['Annotation export folder'] = annot_path

    # If the audio folder already exists
    else:
        # Display a warning message
        print(f'Warning: This folder already exists, data may be deleted: \n')
        print(path_print(os.path.join(export_settings['Export folder'], export_settings['Original project name'])))

        # Ask the user whether to delete existing data
        if query_yes_no(f'Delete data?', default="yes") == True:

            # Delete existing audio and annotations folders
            shutil.rmtree(audio_path)
            shutil.rmtree(annot_path)

            # Recreate audio and annotations folders
            os.makedirs(audio_path)
            os.makedirs(annot_path)

            # Update export settings with the new paths
            export_settings['Audio export folder'] = audio_path
            export_settings['Annotation export folder'] = annot_path
        else:
            # Prompt the user to change the export folder path
            print(f"Please change the export folder path")


def check_export_settings(export_settings):
    """
    Checks the completeness of export settings provided by the user.

    Inputs:
        - export_settings: A dictionary that should contain the audio export settings:
        'Original project name', 'Audio duration (s)', 'fs (Hz)', 'Bit depth', 'Export label', 
        'Split export selections', and 'Export folder'.

    Raises:
        - ValueError: If any required field in the wanted_fields_list is missing in the export_settings 
        dictionary.
    """
    wanted_fields_list = ['Original project name', 'Audio duration (s)', 'fs (Hz)', 'Bit depth', 'Export label',
                          'Split export selections', 'Export folder']
    missing = []

    # Go through the wanted fields
    for wf in wanted_fields_list:

        # Test if the wanted field is not in the export_settings dictionary, if true add it to the 'missing' list
        if wf not in export_settings:
            missing.append(wf)

    if missing:
        raise ValueError(f"Error: Missing field in export_settings: {missing}")
    else:
        print(f"All required fields are filled")


def check_selection_tab(selection_table_path):
    """
    Checks the validity of a selection table path.

    Inputs:
        - selection_table_path: A string representing the path to a selection table file or folder.

    Raises:
        - ValueError: If the selection_table_path is not a valid path to an existing folder or file.
    """
    # Test if selection_table_path is a file
    if os.path.isfile(selection_table_path):
        print(f"selection_table_path is a File")

    # Test if selection_table_path is a Folder and count number of txt files in that folder
    elif os.path.isdir(selection_table_path):
        filelist = [file for file in os.listdir(selection_table_path) if file.endswith(".txt")]

        print(f"selection_table_path is a Folder with {len(filelist)} .txt Files")

    # Otherwise, raise an error for invalid selection_table_path
    else:
        raise ValueError("Please provide a valid path to an existing folder or file.")


def get_bitdepth(export_settings):
    """
    Get the bit depth based on user-input export settings. Only FLAC files are supported.

    Inputs:
        - export_settings: Dictionary containing export settings, including parameters such as 'Bit depth'.

    Outputs:
        - bit_depth: The corresponding bit depth for the export settings.
    """
    authorized_user_bit_depth = [8, 16, 24]
    sf_flac_bit_depth = ['PCM_S8', 'PCM_16', 'PCM_24']  # This is only valid for flac files. 
    # write sf.available_subtypes('WAV') to get the bit depth 
    # format supported for wav files

    bit_depth = sf_flac_bit_depth[authorized_user_bit_depth.index(export_settings['Bit depth'])]
    return bit_depth


def get_print_fs(fs_original):
    """
    Take note of the sampling frequency for the file naming system.
    Input:
        - fs_original: Original sampling frequency.
        
    Output:
        - fs_original_print: fs to print
    """
    if fs_original >= 1000:
        fs_original_print = str(int(np.floor(fs_original / 1000))) + 'kHz'
    else:
        fs_original_print = str(int(fs_original)) + 'Hz'

    return fs_original_print


# ------------------------
#  Data checking functions
def check_bitdepth(export_settings):
    """
    Checks if the user-input bit depth is a possible value, based on formats supported by soundfile.write for FLAC files.

    Displays an error message if the value is not supported.
    
    Inputs:
        - export_settings: Dictionary containing export settings.
    Output:
        - Printed text indicating if the bit depth is not supported
    """

    # List of authorized bit depths user inputs and corresponding soundfile FLAC bit depths
    authorized_user_bit_depth = [8, 16, 24]
    sf_flac_bit_depth = ['PCM_S8', 'PCM_16', 'PCM_24']

    # Test if the specified bit depth is supported
    if export_settings['Bit depth'] not in authorized_user_bit_depth:
        # Raise error message if the specified bit depth is not supported
        raise ValueError(
            f"Error: Non-supported Bit depth, please select on of the following values:\n ...{authorized_user_bit_depth}")


def check_selection_table(df):
    """
    This function checks whether all of the required fields are present in the selection table.

    Inputs:
        - df: The dataframe of the selection table.
        - label_key: The name of the field for the label column.

    Output:
        - Printed text indicating whether the required fields are present.
    """

    # List of all desired fields in the selection table
    wanted_fields = ['Begin Time (s)', 'End Time (s)', 'Low Freq (Hz)', 'High Freq (Hz)', 'File Offset (s)',
                     'Begin Path']

    # Check if each desired field is present in the selection table, and if not, add it to the 'missing' list
    missing = []
    for item in wanted_fields:
        if item not in df.columns:
            missing.append(item)

    # Raise an error if any required fields are missing
    if missing:
        raise ValueError(f'Error: The following field(s) is missing from the selection table: {", ".join(missing)}')
    else:
        print('All required fields are in the selection table')


def check_selection_table_folder(df):
    """
    This function checks whether all of the required fields are present in a selection table without specifying the annotation column.

    Inputs:
        - df: The dataframe of the selection table.
        - label_key: The name of the field for the label column.

    Output:
        - Printed text indicating whether the required fields are present.
    """

    # List of all desired fields in the selection table
    wanted_fields = ['Begin Time (s)', 'End Time (s)', 'Low Freq (Hz)', 'High Freq (Hz)', 'File Offset (s)',
                     'Begin Path']

    # Check if each desired field is present in the selection table, and if not, add it to the 'missing' list
    missing = []
    for item in wanted_fields:
        if item not in df.columns:
            missing.append(item)

    return missing


# ----------------------------------------------
# Manipulate existing selection tables functions


def load_selection_table(selection_table_path):
    """
    Load one or multiple selection table(s) from a file or folder. It takes tab-separated Raven Pro 1.6 
    selection tables (.txt).

    Inputs:
        - selection_table_path: A string representing the path to a selection table file or folder.

    Returns:
        - selection_table_df: A Panda DataFrame containing the loaded selection table.

    This function loads the selection table from the provided selection_table_path, which can be either a 
    file or a folder containing multiple selection table files. If selection_table_path points to a file, 
    the function reads the file using pandas.read_csv(). If selection_table_path points to a folder, the 
    function iterates through all '.csv' files in the folder, reads each file, and concatenates the data 
    into a single DataFrame.

    The function also checks if all necessary fields are present in the selection table(s) and raises a 
    ValueError if any field is missing. If all required fields are present, it prints a message confirming 
    their presence.

    """

    # If selection_table_path is a file
    if os.path.isfile(selection_table_path):
        selection_table_df = pd.read_csv(selection_table_path, sep='\t')

        # Check if all necessary fields are present
        check_selection_table(selection_table_df)

    # If selection_table_path is a folder
    elif os.path.isdir(selection_table_path):
        # Get the list of files
        seltab_list = os.listdir(selection_table_path)

        # Create empty list for missing fields
        missing = {}
        for ff in seltab_list:
            # Open selection table
            selection_table_df_temp = pd.read_csv(os.path.join(selection_table_path, ff), sep='\t')

            # Check that all the files have the same fields
            missing_file = check_selection_table_folder(selection_table_df_temp)

            # Add the file and missing field to the dictionary if missing_file not empty
            if missing_file:
                missing[ff] = missing_file

            # If no entries are missing and this is the first selection table, create the output big selection table
            elif (not missing_file) & ('selection_table_df' not in locals()):
                selection_table_df = selection_table_df_temp

            # If no entries are missing and selection_table_df exists   
            elif (not missing_file) & ('selection_table_df' in locals()):
                #selection_table_df = selection_table_df.append(selection_table_df_temp)
                selection_table_df = pd.concat([selection_table_df, selection_table_df_temp], ignore_index=True)

        # If all required fields are in 
        if not missing:
            print('All required fields are in the selection tables')

        else:

            # Raise an error indicating missing fields in the selection tables
            error_msg = 'Error: The following field(s) is missing from the selection table:\n'
            for keys, value in missing.items():
                error_msg += f'--> in {keys}, the field(s) {value} are missing\n'
            raise ValueError(error_msg)

            # Empty the dataframe
            selection_table_df = pd.DataFrame({'A': []})

    else:
        # Raise an error for invalid selection_table_path
        raise ValueError("Please provide a valid path to an existing folder or file.")

    return selection_table_df


def get_number_clips(list_audio_files, clip_duration):
    """
    This function reads the durations of all audio files in the given list and compares them to the desired clip duration.

    Inputs:
        - list_audio_files: A list of audio files with their full paths.
        - clip_duration: The chosen export clip duration.

    Outputs:
        - number_clip: The number of export clips per audio file.
    """

    # Get the duration of each file and calculate the associated number of non-overlapping clips
    file_duration = []
    number_clip = []
    for file in list_audio_files:
        fdur = librosa.get_duration(path=file)
        number_clip.append(int(np.floor(fdur / clip_duration)))
        file_duration.append(fdur)

    # Check if all files have the same number of clips
    unique_number_clip = list(set(number_clip))

    if len(unique_number_clip) == 1:  # If all files have the same number of clips
        # Print the information about the number of non-overlapping clips
        print(f'All files can be divided into {unique_number_clip[0]} x {clip_duration}-s clips')
    else:  # If there are different numbers of clips for different files
        # Print the mismatched number of clips
        print(f'Mismatched number of clips: {unique_number_clip} s')

    # Return the list containing the number of clips for each file
    return number_clip


def update_labels(selection_table_df, labels_dict, label_key):
    """
    Updates labels in the selection table based on the provided labels dictionary.

    Inputs:
        - selection_table_df: DataFrame containing the selection table.
        - labels_dict: Dictionary containing label updates.
        - label_key: Name of the field for the label column.

    Outputs:
        - Updated selection table with labels.
    """

    # Swap the labels in the selection table
    for old_label in labels_dict.keys():
        # Test if the original label is present in the selection table
        if old_label in selection_table_df[label_key].unique():
            # Replace the original label with the new label
            selection_table_df[label_key].replace(old_label, labels_dict[old_label], inplace=True)
        else:
            # Print a message if the original label is not found in the selection table
            print(f'Skipping: Original label {old_label} not found in the selection table')

    # Check the uniqueness of labels after swapping
    unique_labels = selection_table_df[label_key].unique()
    print('New unique label list:')
    for lab in unique_labels:
        print(lab)

    # Return the modified selection table
    return selection_table_df


# -----------------------
# Write outputs functions

def save_audioclip(audiofile, export_settings, export_filename, start_clip, bit_depth, channel):
    # Test if the export audio file already exists otherwise, create it
    if not os.path.exists(os.path.join(export_settings['Audio export folder'], export_filename + '.flac')):

        # Load and resample the the audio
        x_clip, fs = librosa.load(audiofile, offset=start_clip,
                                  duration=export_settings['Audio duration (s)'],
                                  sr=export_settings['fs (Hz)'], mono=False, res_type='soxr_vhq')
        # Test if x is multi-channel
        nb_ch = x_clip.ndim
        # Keep the wanted channel
        if nb_ch > 1:
            x_clip = x_clip[channel, :]

        # Save clip
        sf.write(os.path.join(export_settings['Audio export folder'], export_filename + '.flac'),
                 x_clip, fs, bit_depth)


def write_selection_table(filename, entry, export_label='Tag'):
    """
    This function creates a selection table, appends entries, and saves it.

    Inputs:
        - filename: Selected file name with full path and an extension.
        - entry: Line to write in the selection table.
        - export_label: Name of the label column in the selection table (str). Default is 'Tag'.

    Outputs:
        - Saved selection table.
    """

    header = ['Selection', 'View', 'Channel', 'Begin Time (s)', 'End Time (s)', 'Low Freq (Hz)', 'High Freq (Hz)',
              'Begin File', 'Original Begin Time (s)', export_label]

    # If the filename doesn't exist yet, add the Header
    if not os.path.exists(filename):
        with open(filename, 'w') as f:
            f.write('\t'.join(header) + '\n')
            f.close()

    # Get the number of entries in the selection table
    # If no entries yet, count = 0
    with open(filename, 'r') as f:
        for count, line in enumerate(f):
            pass
    entry[0] = count + 1

    # If some of the entries are not strings
    for ind in range(len(entry)):
        if not isinstance(entry[ind], str):
            entry[ind] = str(entry[ind])

    # Append the variables to the table
    with open(filename, 'a') as f:
        f.write('\t'.join(entry) + '\n')
        f.close()


def write_annotation_csv(filename, entry, export_label='Tag'):
    """
    This function creates a recap annotation CSV, appends entries, and saves it in the format of https://doi.org/10.5281/zenodo.7079380.

    Inputs:
        - filename: Selected file name with full path and an extension.
        - entry: Line to write in the selection table.
        - export_label: Name of the label column in the selection table (str). Default is 'Tag'.

    Outputs:
        - One annotation table for the entire project.
    """

    header = ['Filename', 'Start Time (s)', 'End Time (s)', 'Low Freq (Hz)', 'High Freq (Hz)', export_label]

    # If the filename doesn't exist yet, add the Header
    if not os.path.exists(filename):
        with open(filename, 'w') as f:
            f.write('\t'.join(header) + '\n')
            f.close()

    # Entry need to remove some of the entries to fit our header
    # [0 = 'Selection', 1= 'View', 2= 'Channel', 3= 'Begin Time (s)', 4= 'End Time (s)', 
    # 5= 'Low Freq (Hz)', 6= 'High Freq (Hz)', 7= 'Begin File', 8= 'Original Begin Time (s)', 9= 'Tag']
    entry = [entry[7], "{:.2f}".format(float(entry[3])), "{:.2f}".format(float(entry[4])),
             entry[5], entry[6], entry[9]]

    # Append the variables to the table
    with open(filename, 'a') as f:
        f.write('\t'.join(entry) + '\n')
        f.close()


def map_audio_selection(filename, audio_filename, selection_filename):
    """
    This function creates a recap CSV matching audio file names and selection table names, appends entries, and saves it.

    Inputs:
        - filename: Selected file name with full path and an extension.
        - audio_filename: Selected audio file name with full path and an extension.
        - selection_filename: Corresponding annotation file name with full path and an extension.

    Outputs:
        - One mapping CSV table for the entire project.
    """

    # If the filename doesn't exist yet, add the Header
    if not os.path.exists(filename):
        with open(filename, 'w') as f:
            f.close()

    # Append the association to the table
    with open(filename, 'a') as f:
        f.write('\t'.join([audio_filename, selection_filename]) + '\n')
        f.close()


def exports(export_settings, selection_table_af_df, save_sel_dict):
    """
    Create all exports based on provided export settings, selection table DataFrame, and save selection dictionary.

    Inputs:
        - export_settings: Dictionary containing export settings.
        - selection_table_af_df: Selection table imported as a Panda DataFrame.
        - save_sel_dict: Dictionary containing information about the clip to be saved with the following keys:
         'Selection #', 'fs_original_print', 'Channel', 'Start export clip', 'Bit depth', 'Label key', 'Begin Time (s)', 
         'End Time (s)'
          This variable is created in benchmark_creator

    This function creates all exports based on the provided export settings, selection table DataFrame, and save selection 
    dictionary. It generates filenames for exported audio files, exports audio clips, writes entries in the selection table 
    file, writes annotations in a global CSV file, and creates a file association CSV.

    Note: This function assumes the presence of several helper functions such as 'save_audioclip', 'write_selection_table',
    'write_annotation_csv', and 'map_audio_selection'.
    """
    # Get the export audio file name in the format
    # <Project>_<OriginalFileName>_<OriginalSamplingFrequency>_<OriginalChannel>.flac
    export_filename = (export_settings['Original project name'] + '_' +
                       os.path.splitext(
                           os.path.basename(selection_table_af_df['Begin Path'].iloc[save_sel_dict['Selection #']]))[
                           0] + '_' +
                       str(save_sel_dict['fs_original_print']) + '_' + 'ch' + "{:02d}".format(
                save_sel_dict['Channel'] + 1) + '_' +
                       "{:04d}".format(int(np.floor(save_sel_dict['Start export clip']))) + 's')

    # Export audio
    audiofile = selection_table_af_df['Begin Path'].iloc[save_sel_dict['Selection #']]
    save_audioclip(audiofile, export_settings, export_filename, save_sel_dict['Start export clip'],
                   save_sel_dict['Bit depth'], save_sel_dict['Channel'])

    # Create/fill the selection table for this clip with the format 
    # ['Selection', 'View', 'Channel', 'Begin Time (s)', 'End Time (s)', 'Low Freq (Hz)', 
    # 'High Freq (Hz)', 'Begin File', 'Original Begin Time (s)', 'Tag']
    selection = [0,  # Placeholder, changes when adding the entry to the file writing the file
                 'Spectrogram',  # All selections are on the Spectrogram
                 1,  # We create monochannel audio so all is on channel 1
                 save_sel_dict['Begin Time (s)'] - save_sel_dict['Start export clip'],
                 save_sel_dict['End Time (s)'] - save_sel_dict['Start export clip'],
                 selection_table_af_df['Low Freq (Hz)'].iloc[save_sel_dict['Selection #']],
                 selection_table_af_df['High Freq (Hz)'].iloc[save_sel_dict['Selection #']],
                 export_filename + '.flac',
                 selection_table_af_df['File Offset (s)'].iloc[save_sel_dict['Selection #']],
                 selection_table_af_df[save_sel_dict['Label key']].iloc[save_sel_dict['Selection #']]]

    # Write in the selection table (.txt)
    write_selection_table(os.path.join(export_settings['Annotation export folder'], export_filename + '.txt'),
                          selection, export_label=export_settings['Export label'])

    # Write in the golbal csv file (.csv)
    write_annotation_csv(os.path.join(export_settings['Export folder'],
                                      export_settings['Original project name'],
                                      export_settings['Original project name'] + '_annotations.csv'),
                         selection, export_label=export_settings['Export label'])

    # Write in the file association (.csv)
    map_audio_selection(os.path.join(export_settings['Export folder'], export_settings['Original project name'],
                                     export_settings['Original project name'] + '_audio_seltab_map.csv'),
                        os.path.join(export_settings['Audio export folder'], export_filename + '.flac'),
                        os.path.join(export_settings['Annotation export folder'], export_filename + '.txt'))


# -------------------
# Benchmark functions

def benchmark_size_estimator(selection_table_df, export_settings, label_key):
    """
    Estimates the benchmark size based on the provided selection table and export settings.

    Inputs:
        - selection_table_df: DataFrame containing the selection table.
        - export_settings: Dictionary containing export settings.

    Returns:
        - Estimated benchmark size.

    This function estimates the benchmark size based on the provided selection table and export settings. It performs the following steps:

    Note: This function relies on helper functions such as 'get_number_clips' and 'check_bitdepth' for certain calculations.
    """

    # 1) Run tests on the selection table

    # List unique audio files in the selection table
    unique_audiofiles = selection_table_df['Begin Path'].unique()

    # Test if the selected export_settings['Audio duration (s)'] can fit in individual audio files
    clip_number = get_number_clips(unique_audiofiles, export_settings['Audio duration (s)'])

    # Test if the bit depth is ok
    check_bitdepth(export_settings)

    # 2) Get the number of audio files that will be created
    export_filename_list = []
    count_benchmark_clips = 0

    # Go through each audio file
    for ind_af in range(len(unique_audiofiles)):
        # Load a second of the file to get the metadata
        x, fs_original = librosa.load(unique_audiofiles[ind_af], offset=0.0, duration=1, sr=None, mono=False)

        # Test if x is multi-channel
        nb_ch = x.ndim

        # Go through each channel 
        for ch in range(nb_ch):
            # From the selection table, get the subset of selections that correspond to this specific audio file and channel
            selection_table_af_df = selection_table_df[(selection_table_df['Begin Path'] == unique_audiofiles[ind_af])
                                                       & (selection_table_df['Channel'] == ch + 1)]

            # If the selection table dataframe is not empty
            if not selection_table_af_df.empty:
                # For each selection
                for sel in range(len(selection_table_af_df)):
                    # Get begin and end time of the selection
                    begin_time = selection_table_af_df['File Offset (s)'].iloc[sel]
                    end_time = (begin_time + selection_table_af_df['End Time (s)'].iloc[sel]
                                - selection_table_af_df['Begin Time (s)'].iloc[sel])

                    # Check which clip chuncks this selection is associated with
                    sel_in_clip_begintime = np.floor(begin_time / export_settings['Audio duration (s)'])
                    sel_in_clip_endtime = np.floor(end_time / export_settings['Audio duration (s)'])

                    # If both begin and end time are in a single clip chunck
                    if sel_in_clip_begintime == sel_in_clip_endtime:

                        # Get the timing of the export clip (s)
                        start_clip = sel_in_clip_begintime * export_settings['Audio duration (s)']
                        end_clip = start_clip + export_settings['Audio duration (s)']

                        # Get the export audio file name in the format
                        # <Project>_<OriginalFileName>_<OriginalSamplingFrequency>_<OriginalChannel>.flac
                        export_filename = (export_settings['Original project name'] + '_' +
                                           os.path.splitext(
                                               os.path.basename(selection_table_af_df['Begin Path'].iloc[sel]))[0]
                                           + '_' + 'ch' + "{:02d}".format(ch + 1) + '_' +
                                           "{:04d}".format(int(np.floor(start_clip))) + 's')

                        # Test if the export audio file already exists otherwise, create it
                        if export_filename not in export_filename_list:
                            export_filename_list.append(export_filename)
                            count_benchmark_clips += 1

    # 3) Calculate the size
    bd = int(export_settings['Bit depth'])
    flac_compression = 0.5
    bit_rate = bd * export_settings['fs (Hz)']
    audio_file_size_byte = bit_rate * export_settings[
        'Audio duration (s)'] * 1 / 8  # nb channels/ nb bits per bytes (8)
    dataset_size_byte = audio_file_size_byte * count_benchmark_clips

    # 4) Display 
    print(
        f"File size are estimated with a flac compression factor of {int(flac_compression * 100)}% which may vary depending on the file.")
    print(f"Estimated file size ... {int(np.round(audio_file_size_byte * 10 ** (-6) * flac_compression))} MB")

    if np.round(dataset_size_byte * 10 ** (-6) * flac_compression) > 999:
        print(
            f" > Estimated Benchmark dataset size ... {int(np.round(dataset_size_byte * 10 ** (-9) * flac_compression))} GB")
    else:
        print(
            f" > Estimated Benchmark dataset size ... {int(np.round(dataset_size_byte * 10 ** (-6) * flac_compression))} MB")


def benchmark_creator(selection_table_df, export_settings, label_key):
    """
    Creates a benchmark based on the provided selection table and export settings.

    Inputs:
        - selection_table_df: DataFrame containing the selection table.
        - export_settings: Dictionary containing export settings.

    Outputs:
        - Created benchmark.

    This function creates a benchmark based on the provided selection table and export settings. It performs the following steps:

    1) Lists unique audio files in the selection table.
    2) Retrieves the bit depth from the export settings.
    3) Iterates through each audio file and channel:
        a) Loads a second of the audio file to retrieve metadata.
        b) Determines the original sampling frequency for file naming.
        c) Checks if the audio data is multi-channel.
        d) Filters selections corresponding to the current audio file and channel.
        e) For each selection:
            i) Identifies the clip chunk associated with the selection.
            ii) Creates a dictionary with variables for the export.
            iii) Calls the 'exports' function to export audio and annotation files.
            iv) Handles split annotations if required by export settings.

    Note: This function relies on helper functions such as 'get_bitdepth', 'get_print_fs', and 'exports' for certain calculations and export operations.
    """

    # List unique audio files in the selection table
    unique_audiofiles = selection_table_df['Begin Path'].unique()

    # Get the bit depth
    bit_depth = get_bitdepth(export_settings)

    # Get total number of clips
    tot_clips = 0

    # Go through each audio file
    for ind_af in tqdm(range(len(unique_audiofiles))):

        # Load a second of the file to get the metadata
        x, fs_original = librosa.load(unique_audiofiles[ind_af], offset=0.0, duration=1, sr=None, mono=False)

        # Take note of the sampling frequency for the file naming system
        fs_original_print = get_print_fs(fs_original)

        # Test if x is multi-channel
        nb_ch = x.ndim

        # Go through each channel 
        for ch in range(nb_ch):
            # From the selection table, get the subset of selections that correspond to this specific audio file and channel
            selection_table_af_df = selection_table_df[(selection_table_df['Begin Path'] == unique_audiofiles[ind_af])
                                                       & (selection_table_df['Channel'] == ch + 1)]

            # If the selection table dataframe is not empty
            if not selection_table_af_df.empty:
                # For each selection
                for sel in range(len(selection_table_af_df)):
                    # Get begin and end time of the selection
                    begin_time = selection_table_af_df['File Offset (s)'].iloc[sel]
                    end_time = (begin_time + selection_table_af_df['End Time (s)'].iloc[sel]
                                - selection_table_af_df['Begin Time (s)'].iloc[sel])

                    # Check which clip chuncks this selection is associated with
                    sel_in_clip_begintime = np.floor(begin_time / export_settings['Audio duration (s)'])
                    sel_in_clip_endtime = np.floor(end_time / export_settings['Audio duration (s)'])

                    # If both begin and end time are in a single clip chunck, that is default and will always be done
                    if sel_in_clip_begintime == sel_in_clip_endtime:

                        # Get the timing of the export clip (s)
                        start_clip = sel_in_clip_begintime * export_settings['Audio duration (s)']
                        end_clip = start_clip + export_settings['Audio duration (s)']

                        # Create the dictionnary that will have all of the variables for the exports
                        save_sel_dict = {
                            'Selection #': sel,  # Selection number in the table
                            'fs_original_print': fs_original_print,  # Original sampling frequency
                            'Channel': ch,  # Channel
                            'Start export clip': start_clip,  # Timing of thebeginint of the export clip (s)
                            'Bit depth': bit_depth,  # Bit depth, in correcto format
                            'Label key': label_key,  # Key to the label column in the selection table
                            'Begin Time (s)': begin_time,  # Time to start the annotation
                            'End Time (s)': end_time  # Time to end the annotation
                        }

                        # Export everything
                        exports(export_settings, selection_table_af_df, save_sel_dict)
                        tot_clips += 1

                    # When an annotation is at the limit between two export audio files, 
                    # If there is sufficient amount on either/both sides, keep it if (export_settings['Split export selections'][0] is True)  
                    elif export_settings['Split export selections'][0] is True:
                        # Test if the duration before the split is sufficient
                        if abs(sel_in_clip_endtime * export_settings['Audio duration (s)'] - begin_time) >= \
                                export_settings['Split export selections'][1]:
                            # Get the timing of the export clip (s)
                            start_clip = sel_in_clip_begintime * export_settings['Audio duration (s)']
                            end_clip = start_clip + export_settings['Audio duration (s)']

                            # Update the begin and end time of the split annotation
                            begin_time = selection_table_af_df['File Offset (s)'].iloc[sel]
                            end_time = end_clip

                            # Create the dictionnary that will have all of the variables for the exports
                            save_sel_dict = {
                                'Selection #': sel,  # Selection number in the table
                                'fs_original_print': fs_original_print,  # Original sampling frequency
                                'Channel': ch,  # Channel
                                'Start export clip': start_clip,  # Timing of thebeginint of the export clip (s)
                                'Bit depth': bit_depth,  # Bit depth, in correcto format
                                'Label key': label_key,  # Key to the label column in the selection table
                                'Begin Time (s)': begin_time,  # Time to start the annotation
                                'End Time (s)': end_time  # Time to end the annotation
                            }

                            # Export everything
                            exports(export_settings, selection_table_af_df, save_sel_dict)
                            tot_clips += 1
                        # Test if the duration after the split is sufficient
                        elif abs(end_time - sel_in_clip_endtime * export_settings['Audio duration (s)']) >= \
                                export_settings['Split export selections'][1]:
                            # Get the timing of the export clip (s)
                            start_clip = sel_in_clip_endtime * export_settings['Audio duration (s)']
                            end_clip = start_clip + export_settings['Audio duration (s)']

                            # Update the begin and end time of the split annotation
                            begin_time = start_clip
                            end_time = (selection_table_af_df['File Offset (s)'].iloc[sel] +
                                        selection_table_af_df['End Time (s)'].iloc[sel]
                                        - selection_table_af_df['Begin Time (s)'].iloc[sel])

                            # Create the dictionnary that will have all of the variables for the exports
                            save_sel_dict = {
                                'Selection #': sel,  # Selection number in the table
                                'fs_original_print': fs_original_print,  # Original sampling frequency
                                'Channel': ch,  # Channel
                                'Start export clip': start_clip,  # Timing of thebeginint of the export clip (s)
                                'Bit depth': bit_depth,  # Bit depth, in correcto format
                                'Label key': label_key,  # Key to the label column in the selection table
                                'Begin Time (s)': begin_time,  # Time to start the annotation
                                'End Time (s)': end_time  # Time to end the annotation
                            }

                            # Export everything
                            exports(export_settings, selection_table_af_df, save_sel_dict)
                            tot_clips += 1
                    else:
                        # If the selection is not comparised in the export clip, then do not save it, and print
                        printselnb = selection_table_af_df['Selection'].iloc[sel]
                        head, tail = os.path.split(selection_table_af_df['Begin Path'].iloc[sel])
                        print(f'Ignored annotation...  Selection # {printselnb}, File {tail}, Channel {ch + 1}, {begin_time}-{end_time} s')


    print(f'Total number of clips: {tot_clips}')