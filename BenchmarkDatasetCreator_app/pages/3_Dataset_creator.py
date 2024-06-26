# Streamlit app page 3, Dataset creator
# This page is associated with a series of functions, in dataset.py
# The text help is in
# Imports
import sys
import os
import streamlit as st
import pandas as pd
import json
import copy

sys.path.insert(1, '.' + os.sep)
from BenchmarkDatasetCreator_app import help_dictionary as hd
from BenchmarkDatasetCreator import dataset, folders, metadata


# Titles
st.set_page_config(
    page_title='Benchmark Dataset Creator: Dataset',
)
st.title('Benchmark Dataset Creator')
st.header('Create benchmark dataset')

# Retrieve data from previous page
if not hasattr(st.session_state, 'export_folder_dictionary'):
    st.error('Project information missing')
    link_to_project = "pages" + os.sep + "1_Project_creator.py"
    st.page_link(link_to_project, label=":white[Go to Project creator]", icon="➡️")

elif not hasattr(st.session_state, 'export_folder_dictionary'):
    st.error('Metadata missing')
    link_to_project = "pages" + os.sep + "2_Metadata_creator.py"
    st.page_link(link_to_project, label=":white[Go to Metadata creator]", icon="➡️")

else:
    export_folder_dictionary = st.session_state.export_folder_dictionary
    original_data_dictionary = st.session_state.original_data_dictionary

    # Show the info on the sidebar
    st.sidebar.subheader('Project settings')
    st.sidebar.write('Export folder')
    st.sidebar.success(export_folder_dictionary['Export folder'])
    st.sidebar.write('Project ID')
    st.sidebar.success(export_folder_dictionary['Project ID'])
    st.sidebar.write('Deployment ID')
    st.sidebar.success(export_folder_dictionary['Deployment ID'])
    st.sidebar.write('Metadata file')
    st.sidebar.success(export_folder_dictionary['Metadata file'])

# Initialize the data saving variables
label_key = []
export_settings = {}

# TODO: Continue editing the species list csv
# TODO: have all of the text in a language-specific file -> https://phrase.com/blog/posts/translate-python-gnu-gettext/
# TODO: Finalize this piece of code with the new functions
# TODO: add BDC info to the metadata
# could be a solution

# User-defined export settings dictionary
if st.session_state.stage >= 9:
    st.subheader('Export settings selection')

    # Needed variables
    authorized_user_fs = ['1 kHz', '2 kHz', '8 kHz', '16 kHz', '32 kHz', '48 kHz',
                          '96 kHz', '192 kHz', '256 kHz', '384 kHz', '500 kHz']
    authorized_user_bit_depth = ['8 Bits', '16 Bits', '24 bits']

    export_settings_user_input = {
        #'Original project name':
        #    st.text_input(
        #        'Original project name',
        #        value="e.g., 2013_UnivMD_Maryland_71485_MD02",
        #        type="default",
        #        help="This entry will be used to  keep track of the origin of "
        #             "the data, as a part of the folder architecture and file naming."
        #             "please do not end this entry by / or \ and avoid spaces",
        #        label_visibility="visible"),

        'Audio duration (s)':
            st.slider(
                'Audio duration (min)',
                min_value=1, max_value=60, value=10, step=1, format='%i',
                help=hd.export['Digital sampling']['Audio duration (s)'],
                label_visibility="visible") * 60,

        'fs (Hz)':
            st.selectbox(
                'Sampling Frequency', authorized_user_fs,
                index=5,
                help=hd.export['Digital sampling']['fs (Hz)'],
                label_visibility="visible"),

        'Bit depth':
            st.selectbox(
                'Bit depth', authorized_user_bit_depth,
                index=2,
                help=hd.export['Digital sampling']['Bit depth'],
                label_visibility="visible"),

        'Export label':
            st.text_input(
                'Export label',
                value="Tags",
                type="default",
                help=hd.export['Selections']['Export label'],
                label_visibility="visible"),

        'Split export selections':
            st.toggle(
                'Split export selections',
                value=False,
                help=hd.export['Selections']['Split export selections']['General'],
                label_visibility="visible")}

    # User-chosen split output
    if export_settings_user_input['Split export selections']:
        export_settings_user_input['Split export selections'] = [
            export_settings_user_input['Split export selections'],
            st.number_input(
                'Minimum duration (s)',
                value=float(1.0),
                min_value=float(0),
                max_value=float(
                    export_settings_user_input[
                        'Audio duration (s)']),
                format='%.1f',
                step=0.1,
                help=hd.export['Split export selections']['Minimum duration (s)'],
                label_visibility="visible")
        ]
    else:
        export_settings_user_input['Split export selections'] = [
            export_settings_user_input['Split export selections'], 0]


    st.button('Done', help=None, on_click=metadata.set_state, args=[10])

