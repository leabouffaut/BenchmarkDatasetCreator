# Import convention
import streamlit as st
import benchmark_dataset_creator as bc
import pandas as pd
import os
import shutil

from contextlib import contextmanager, redirect_stdout
from io import StringIO
import pandas as pd



# The function below is to help write the output
@contextmanager
def st_capture(output_func):
    with StringIO() as stdout, redirect_stdout(stdout):
        old_write = stdout.write

        def new_write(string):
            ret = old_write(string)
            output_func(stdout.getvalue())
            return ret

        stdout.write = new_write
        yield

# Create a "staged" version of the program so not all shows up at once
if 'stage' not in st.session_state:
    st.session_state.stage = 0

def set_state(i):
    st.session_state.stage = i


# --------------------------------
st.title('Benchmark Dataset Creator')

# User-defined export settings dictionary
st.subheader('Export settings selection')

# Needed variables
authorized_user_fs = ['1 kHz', '2 kHz', '8 kHz', '16 kHz', '32 kHz', '48 kHz',
                      '96 kHz', '192 kHz', '256 kHz', '384 kHz', '500 kHz']
authorized_user_bit_depth = ['8 Bits', '16 Bits', '24 bits']

export_settings_user_input = \
    {
        'Original project name': st.text_input('Original project name',
                                               value="e.g., 2013_UnivMD_Maryland_71485_MD02",
                                               type="default",
                                               help="This entry will be used to  keep track of the origin of "
                                                    "the data, as a part of the foler architecture and file naming."
                                                    "please do not end this entry by / or \ and avoid spaces",
                                               label_visibility="visible"),

        'Audio duration (s)': st.slider('Audio duration (min)',
                                        min_value=1, max_value=60, value=10, step=1, format='%i',
                                        help="Set  the chosen export audio file duration for the Benchmark "
                                             "dataset in minutes. Our recommendation is to set it to encompass the "
                                             "vocalization(s) of interest but also some context. What is the minimum "
                                             "duration that would represent the signal's repetition or "
                                             "call/cue rate (with several annotations)?",
                                        label_visibility="visible") * 60,

        'fs (Hz)': st.selectbox('Sampling Frequency', authorized_user_fs,
                                index=5,
                                help='The sampling frequency is to be set at minima at double the maximum frequency of'
                                     ' the signals of interest. If relevant, BirdNET uses fs = 48 kHz ',
                                label_visibility="visible"),

        'Bit depth': st.selectbox('Bit depth', authorized_user_bit_depth,
                                  index=2,
                                  help='The bit depth determines the number of possible amplitude values we can record '
                                       'for each audio sample; for SWIFT units, it is set to 16 bits and for Rockhopper '
                                       'to 24 bits.',
                                  label_visibility="visible"),

        'Export label': st.text_input('Export label',
                                      value="Tags",
                                      type="default",
                                      help="Defines the name of the label column for the created export Raven selection "
                                           "tables",
                                      label_visibility="visible"),

        'Split export selections': st.toggle('Split export selections',
                                             value=False,
                                             help="Split export selection specifies the method when a selection is at the "
                                                  "junction between two export audio files."
                                                  "[Recommended] If you have hundreds or even tens of selections of your target signals, "
                                                  "we would recommend to keep this parameter set to false. "
                                                  "[Other] This parameter can be handy if, for example, you "
                                                  "selected long periods of background noise (long compared to the "
                                                  "annotations of signals of interest) that could be split across two audio "
                                                  "export files. In that case, you can set the minimun duration to something"
                                                  " longer than your signals of interest or to 3 s if you plan to work with "
                                                  "BirdNET. Another use case is if you have a very tight selection around "
                                                  "your signal of interest (in time) and want even a very small portion of "
                                                  "that signal to be labeled.",
                                             label_visibility="visible")}


# User-chosen split output
if export_settings_user_input['Split export selections']:
    export_settings_user_input['Split export selections'] = [export_settings_user_input['Split export selections'],
                                                             st.text_input('Minimum duration (s)',
                                                                           value="1",
                                                                           type="default",
                                                                           help="Specify the minimum duration to report an "
                                                                                "annotation in the selection table in seconds",
                                                                           label_visibility="visible")
                                                        ]
else:
    export_settings_user_input['Split export selections'] = [export_settings_user_input['Split export selections'], 0]

export_settings_user_input['Export folder'] = st.text_input('Export folder',
                                                            value="e.g., benchmark_data",
                                                            type="default",
                                                            help="Export folder is where the data will be saved.",
                                                            label_visibility="visible")

if st.session_state.stage == 0:
    # Create a button-controlled creation of the export folder (So that not everything runs)
    st.button('Create Export folders', help=None, on_click=set_state, args=[1])

