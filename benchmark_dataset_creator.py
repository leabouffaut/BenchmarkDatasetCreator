# Benchmark Dataset Creator functions
#
# Léa Bouffaut, Ph.D. -- K. Lisa Yang Center for Conservation Bioacoustics, Cornell University
# lea.bouffaut@cornell.edu

import os
import sys
import shutil

import numpy as np
from scipy import signal
import pandas as pd
import librosa
import soundfile as sf
from tqdm.notebook import tqdm

# ---------------------------
#  User interaction functions
def query_yes_no(question, default="yes"):
    """
    Ask a yes/no question via raw_input() and return their answer.

    Inputs:
        - question: A string that is presented to the user.
        - default: The presumed answer if the user just hits <Enter>. It must be "yes" (the default), "no", or None (meaning an answer is required from the user).

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


def path_print(startpath):
    
    """
    Prints the content of the folder designated by startpath
    """
   
    # Iterate through the directory tree starting from 'startpath'
    for root, dirs, files in os.walk(startpath):
        
        # Determine the depth of the current directory relative to 'startpath'
        level = root.replace(startpath, '').count(os.sep)
        
        # Calculate the indentation for displaying directory structure
        indent = ' ' * 4 * (level)
       
        # Print the name of the current directory
        print('{}{}/'.format(indent, os.path.basename(root)))
        
        # Calculate the indentation for displaying files within the directory
        subindent = ' ' * 4 * (level + 1)
        
        # Iterate through the files in the current directory
        for f in files:
            # Print the name of each file within the directory
            print('{}{}'.format(subindent, f))

def create_path(export_settings):
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
            
            
# ------------------------
#  Data checking functions
def check_bitdepth(export_settings):
    """
    Checks if the user-input bit depth is a possible value, based on formats supported by soundfile.write for FLAC files.

    Displays an error message if the value is not supported.
    """
    # List of authorized bit depths user inputs and corresponding soundfile FLAC bit depths
    authorized_user_bit_depth = [8, 16, 24]
    sf_flac_bit_depth = ['PCM_S8', 'PCM_16', 'PCM_24']
    
    # Test if the specified bit depth is supported
    if export_settings['Bit depth'] not in authorized_user_bit_depth:
        # Print an error message if the specified bit depth is not supported
        print(f"Error: Non-supported Bit depth, please select on of the following values:\n ...{authorized_user_bit_depth}")
            
            
def check_selection_table(df, label_key):
    """
    This function checks whether all of the required fields are present in the selection table.

    Inputs:
        - df: The dataframe of the selection table.
        - label_key: The name of the field for the label column.

    Output:
        - Printed text indicating whether the required fields are present.
    """

    # List of all desired fields in the selection table
    wanted_fields = ['Begin Time (s)', 'End Time (s)', 'Low Freq (Hz)', 'High Freq (Hz)', 'File Offset (s)', 'Begin Path', label_key]

    # Check if each desired field is present in the selection table, and if not, add it to the 'missing' list
    missing = []
    for item in wanted_fields:
        if item not in df.columns:
            missing.append(item)

    # Inform the user about the presence of all required fields
    if not missing:
        print('All required fields are in the selection table')
    else:
        # Inform the user about missing fields in the selection table
        print(f'Error: The following field(s) is missing from the selection table:', end='\n--> ') 
        for field in missing:
            print(field)

            
# ----------------------------------------------
# Manipulate existing selection tables functions

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
        number_clip.append(int(np.floor(fdur/clip_duration)))
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
    
    header = ['Selection', 'View', 'Channel', 'Begin Time (s)', 'End Time (s)', 'Low Freq (Hz)', 'High Freq (Hz)', 'Begin File', 'Original Begin Time (s)', export_label]
    
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
    entry[0] = count +1
    
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
    #[0 = 'Selection', 1= 'View', 2= 'Channel', 3= 'Begin Time (s)', 4= 'End Time (s)', 
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
    """
    
    # 1) Run tests on the selection table
    # Test if all necessary fields are present
    check_selection_table(selection_table_df, label_key)

    # List unique audio files in the selection table
    unique_audiofiles = selection_table_df['Begin Path'].unique()

    # Test if the selected export_settings['Audio duration (s)'] can fit in individual audio files
    clip_number = get_number_clips(unique_audiofiles, export_settings['Audio duration (s)'])
    
    # Test if the bit depth is ok
    check_bitdepth(export_settings)
        
    
    # 2) Get the number of audio files that will be created
    export_filename_list=[]
    count_benchmark_clips=0

    # Go through each audio file
    for ind_af in range(len(unique_audiofiles)):
        # Load a second of the file to get the metadata
        x, fs_original = librosa.load(unique_audiofiles[ind_af], offset=0.0, duration=1, sr=None, mono=False)

        # Test if x is multi-channel
        nb_ch, np_samples= np.shape(x)

        # Go through each channel 
        for ch in range(nb_ch): 
            # From the selection table, get the subset of selections that correspond to this specific audio file and channel
            selection_table_af_df = selection_table_df[(selection_table_df['Begin Path']==unique_audiofiles[ind_af])
                                                       &(selection_table_df['Channel']==ch+1)]

            # If the selection table dataframe is not empty
            if not selection_table_af_df.empty:

                # For each selection
                for sel in range(len(selection_table_af_df)):
                    # Get begin and end time of the selection
                    begin_time = selection_table_af_df['File Offset (s)'].iloc[sel]
                    end_time = (begin_time + selection_table_af_df['End Time (s)'].iloc[sel] 
                                - selection_table_af_df['Begin Time (s)'].iloc[sel])

                    # Check which clip chuncks this selection is associated with
                    sel_in_clip_begintime = np.floor(begin_time/export_settings['Audio duration (s)'])
                    sel_in_clip_endtime = np.floor(end_time/export_settings['Audio duration (s)'])
                    
                    # If both begin and end time are in a single clip chunck
                    if sel_in_clip_begintime == sel_in_clip_endtime:

                        # Get the timing of the export clip (s)
                        start_clip = sel_in_clip_begintime*export_settings['Audio duration (s)']
                        end_clip = start_clip + export_settings['Audio duration (s)']

                        # Get the export audio file name in the format
                        # <Project>_<OriginalFileName>_<OriginalSamplingFrequency>_<OriginalChannel>.flac
                        export_filename = (export_settings['Original project name'] + '_' + 
                                            os.path.splitext(os.path.basename(selection_table_af_df['Begin Path'].iloc[sel]))[0] 
                                           + '_' + 'ch' + "{:02d}".format(ch+1) + '_' + 
                                           "{:04d}".format(int(np.floor(start_clip))) +'s')

                        # Test if the export audio file already exists otherwise, create it
                        if export_filename not in export_filename_list:
                            export_filename_list.append(export_filename)
                            count_benchmark_clips += 1
    
    # 3) Calculate the size
    bd = int(export_settings['Bit depth'])
    flac_compression = 0.5
    bit_rate = bd*export_settings['fs (Hz)']
    audio_file_size_byte = bit_rate * export_settings[ 'Audio duration (s)']* 1/8 # nb channels/ nb bits per bytes (8)
    dataset_size_byte = audio_file_size_byte*count_benchmark_clips
    
    # 4) Display 
    print(f"File size are estimated with a flac compression factor of {int(flac_compression*100)}% which may vary depending on the file.")
    print(f"Estimated file size ... {int(np.round(audio_file_size_byte*10**(-6)*flac_compression))} MB")
    
    if np.round(dataset_size_byte*10**(-6)*flac_compression)>999:
        print(f"Estimated Benchmark dataset size ... {int(np.round(dataset_size_byte*10**(-9)*flac_compression))} GB")
    else:
        print(f"Estimated Benchmark dataset size ... {int(np.round(dataset_size_byte*10**(-6)*flac_compression))} MB")
        

