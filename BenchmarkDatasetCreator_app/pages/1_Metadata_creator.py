# Import convention
import streamlit as st
#from datetime import datetime, timezone
import datetime as dt
import benchmark_dataset_creator as bc
import os
import shutil

from contextlib import contextmanager, redirect_stdout
from io import StringIO
import pandas as pd
import json
import timezonefinder, pytz

import datetime as dt
import pytz
import timezonefinder
import streamlit as st

def get_date_time(label, original_data_dictionary):
    """
    Function to obtain date and time information with correct formats.

    Inputs:
        - label (str): Label for the date and time entry.
        - original_data_dictionary (dict): Original data dictionary containing deployment
        information.

    Returns:
        - tuple: A tuple containing the date and time information in UTC and local time formats
        following the ISO-8601 format e.g.,
            * UTC format: 2010-08-27T23:58:03.3975Z
            * Local time format (UTC-7h): 2023-03-15T10:54:00-07:00
    """

    # Create UI layout using Streamlit's columns
    col_label, col_unused, col_utc = st.columns([0.2, 0.2, 0.6])

    # Display label for the date and time entry
    col_label.write(label)

    # Toggle for UTC time
    UTC_bool = col_utc.toggle(
        'UTC',
        value=True,
        help=None,
        key='utc' + label
    )

    # Create UI layout for date and timezone selection
    col_date, col_tz = st.columns([0.7, 0.74])

    # Date input field
    date = col_date.date_input(
        "Date",
        value=None,
        min_value=dt.datetime(1970, 1, 1),
        max_value=dt.datetime.now(),
        format="YYYY-MM-DD",
        key='date' + label
    )

    # Get timezone from latitude and longitude
    tf = timezonefinder.TimezoneFinder()
    default_tz = tf.certain_timezone_at(
        lat=original_data_dictionary['Deployment']['Position']['Lat.'],
        lng=original_data_dictionary['Deployment']['Position']['Lon.']
    )

    # Select local timezone
    if default_tz in pytz.common_timezones:
        local_timezone = col_tz.selectbox(
            'Select local time zone',
            pytz.common_timezones,
            index=pytz.common_timezones.index(default_tz),
            key='tz' + label
        )
    else:
        local_timezone = col_tz.selectbox(
            'Select local time zone',
            pytz.common_timezones,
            key='tz' + label
        )

    # UI layout for time selection
    col_hh, col_mm, col_ss = st.columns(3)

    # Hour input
    time_hh = int(col_hh.number_input(
        'Hour',
        min_value=0,
        max_value=23,
        format='%i',
        step=1,
        key='time_hh' + label
    ))

    # Minute input
    time_mm = int(col_mm.number_input(
        'Minutes',
        min_value=0,
        max_value=59,
        format='%i',
        step=1,
        key='time_mm' + label
    ))

    # Second input
    time_ss = int(col_ss.number_input(
        'Seconds',
        value=float(0),
        min_value=float(0),
        max_value=float(59.9999),
        format='%.4f',
        step=0.0001,
        key='time_ss' + label
    ))

    # Assemble datetime information
    date_time_entry = dt.datetime.combine(
        date, dt.time(hour=time_hh, minute=time_mm, second=time_ss)
    )

    # Convert to UTC or local time based on toggle
    if UTC_bool:
        tz_entry = pytz.timezone('UTC')
        date_time_utc = tz_entry.localize(date_time_entry)
        date_time_local = date_time_utc.astimezone(pytz.timezone(local_timezone))
    else:
        tz_entry = pytz.timezone(local_timezone)
        date_time_local = tz_entry.localize(date_time_entry)
        date_time_utc = date_time_local.astimezone(pytz.timezone('UTC'))

    # Format date and time in ISO format
    date_time_local = str(date_time_local.replace(microsecond=0).isoformat())
    date_time_utc = str(date_time_utc.replace(microsecond=0).isoformat()).replace('+00:00', 'Z')

    return date_time_utc, date_time_local



st.set_page_config(
    page_title='Benchmark Dataset Creator: Metadata',
)
st.title('Benchmark Metadata Creator')

st.header('Information on the original data')

# Create a dictionary that will summarize all user inputs
st.subheader('Project information')
# 1) Collect info on project & project ID
original_data_dictionary = {
    'Project ID': st.text_input(
        'Project ID',
        value="e.g., 2013_UnivMD_Maryland_71485_MD02",
        type="default",
        help="The name of your project",
        label_visibility="visible"),
    'Deployment ID': st.number_input(
        'Deployment ID',
        value=int(1.0),
        min_value=int(1),
        max_value=None,
        format='%i',
        step=1,
        help="Used to help distinguish groups of deployments",
        label_visibility="visible")
}

# 2) Collect info on Data owners/curators
st.subheader('Data stewardship',
             help="Information and contact of the people/institutions/groups that contributed to "
                  "this dataset. Show and fill the fields of entry by pushing the 'Add co-creator' button")

# Create list of authorized roles (based on Zenodo)
authorized_roles = ['Contact person', 'Data collector', 'Data curator', 'Distributor',
                    'Hosting institution', 'Principal Investigator', 'Rights holder', 'Sponsor']


# Function to display a row of input fields for a person's information
def display_input_row(index):
    # Create four columns for each input field: Name, Affiliation, Email Address, Role
    role_col, name_col, affiliation_col, email_col = st.columns(4)

    # Add text input fields for Name, Affiliation, Email Address, and Role
    role_col.selectbox('Role', authorized_roles, key=f'role_{index}')
    name_col.text_input('Name', key=f'name_{index}')
    affiliation_col.text_input('Affiliation', key=f'affiliation_{index}')
    email_col.text_input('Email Address', key=f'email_{index}')