if st.session_state.stage >= 1:
    # 1) continued, Entries in the correct format
    # Create export_settings based on the user input:
    export_settings = {
        'Original project name': export_settings_user_input['Original project name'],
        'Audio duration (s)': export_settings_user_input['Audio duration (s)'],
        'Export label': export_settings_user_input['Export label'],
        'Split export selections': export_settings_user_input['Split export selections'],
        'Export folder': export_settings_user_input['Export folder']
    }
    # Construct paths for audio and annotations folders based on export settings
    audio_path = os.path.join(export_settings['Export folder'], export_settings['Original project name'], 'audio')
    annot_path = os.path.join(export_settings['Export folder'], export_settings['Original project name'], 'annotations')

    export_settings['Audio export folder'] = audio_path
    export_settings['Annotation export folder'] = annot_path

    # Write fs in the correct format (str to num)
    fs_wanted = [1, 2, 8, 16, 32, 48, 96, 192, 256, 384, 500]
    export_settings['fs (Hz)'] = fs_wanted[authorized_user_fs.index(export_settings_user_input['fs (Hz)'])]*1000

    # Write fs in the correct format (str to num)
    bit_depth_wanted = [8, 16, 24]
    export_settings['Bit depth'] = \
        bit_depth_wanted[authorized_user_bit_depth.index(export_settings_user_input['Bit depth'])]

    # 2) Create directories

    # Option 1 -- The audio folder does not exist in path
    if not os.path.exists(audio_path):
        # Create the audio and annotations folders
        os.makedirs(audio_path)
        os.makedirs(annot_path)

        st.session_state.stage = 2

    # Option 2 -- the audio folder already exists
    else:   #os.path.exists(audio_path):
        # Display a warning message
        st.write(f'Warning: This folder already exists, data may be deleted: \n')

        output = st.empty()
        with st_capture(output.code):
            bc.path_print(os.path.join(export_settings['Export folder'], export_settings['Original project name']))

        # Ask the user whether to delete existing data
        if st.button('Delete data', help=None, on_click=set_state, args=[2]):
            # Delete existing audio and annotations folders
            shutil.rmtree(audio_path)
            shutil.rmtree(annot_path)

            # Recreate audio and annotations folders
            os.makedirs(audio_path)
            os.makedirs(annot_path)

            #output = st.empty()
            #with st_capture(output.code):
            st.success('Data deleted')


        if st.button('Abort', help=None, on_click=set_state, args=[1]):
            # Prompt the user to change the export folder path
            output = st.empty()
            with st_capture(output.code):
                raise ValueError("Please change the export folder path")

if st.session_state.stage >= 2:
   # 3) Run check on the user-defined entries and show output
    output = st.empty()
    with st_capture(output.code):
        bc.check_export_settings(export_settings)

    st.subheader('Load selections')
    # # User-defined path to selection table(s)
    selection_table_path = st.text_input('Path to a selection table or selection table folder',
                                         value="SelectionTable/MD03_truth_selections.txt",
                                         type="default",
                                         help="(1) a complete path to a <b>selection table</b> if dealing with a single "
                                                  "audio file in total or a project with multiple audio files, e.g. "
                                                  "`'SelectionTable/MD03_truth_selections.txt'`"
                                                  "(2) a path to a <b>folder</b> if dealing with one selection table associated"
                                                  " with a single audio file, e.g., `'SelectionTables/'`",
                                         label_visibility="visible")

    # 4) Load selection table and show output
    output = st.empty()
    with st_capture(output.code):
        selection_table_df = bc.load_selection_table(selection_table_path)

    # 5) Run bc.check_selection_tab and show output of the function
    output = st.empty()
    with st_capture(output.code):
        bc.check_selection_tab(selection_table_path)

    # 6) Show selection table
    col1, col2 = st.columns([3, 1])
    col1.subheader('Uploaded Selection table')
    if not selection_table_df.empty:
        col1.dataframe(selection_table_df)

    # 7) Ask for user-defined label key, should be in the Selection table keys displayed above
    col2.subheader('Label')
    label_key = col2.text_input('Selection table label',
                              value="e.g., Tags",
                              type="default",
                              help="User-defined label key, should be in the displayed Selection table",
                              label_visibility="visible",
                              on_change=set_state, args=[3]),

if st.session_state.stage >= 3:
    label_key=label_key[0]

    # 8) Remove duplicates (e.g., if we have both the spectrogram and waveform view)
    selection_table_df.drop_duplicates(subset='Begin Time (s)', keep="last")

    # 9) Estimate the size of the dataset and show output

    st.subheader('Estimate Benchmark Dataset size') #TODO: show something that indicates it's running
    with st.spinner("Creating the Benchmark dataset..."):
        output = st.empty()
        with st_capture(output.code):
            bc.benchmark_size_estimator(selection_table_df, export_settings, label_key)

    # 10) Check & update labels
    st.subheader('Edit labels')
    # Get a list of unique labels from the selection table
    unique_labels = selection_table_df[label_key].unique()

    # Create a dataframe
    remap_label_df = pd.DataFrame({'Original labels': unique_labels,
                                   'New labels': unique_labels})
    # Show dataframe
    new_labels_dict = st.data_editor(remap_label_df)

    # Show button for creating Benchmark dataset
    st.button('Create Benchmark Dataset', help=None, on_click=set_state, args=[4])

if st.session_state.stage >= 4:

    # 11) Swap the labels #TODO
    #selection_table_df = bc.update_labels(selection_table_df, new_labels_dict, label_key)

    # 12) Create the dataset
    with st.spinner("Creating the Benchmark dataset..."):
        bc.benchmark_creator(selection_table_df, export_settings, label_key) #TODO: show something that indicates it's running

    st.success('Benchmark dataset successfully created!')
            ## New label dictionary
            #new_labels_dict = {}
            #st.write(len(new_labels['Original labels']))

            #for ii in range(int(len(new_labels['Original labels']))):
            #    print(ii)
            #    print(new_labels['Original labels'].iloc(ii))
            #    print(new_labels['New labels'].iloc(ii))



            # Swap the labels
            #selection_table_df = bc.update_labels(selection_table_df, new_labels_dict, label_key)

            # Create the dataset