if st.session_state.stage >= 10:
    # 1) continued, Entries in the correct format
    # Create export_settings based on the user input:
    export_settings = {
        'Project ID': export_folder_dictionary['Project ID'],
        'Deployment ID': export_folder_dictionary['Deployment ID'],
        'Method': hd.benchmark_creator_info['Method'],
        'Signal Processing': hd.benchmark_creator_info['Signal Processing'],
        'Digital sampling': {
            'Audio duration (s)': export_settings_user_input['Audio duration (s)'],
        },

        'Selections': {
            'Export label': export_settings_user_input['Export label'],
            'Split export selections': export_settings_user_input['Split export selections'],
        },

        'Export folders': {
            'Export folder': export_folder_dictionary['Export folder'],
            'Audio export folder': export_folder_dictionary['Audio export folder'],
            'Annotation export folder': export_folder_dictionary['Annotation export folder'],
            'Metadata folder': export_folder_dictionary['Metadata folder'],
            'Metadata file': export_folder_dictionary['Metadata file'],
            'Annotation CSV file': export_folder_dictionary['Annotation CSV file'],
            'Audio-Seltab Map CSV file': export_folder_dictionary['Audio-Seltab Map CSV file']
        },
        }

    # Write fs in the correct format (str to num)
    fs_wanted = [1, 2, 8, 16, 32, 48, 96, 192, 256, 384, 500]
    export_settings['Digital sampling']['fs (Hz)'] = \
        fs_wanted[authorized_user_fs.index(export_settings_user_input['fs (Hz)'])] * 1000

    # Write fs in the correct format (str to num)
    bit_depth_wanted = [8, 16, 24]
    export_settings['Digital sampling']['Bit depth'] = \
        bit_depth_wanted[authorized_user_bit_depth.index(export_settings_user_input['Bit depth'])]

    # 3) Run check on the user-defined entries and show output
    output = st.empty()
    with folders.st_capture(output.code):
        dataset.check_export_settings(export_settings)

    st.subheader('Load selections')
    # # User-defined path to selection table(s)
    selection_table_path = \
        st.text_input(
            'Path to a selection table or selection table folder',
            value="e.g., SelectionTable/MD02_truth_selections.txt",
            type="default",
            help=hd.export['Selections']['Path'],
            label_visibility="visible")

    # 4) Load selection table and show output
    output = st.empty()
    with folders.st_capture(output.code):
        selection_table_df = dataset.load_selection_table(selection_table_path)

    # 5) Run dataset.check_selection_tab and show output of the function
    output = st.empty()
    with folders.st_capture(output.code):
        dataset.check_selection_tab(selection_table_path)

    # 6) Show selection table
    col3, col4 = st.columns([3, 1])
    col3.subheader('Uploaded Selection table')
    if not selection_table_df.empty:
        col3.dataframe(selection_table_df)

    # 7) Ask for user-defined label key, should be in the Selection table keys displayed above
    col4.subheader('Label')
    label_key = \
        col4.text_input(
            'Selection table label',
            value="e.g., Tags",
            type="default",
            help=hd.export['Selections']['Label'],
            label_visibility="visible",
            on_change=metadata.set_state, args=[11]),

if st.session_state.stage >= 11:
    label_key = label_key[0]

    # 8) Remove duplicates (e.g., if we have both the spectrogram and waveform view)
    selection_table_df.drop_duplicates(subset='Begin Time (s)', keep="last")

    # 9) Estimate the size of the dataset and show output
    st.subheader('Estimate Benchmark Dataset size')
    with st.spinner("Estimating the size of the Benchmark dataset..."):
        output = st.empty()
        with folders.st_capture(output.code):
            dataset.benchmark_size_estimator(selection_table_df, export_settings, label_key)

    # 10) Check & update labels
    st.subheader('Edit labels (Optional)')
    # Get a list of unique labels from the selection table
    unique_labels = selection_table_df[label_key].unique()

    # Create a dataframe
    remap_label_df = pd.DataFrame({'Original labels': unique_labels,
                                   'New labels': unique_labels})
    # Show dataframe
    col5, col6 = st.columns([1, 1.5])
    new_labels_df = \
        col5.data_editor(
            remap_label_df,
            num_rows="fixed",
            disabled=["Original labels"],
            hide_index=True)
    col6.write(hd.export['Selections']['Label editor']['Help'])
    col6.image(
        'docs/illustrations/‎method_schematicV2_zoom.png',
        caption=None, width=None, use_column_width=True,
        clamp=False,
        channels="RGB", output_format="auto")

    col6.write(hd.export['Selections']['Label editor']['Label list'])

    # Show button for creating Benchmark dataset
    col6.button('Continue', help=None, on_click=metadata.set_state, args=[12])

if st.session_state.stage >= 12:

    # Show button for creating Benchmark dataset
    st.button('Create Benchmark Dataset', help=None, on_click=metadata.set_state, args=[13])

if st.session_state.stage >= 13:
    # 11) Swap the labels
    # We want labels in a dictionary format with Key (old label): Value (new label)
    new_labels_dict = new_labels_df.set_index('Original labels')['New labels'].to_dict()

    # Update the selection table
    selection_table_df_updated = dataset.update_labels(selection_table_df, new_labels_dict, label_key)

    # Add the new labels to the Metadata dictionary
    export_settings['Annotations'] = {
        'LabelKey': label_key,
        'Used Label List': list(new_labels_dict.values()),
        'Standard': hd.benchmark_creator_info['Annotations']['Standard'],
    }

    # 12) Write the metadata
    dict_oj = copy.deepcopy(original_data_dictionary)
    dict_export = copy.deepcopy(export_settings)

    metadata_save = {
        'Original data': metadata.transform_original_metadata_to_ASA_standard(dict_oj),
        'Benchmarked data': metadata.transform_export_metadata_to_ASA_standard(dict_export)
    }

    with open(export_folder_dictionary['Metadata file'], 'w') as fp:
        json.dump(metadata_save, fp, indent=4)

    # 13) Create the dataset
    with st.spinner("Creating the Benchmark dataset..."):
        dataset.benchmark_creator(selection_table_df_updated, export_settings, label_key)

    st.success('Benchmark dataset successfully created!')
