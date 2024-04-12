# Streamlit app page 2, Metadata input
# This page is associated with a series of functions, in create_folders_functions.py
# The text help for streamlit user inputs is integrated in help_dictionary.py in
# the folders dict

import streamlit as st
import help_dictionary as hd
import create_metadata_functions as cm
import create_folders_functions as cf
import os
import shutil

# Page title (tab and page), Header
st.set_page_config(
    page_title='Benchmark Dataset Creator: Project',
)
st.title('Benchmark Metadata Creator')
st.header('Project creator')

# Create a "staged" version of the program so not all shows up at once
if 'stage' not in st.session_state:
    st.session_state.stage = 0


def set_state(i):
    st.session_state.stage = i


# 1) Collect info on project & project ID
if st.session_state.stage >= 0:
    st.subheader('Project information')

    # Create the dictionary to store the information on the export folders
    export_folder_dictionary = {
        'Project ID': st.text_input(
            'Project ID',
            value="e.g., 2013_UnivMD_Maryland_71485",
            type="default",
            help=hd.folder['Project ID'],
            label_visibility="visible"),
        'Deployment ID': "{:02d}".format(st.number_input(
            'Deployment ID',
            value=int(1.0),
            min_value=int(1),
            max_value=None,
            format='%02d',
            step=1,
            help=hd.folder['Deployment ID'],
            label_visibility="visible")),

        'Export folder': st.text_input(
            'Export folder',
            value="e.g., benchmark_data",
            type="default",
            help=hd.folder['Export folder'],
            label_visibility="visible")
    }

    st.button('Create Export folders', on_click=cm.set_state, args=[1])

# 2) Construct paths for audio and annotations folders based on export settings
if st.session_state.stage >= 1:
    # <Export Folder>/<'Deployment ID'>_<'Project ID'>/audio/
    # <Export Folder>/<'Deployment ID'>_<'Project ID'>/annotations/

    # path names
    audio_path = os.path.join(export_folder_dictionary['Export folder'],
                              export_folder_dictionary['Project ID'] + '_' +
                              export_folder_dictionary['Deployment ID'],
                              'audio')
    annot_path = os.path.join(export_folder_dictionary['Export folder'],
                              export_folder_dictionary['Project ID'] + '_' +
                              export_folder_dictionary['Deployment ID'],
                              'annotations')
    metadata_path = os.path.join(export_folder_dictionary['Export folder'],
                                 export_folder_dictionary['Project ID'] + '_' +
                                 export_folder_dictionary['Deployment ID'])

    export_folder_dictionary['Audio export folder'] = audio_path
    export_folder_dictionary['Annotation export folder'] = annot_path
    export_folder_dictionary['Metadata folder'] = metadata_path

    # Metadata, annotation csv and audio-selection table map names
    metadata_filename = \
        os.path.join(export_folder_dictionary['Metadata folder'],
                     export_folder_dictionary['Project ID'] + '_' + \
                     export_folder_dictionary['Deployment ID'] + \
                     '_metadata.json')

    annotation_csv_filename = \
        os.path.join(export_folder_dictionary['Metadata folder'],
                     export_folder_dictionary['Project ID'] + '_' + \
                     export_folder_dictionary['Deployment ID']
                     + '_annotations.csv')
    audio_sel_map_csv_filename = \
        os.path.join(export_folder_dictionary['Metadata folder'],
                     export_folder_dictionary['Project ID'] + '_' + \
                     export_folder_dictionary['Deployment ID']
                     + '_audio_seltab_map.csv')

    export_folder_dictionary['Metadata file'] = metadata_filename
    export_folder_dictionary['Annotation CSV file'] = annotation_csv_filename
    export_folder_dictionary['Audio-Seltab Map CSV file'] = audio_sel_map_csv_filename


    # Create directories
    # Option 1 -- The audio folder does not exist in path
    if not os.path.exists(audio_path):
        # Create the audio and annotations folders
        os.makedirs(audio_path)
        os.makedirs(annot_path)

        st.success(':white_check_mark: New folders created!')
        st.session_state.stage = 2

    # Option 2 -- the audio folder already exists
    else:
        # Display a warning message
        st.write(f'Warning: This folder already exists, data may be deleted: \n')

        output = st.empty()
        with cf.st_capture(output.code):
            cf.path_print(os.path.join(export_folder_dictionary['Export folder'],
                                       export_folder_dictionary['Project ID'] + '_' +
                                       export_folder_dictionary['Deployment ID']))

        col1, col2, col3, col4 = st.columns([0.2, 0.2, 0.4, 0.3])
        # Ask the user whether to delete existing data
        if col1.button('Delete data', help=None, on_click=set_state, args=[2]):
            # Delete existing audio and annotations folders
            shutil.rmtree(audio_path)
            shutil.rmtree(annot_path)

            # Recreate audio and annotations folders
            os.makedirs(audio_path)
            os.makedirs(annot_path)

            st.success(':white_check_mark: Data successfully deleted & new folders created!')

        if col2.button('Abort', help=None, on_click=set_state, args=[1]):
            # Prompt the user to change the export folder path
            output = st.empty()
            with cf.st_capture(output.code):
                raise ValueError("Please change the export folder path")

if st.session_state.stage >= 2:
    # Show the info on the sidebar
    st.sidebar.subheader('Project settings')
    st.sidebar.write('Project ID')
    st.sidebar.success(export_folder_dictionary['Project ID'])
    st.sidebar.write('Deployment ID')
    st.sidebar.success(export_folder_dictionary['Deployment ID'])
    st.sidebar.write('Export folder')
    st.sidebar.success(export_folder_dictionary['Export folder'])

    # Save
    st.session_state.export_folder_dictionary = export_folder_dictionary

    # Activate next session state
    st.session_state.stage = 3
    link_to_metadata = "pages" + os.sep + "2_Metadata_creator.py"
    st.page_link(link_to_metadata, label=":green[Continue to Metadata Creator]", icon="➡️")
