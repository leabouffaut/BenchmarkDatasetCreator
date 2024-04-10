# Import convention
import streamlit as st
from datetime import datetime, timezone
import benchmark_dataset_creator as bc
import os
import shutil

from contextlib import contextmanager, redirect_stdout
from io import StringIO
import pandas as pd
import json

st.set_page_config(
    page_title='Benchmark Dataset Creator: Metadata',
)
st.title('Benchmark Metadata Creator')

st.subheader('Info. on the original data')


# Create a dictionary that will summarize all user inputs
# 1) Collect info on project & project ID
original_data_dictionary = {
    'Project ID': st.text_input('Project ID',
                                 value="e.g., 2013_UnivMD_Maryland_71485_MD02",
                                 type="default",
                                 help="The name of your project",
                                 label_visibility="visible"),
    'Deployment ID': st.number_input('Deployment ID',
                                     value=int(1.0),
                                     min_value=int(1),
                                     max_value=None,
                                     format='%i',
                                     step=1,
                                     help="Used to help distinguish groups of deployments",
                                     label_visibility="visible")
}

# 2) Collect info on Data owners/curators
st.subheader('Data stewardship', help="Information anc contact of the people/institutions/groups that contributed to this dataset",)

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
st.button('Add person', on_click=increase_rows)

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
st.write('Recap')
st.dataframe(people_df, use_container_width=True, hide_index=True)

# Transform the dictionary in the wanted format
original_data_dictionary['Data stewardship'] = people_data

# Optional associated publication DOI
original_data_dictionary['Data stewardship'] = {
    'DOI': st.text_input('Associated publication (DOI) ',
    value="https://doi.org/XX.XXXXX",
    type="default",
    help="DOI of an assoicated publication (optional).",
    label_visibility="visible")}



# Write metadata as a json file
with open('test_write.json', 'w') as fp:
    json.dump(original_data_dictionary, fp, indent=4)
