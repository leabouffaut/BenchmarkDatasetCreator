# Streamlit app page 2, Metadata input
# This page is associated with a series of functions, in metadata.py
# The text help for streamlit user inputs is integrated in help_dictionary.py in the metadata dict

# Creates original_data_dictionary

# Imports
import json
import os
import sys

import pandas as pd
import streamlit as st

sys.path.insert(1, '.' + os.sep)
from BenchmarkDatasetCreator_app import help_dictionary as hd
from BenchmarkDatasetCreator import metadata

# Page title (tab and page), Header
st.set_page_config(
    page_title='Benchmark Dataset Creator: Metadata',
)
st.title('Benchmark Dataset Creator')
st.header('Collect metadata')

# Retrieve data from previous page
if not hasattr(st.session_state, 'export_folder_dictionary'):
    st.error('Project information missing')
    link_to_project = "pages" + os.sep + "1_Project_creator.py"
    st.page_link(link_to_project, label=":white[Go to Project creator]", icon="➡️")
else:
    export_folder_dictionary = st.session_state.export_folder_dictionary

    # Show the info on the sidebar
    st.sidebar.subheader('Project settings')
    st.sidebar.write('Project ID')
    st.sidebar.success(export_folder_dictionary['Project ID'])
    st.sidebar.write('Deployment ID')
    st.sidebar.success(export_folder_dictionary['Deployment ID'])
    st.sidebar.write('Export folder')
    st.sidebar.success(export_folder_dictionary['Export folder'])

    # Initialize the data saving dict
    original_data_dictionary = {}

    # 1) Collect info on project & project ID

    # Create the dictionary to store the information
    original_data_dictionary = {
        'Project ID': export_folder_dictionary['Project ID'],
        'Deployment ID': export_folder_dictionary['Deployment ID'],
    }

    if st.session_state.stage >= 3:
        # 2) Collect info on Data owners/curators
        # TODO: Add terms for local/indigenous partners
        # TODO: Land acknowledgment
        st.subheader('Data stewardship',
                     help=hd.metadata['Data stewardship']['General'])

        # Create list of authorized roles (based on Zenodo)
        authorized_roles = ['Contact person', 'Data collector', 'Data analyst', 'Dataset curator', 'Distributor',
                            'Hosting institution', 'Principal Investigator', 'Rights holder', 'Sponsor']

        # Check if 'rows' is not in the session state and initialize it to 0
        if 'rows' not in st.session_state:
            st.session_state['rows'] = 0


        # Add rows
        def increase_rows():
            """
            Function to increase the number of rows when the "Add person" button is clicked
            """
            st.session_state['rows'] += 1


        # Button to add a new person; calls the increase_rows function when clicked
        st.button('Add co-creator', on_click=increase_rows)

        # Loop through the number of rows and display input fields for each person
        for i in range(st.session_state['rows']):
            metadata.display_input_row(i, authorized_roles)

        # Display the entered information for each person as an interactive DataFrame
        # Create a list to store the entered data
        people_data = []

        # Loop through the rows and append the entered data to the list
        for i in range(st.session_state['rows']):
            person_data = {
                'Role': st.session_state[f'role_{i}'],
                'Name': st.session_state[f'name_{i}'],
                'Affiliation': st.session_state[f'affiliation_{i}'],
                'Email Address': st.session_state[f'email_{i}']
            }
            people_data.append(person_data)

        # Create a DataFrame from the collected data
        people_df = pd.DataFrame(people_data)

        # Display the DataFrame
        st.write('Entered dataset co-creators')
        st.dataframe(people_df, use_container_width=True, hide_index=True)

        original_data_dictionary['Data stewardship'] = {
            # Information about permits
            'Permits': st.text_area(
                'Permit # or Permission and permitting authority',
                placeholder=hd.metadata['Data stewardship']['Permits'],
                height=None, max_chars=None, key=None,
                label_visibility="visible"),

            # Optional associated publication DOI
            'DOI': st.text_input(
                'Associated publication (DOI) ',
                value="https://doi.org/XX.XXXXX",
                type="default",
                help=hd.metadata['Data stewardship']['DOI'],
                label_visibility="visible")}

        st.button('Next', key='Next2', help=None, on_click=metadata.set_state, args=[4])

    # 3) Add information on the instrumentation
    if st.session_state.stage >= 4:
        # Save the previous data
        # Transform the dictionary in the wanted format
        original_data_dictionary['Data stewardship'] = people_data

        st.subheader('Instrumentation',
                     help=hd.metadata['Instrument']['General'])

        # Create two columns for app display
        instrumentation_col, settings_col = st.columns(2)

        # List of authorized recording equipment + sort + add "Other" at the end
        authorized_instruments = ['Cornell - SwiftOne', 'Cornell - Swift',
                                  'Cornell - Rockhopper', 'Cornell - MARU',
                                  'Open Acoustic Devices - AudioMoth',
                                  'Open Acoustic Devices - HydroMoth',
                                  "Ocean Instrunents - SoundTrap ST600 STD",
                                  "Ocean Instrunents - SoundTrap ST600 HF",
                                  "Scripps - HARP", "Wildlife Acoustics - Song Meter SM4",
                                  "Wildlife Acoustics - Song Meter Mini 2",
                                  "Wildlife Acoustics - Song Meter Micro",
                                  "Wildlife Acoustics - Song Meter Micro 2",
                                  "Wildlife Acoustics - Song Meter SM4BAT FS",
                                  "Wildlife Acoustics - Song Meter Mini Bat2"]
        authorized_instruments.sort()
        authorized_instruments.append("Other")

        # Add the user inputs to the dictionary
        original_data_dictionary['Instrument'] = {
            'Type': instrumentation_col.selectbox(
                'Select recording equipment',
                authorized_instruments,
                help=hd.metadata['Instrument']['Type']),
            'Settings': settings_col.text_area(
                'Details on instrument settings',
                placeholder=hd.metadata['Instrument']['Settings'],
                height=None, max_chars=None, key=None,
                label_visibility="visible")
        }
        st.button('Next', key='Next3', help=None, on_click=metadata.set_state, args=[5])

    # 4) Add information about the deployment
    if st.session_state.stage >= 5:
        st.subheader('Deployment',
                     help=hd.metadata['Deployment']['General'])

        # Create two columns with different width for app display
        deployment_input_col, map_col = st.columns([0.3, 0.7])

        # Get user inputs
        original_data_dictionary['Deployment'] = {
            'Position': {
                'Lat.': float(
                    deployment_input_col.number_input(
                        'Recorder latitude (°)',
                        value=42.478327,
                        min_value=-90.0,
                        max_value=90.0,
                        format='%.6f',
                        step=0.000001,
                        label_visibility="visible")),
                'Lon.': float(
                    deployment_input_col.number_input(
                        'Recorder longitude (°)',
                        value=-76.450438,
                        min_value=-180.0,
                        max_value=180.0,
                        format='%.6f',
                        step=0.000001,
                        # help="Enter Longitude",
                        label_visibility="visible")),
            },
            'Height/depth (m)': int(
                deployment_input_col.number_input('Recorder height/depth (m)',
                                                  value=10,
                                                  min_value=0,
                                                  max_value=None,
                                                  format='%i',
                                                  step=1,
                                                  help=hd.metadata['Deployment']['Height/depth (m)'],
                                                  label_visibility="visible")),
            'Terrain elevation/water depth (m)': int(
                deployment_input_col.number_input(
                    'Elevation/water depth (m)',
                    value=10,
                    min_value=0,
                    max_value=None,
                    format='%i',
                    step=1,
                    help=hd.metadata['Deployment']['Terrain elevation/water depth (m)'],
                    label_visibility="visible")),
            'Env. context': deployment_input_col.text_area(
                'Details on environmental context',
                placeholder=hd.metadata['Deployment']['Env. context'],
                label_visibility="visible",
                height=143)
        }

        # Show map for the user to check their entry
        df_map = pd.DataFrame({
            'lat': [original_data_dictionary['Deployment']['Position']['Lat.']],
            'lon': [original_data_dictionary['Deployment']['Position']['Lon.']]
        })
        map_col.map(df_map, size=5, zoom=15)
        st.button('Next', key='Next4', help=None, on_click=metadata.set_state, args=[6])

    # 5) Enter sampling details
    if st.session_state.stage >= 6:
        st.subheader('Sampling details',
                     help=hd.metadata['Sampling details']['General'])

        # Declare the dictionary structure for sampling details
        original_data_dictionary['Sampling details'] = {
            'Time': '',
            'Digital sampling': '',
        }
        # Get the start and end time in both local time and UTC
        start_date_time_utc, start_date_time_local = \
            metadata.get_date_time('Recording start', original_data_dictionary)

        end_date_time_utc, end_date_time_local = \
            metadata.get_date_time('Recording end', original_data_dictionary)

        # If the dates are filled
        if (start_date_time_local is not None and end_date_time_local is not None) and \
                (start_date_time_local != '' and end_date_time_local != ''):
            # Check the dates make sense:
            metadata.check_dates(start_date_time_local, end_date_time_local)

            # Fill times in the dictionary
            original_data_dictionary['Sampling details']['Time'] = {
                'UTC Start': start_date_time_utc,
                'UTC End': end_date_time_utc,
                'Local Start': start_date_time_local,
                'Local End': end_date_time_local}

            # Get the information on the digital sampling
            st.write('Digital sampling')

            # Create two columns with different width for app display
            digital_sampling_col, data_mod_col = st.columns([0.5, 0.5])

            # Values for bit depth
            authorized_bit_depths = [8, 16, 24]

            # User inputs for all digital sampling
            original_data_dictionary['Sampling details']['Digital sampling'] = {
                'Sample rate (kHz)': float(digital_sampling_col.number_input(
                    'Sample rate (kHz)',
                    value=1.000,
                    min_value=0.100,
                    max_value=None,
                    format='%.3f',
                    step=1.000,
                    help=
                    hd.metadata['Sampling details']['Digital sampling'][
                        'Sample rate (kHz)'],
                    label_visibility="visible")),

                'Sample Bits': int(digital_sampling_col.selectbox(
                    'Bit depth',
                    authorized_bit_depths,
                    index=1,
                    help=hd.metadata['Sampling details']['Digital sampling'][
                        'Sample Bits'])),

                'Clipping': digital_sampling_col.radio(
                    'Clipping',
                    ['Yes', 'No', 'Don\'t know'],
                    horizontal=True,
                    index=None,
                    help=hd.metadata['Sampling details']['Digital sampling'][
                        'Clipping']),
                'Data Modifications': data_mod_col.text_area(
                    'Data Modifications',
                    placeholder=
                    hd.metadata['Sampling details']['Digital sampling'][
                        'Data Modifications'],
                    label_visibility="visible",
                    height=185)
            }

            st.button('Next', key='Next5', help=None, on_click=metadata.set_state, args=[7])

    # 6) Get information on the annotation protocol
    if st.session_state.stage >= 7:
        st.subheader('Annotations',
                     help=hd.metadata['Annotations']['General'])
        # Add columns
        annotation_questions_col, annotation_protocol_col = st.columns([0.5, 0.5])

        # About the target signals
        annotation_questions_col.write('Target signals')

        # Authorized annotation types
        authorized_annotations = ['SpeciesID', 'CallID']

        # Initialize annotations section of the dictionary
        original_data_dictionary['Annotations'] = {
            'Target signals': '',
            'Non-target signals': '',
            'Annotation protocol': ''
        }

        original_data_dictionary['Annotations']['Target signals'] = {
            'Kind': annotation_questions_col.radio(
                'Annotation type',
                authorized_annotations,
                horizontal=True,
                index=None,
                help=hd.metadata['Annotations']['Target signals']['Kind']
            ),
        }

        # About non-target signals
        annotation_protocol_col.write('Non-target signals')

        # Authorized answers
        yes_no = ['Yes', 'No']

        # noinspection PyTypedDict
        original_data_dictionary['Annotations']['Non-target signals'] = {
            'Noise': annotation_protocol_col.radio(
                'Does the dataset contain a background noise class?',
                yes_no,
                index=None,
                horizontal=True),
            'Bio': '',
            'Anthro': '',
            'Geo': '',
        }

        st.markdown("""
        <style>
        .small-font {
            font-size:14px !important;
        }
        </style>
        """, unsafe_allow_html=True)
        annotation_protocol_col.markdown(
            '<p class="small-font">Does the dataset contain selections with unique labels for:</p>',
            unsafe_allow_html=True)

        original_data_dictionary['Annotations']['Non-target signals']['Bio'] = \
            annotation_protocol_col.radio(
                ':heavy_minus_sign: Other biological sounds (e.g., insect chorus, un-IDed call types, etc)?',
                yes_no,
                index=None,
                horizontal=True,
                help='')
        original_data_dictionary['Annotations']['Non-target signals']['Anthro'] = \
            annotation_protocol_col.radio(
                ':heavy_minus_sign: Anthropogenic sounds (e.g., ship noise, piling, vehicles, chainsaw etc.)?',
                yes_no,
                index=None,
                horizontal=True,
                help='')
        original_data_dictionary['Annotations']['Non-target signals']['Geo'] = \
            annotation_protocol_col.radio(
                ':heavy_minus_sign: Geophysical sounds (e.g., thunder, heavy rain, earthquakes etc.)?',
                yes_no,
                index=None,
                horizontal=True,
                help='')

        # Optional field for annotation protocol

        # Free field for annotation protocol
        original_data_dictionary['Annotations']['Annotation protocol'] = \
            annotation_questions_col.text_area(
                'Annotation protocol',
                placeholder=hd.metadata['Annotations']['Annotation protocol'],
                label_visibility="visible",
                height=254)

        st.button('Submit', key='Submit', help=None, on_click=metadata.set_state, args=[8])

    # 7) Submit button to write JSON file
    if st.session_state.stage >= 8:
        metadata_save = {
            'Original data': metadata.transform_original_metadata_to_ASA_standard(original_data_dictionary),
            'Benchmarked data': ''
        }
        with open(export_folder_dictionary['Metadata file'], 'w') as fp:
            json.dump(metadata_save, fp, indent=4)

        st.success('Metadata successfully created!')

        # Save
        st.session_state.export_folder_dictionary = export_folder_dictionary
        st.session_state.original_data_dictionary =original_data_dictionary

        # Show on sidebar
        st.sidebar.write('Metadata file')
        if st.sidebar.button('Show metadata'):
            st.write('The metadata is saved at:', export_folder_dictionary['Metadata file'])
            st.write('Here is a preview: ')
            st.json(original_data_dictionary)

        # Activate next session state
        st.session_state.stage = 9
        link_to_dataset = "pages" + os.sep + "3_Dataset_creator.py"
        st.page_link(link_to_dataset, label=":green[Continue to Dataset Creator]", icon="➡️")