def benchmark_creator(selection_table_df, export_settings, label_key):
    """
    Creates a benchmark based on the provided selection table and export settings.

    Inputs:
        - selection_table_df: DataFrame containing the selection table.
        - export_settings: Dictionary containing export settings.

    Outputs:
        - Created benchmark.
    """
    
    # List unique audio files in the selection table
    unique_audiofiles = selection_table_df['Begin Path'].unique()
    
    # Get the bit depth
    authorized_user_bit_depth = [8, 16, 24]
    sf_flac_bit_depth = ['PCM_S8', 'PCM_16', 'PCM_24'] # This is only valid for flac files. 
                                                       # write sf.available_subtypes('WAV') to get the bit depth 
                                                       # format supported for wav files
    
    bit_depth = sf_flac_bit_depth[authorized_user_bit_depth.index(export_settings['Bit depth'])]
    
    # Go through each audio file
    for ind_af in tqdm(range(len(unique_audiofiles))):

        # Load a second of the file to get the metadata
        x, fs_original = librosa.load(unique_audiofiles[ind_af], offset=0.0, duration=1, sr=None, mono=False)

        # Take note of the sampling frequency for the file naming system
        if fs_original >= 1000:
            fs_original_print = str(int(np.floor(fs_original/1000)))+'kHz'
        else:
            fs_original_print = str(int(fs_original)) + 'Hz'
        
        # Test if x is multi-channel
        nb_ch, np_samples= np.shape(x)

        # Go through each channel 
        for ch in range(nb_ch): 
            # From the selection table, get the subset of selections that correspond to this specific audio file and channel
            selection_table_af_df = selection_table_df[(selection_table_df['Begin Path']==unique_audiofiles[ind_af])
                                                       &(selection_table_df['Channel']==ch+1)]

            # If the selection table dataframe is not empty
            if not selection_table_af_df.empty:
                # For each selection
                for sel in range(len(selection_table_af_df)):
                    # Get begin and end time of the selection
                    begin_time = selection_table_af_df['File Offset (s)'].iloc[sel]
                    end_time = (begin_time + selection_table_af_df['End Time (s)'].iloc[sel] 
                                - selection_table_af_df['Begin Time (s)'].iloc[sel])

                    # Check which clip chuncks this selection is associated with
                    sel_in_clip_begintime = np.floor(begin_time/export_settings['Audio duration (s)'])
                    sel_in_clip_endtime = np.floor(end_time/export_settings['Audio duration (s)'])

                    # If both begin and end time are in a single clip chunck
                    if sel_in_clip_begintime == sel_in_clip_endtime:

                        # Get the timing of the export clip (s)
                        start_clip = sel_in_clip_begintime*export_settings['Audio duration (s)']
                        end_clip = start_clip + export_settings['Audio duration (s)']

                        # Get the export audio file name in the format
                        # <Project>_<OriginalFileName>_<OriginalSamplingFrequency>_<OriginalChannel>.flac
                        export_filename = (export_settings['Original project name'] + '_' + 
                                            os.path.splitext(os.path.basename(selection_table_af_df['Begin Path'].iloc[sel]))[0] + '_' + 
                                           str(fs_original_print) + '_' + 'ch' + "{:02d}".format(ch+1) + '_' + 
                                           "{:04d}".format(int(np.floor(start_clip))) +'s')

                        # Test if the export audio file already exists otherwise, create it
                        if not os.path.exists(os.path.join(export_settings['Audio export folder'], export_filename+'.flac')):

                            # Load and resample the the audio
                            x_clip, fs = librosa.load(unique_audiofiles[ind_af], offset=start_clip, 
                                                      duration=export_settings['Audio duration (s)'], 
                                                      sr=export_settings['fs (Hz)'], mono=False, res_type='soxr_vhq')
                            # Keep the wanted channel
                            x_clip = x_clip[ch,:]

                            # Save clip
                            sf.write(os.path.join(export_settings['Audio export folder'], export_filename +'.flac'),
                                     x_clip, fs, bit_depth) #.astype(np.int24)
                            
                            #print('Saved: ' + export_filename +'.flac')


                        # Create/fill the selection table for this clip with the format 
                        #['Selection', 'View', 'Channel', 'Begin Time (s)', 'End Time (s)', 'Low Freq (Hz)', 
                        # 'High Freq (Hz)', 'Begin File', 'Original Begin Time (s)', 'Tag']
                        selection = [0, # Placeholder, changes when adding the entry to the file writing the file
                                    'Spectrogram', # All selections are on the Spectrogram
                                    1, # We create monochannel audio so all is on channel 1
                                    begin_time - start_clip,
                                    end_time - start_clip,
                                    selection_table_af_df['Low Freq (Hz)'].iloc[sel],
                                    selection_table_af_df['High Freq (Hz)'].iloc[sel],
                                    export_filename +'.flac',
                                    selection_table_af_df['File Offset (s)'].iloc[sel],
                                    selection_table_af_df[label_key].iloc[sel]]

                        # Write in the selection table (.txt)
                        write_selection_table(os.path.join(export_settings['Annotation export folder'], export_filename +'.txt'), 
                                              selection, export_label=export_settings['Export label'])

                        # Write in the golbal csv file (.csv)
                        write_annotation_csv(os.path.join(export_settings['Export folder'], 
                                                          export_settings['Original project name'],  
                                                          export_settings['Original project name'] + '_annotations.csv'), 
                                             selection, export_label=export_settings['Export label'])

                        # Write in the file association (.csv)
                        map_audio_selection(os.path.join(export_settings['Export folder'], export_settings['Original project name'],
                                                         export_settings['Original project name'] + '_audio_seltab_map.csv'),
                                            os.path.join(export_settings['Audio export folder'], export_filename +'.flac'),
                                            os.path.join(export_settings['Annotation export folder'], export_filename +'.txt'))

                    else:
                        # If the selection is not comparised in the export clip, then do not save it, and print
                        printselnb = selection_table_af_df['Selection'].iloc[sel]
                        head, tail = os.path.split(selection_table_af_df['Begin Path'].iloc[sel])
                        print(f'Ignored annotation...  Selection # {printselnb}, File {tail}, Channel {ch+1}, {begin_time}-{end_time} s')