# Function to increase the number of rows when the "Add person" button is clicked
def increase_rows():
    st.session_state['rows'] += 1


# Check if 'rows' is not in the session state and initialize it to 0
if 'rows' not in st.session_state:
    st.session_state['rows'] = 0

# Button to add a new person; calls the increase_rows function when clicked
st.button('Add co-creator', on_click=increase_rows)

# Loop through the number of rows and display input fields for each person
for i in range(st.session_state['rows']):
    display_input_row(i)

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

# Transform the dictionary in the wanted format
original_data_dictionary['Data stewardship'] = people_data

# Optional associated publication DOI
original_data_dictionary['Data stewardship'] = {
    'DOI': st.text_input(
        'Associated publication (DOI) ',
        value="https://doi.org/XX.XXXXX",
        type="default",
        help="DOI of an associated publication (optional).",
        label_visibility="visible")}

# 3) Add information on the instrumentation
st.subheader('Instrumentation',
             help="Information on the recording equipment")

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
        help='Select the recording equipment used to collect the original data.'),
    'Settings': settings_col.text_area(
        'Details on instrument settings',
        placeholder="(Optional) Details on instrument settings, e.g., "
                    "gain, recording schedule, etc.",
        height=None, max_chars=None, key=None,
        help='If Other is selected in recording equipment, '
             'please add details about the recording set up in this field',
        label_visibility="visible")
}

# 4) Add information about the deployment
st.subheader('Deployment',
             help="Information on the deployment location and conditions. "
                  "The Latitude and Longitude (°) entries take 6 decimals to enable sub-meter "
                  "precision at all latitudes. The map is used as a visual tool to verify "
                  "user entry.")

# Create two columns with different width for app display
input_col, map_col = st.columns([0.3, 0.7])

# Get user inputs
original_data_dictionary['Deployment'] = {
    'Position': {
        'Lat.': float(
            input_col.number_input(
                'Recorder latitude (°)',
                value=42.478327,
                min_value=-90.0,
                max_value=90.0,
                format='%.6f',
                step=0.000001,
                label_visibility="visible")),
        'Lon.': float(
            input_col.number_input(
                'Recorder longitude (°)',
                value=-76.450438,
                min_value=-180.0,
                max_value=180.0,
                format='%.6f',
                step=0.000001,
                # help="Enter Longitude",
                label_visibility="visible")),
        'Height/depth (m)': int(
            input_col.number_input('Recorder height/depth (m)',
                                   value=10,
                                   min_value=0,
                                   max_value=None,
                                   format='%i',
                                   step=1,
                                   help='<b>Terrestrial</b>: recorder height is reported relative to ground level.'
                                        '<b>Aquatic/Marine</b>: recorder depths are entered relative to the surface',
                                   label_visibility="visible")),
        'Terrain elevation/water depth (m)': int(
            input_col.number_input(
                'Elevation/water depth (m)',
                value=10,
                min_value=0,
                max_value=None,
                format='%i',
                step=1,
                help='Terrain elevation and water depth relative to sea level reported at the '
                     'position of the recorder',
                label_visibility="visible")),
        'Env. context': input_col.text_area(
            'Details on environmental context',
            placeholder="(Optional) ) Description of the environmental context , e.g., "
                        "vegetation, weather, ocean-bottom type, sea state, etc.",
            label_visibility="visible",
            height=143)
    }
}
# Show map for the user to check their entry
df_map = pd.DataFrame({
    'lat': [original_data_dictionary['Deployment']['Position']['Lat.']],
    'lon': [original_data_dictionary['Deployment']['Position']['Lon.']]
})
map_col.map(df_map, size=5, zoom=15)

# 5) Enter sampling details
st.subheader('Sampling details',
             help=None)

#TODO: add test Start date < end date
start_date_time_utc, start_date_time_local = get_date_time('Recording start',
                                               original_data_dictionary)
end_date_time_utc, end_date_time_local = get_date_time('Recording end',
                                               original_data_dictionary)
# Add times to dictionary
original_data_dictionary['Sampling details']={
        'Time': {
            'UTC Start': start_date_time_utc,
            'UTC End': end_date_time_utc,
            'Local Start': start_date_time_local,
            'Local End': end_date_time_local,
        }}

st.write('Digital sampling')
original_data_dictionary['Sampling details']={
        'Digital sampling': {
            'Sample rate (kHz)': float(
                st.number_input(
                'Sample rate (kHz)',
                value=1.000,
                min_value=0.100,
                max_value=None,
                format='%.3f',
                step=1.000,
                label_visibility="visible")),
            'Sample Bits': int(
                st.number_input(
                'Sample Bits',
                value=8,
                min_value=8,
                max_value=24,
                format='%i',
                step=1,
                label_visibility="visible")),
        },
        'Clipping': 'N', # Options, Y/N/DK
        'Data Modificatons': 'Was the data modified? (resampled, normalized, filtered etc.?)',  # (Optional) free form text
    },

# Final) Submit button to write JSON file
submitted = st.button('Submit')  # , on_click=increase_rows)

if submitted:
    # Write metadata as a json file
    with open('test_write.json', 'w') as fp:
        json.dump(original_data_dictionary, fp, indent=4)
