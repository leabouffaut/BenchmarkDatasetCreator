import streamlit as st
import datetime as dt
import timezonefinder, pytz

def set_state(i):
    st.session_state.stage = i

# Function definitions
def get_date_time(label, data_dictionary):
    """
    Function to obtain date and time information with correct formats.

    Inputs:
        - label (str): Label for the date and time entry.
        - original_data_dictionary (dict): Original data dictionary containing deployment
        information.
        - st_session_state_stage:

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
        key='date' + label,
    )

    # Get timezone from latitude and longitude
    tf = timezonefinder.TimezoneFinder()
    default_tz = tf.certain_timezone_at(
        lat=data_dictionary['Deployment']['Position']['Lat.'],
        lng=data_dictionary['Deployment']['Position']['Lon.']
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

    if date is not None:
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
    else:
        st.warning('Please enter a valid date')
        date_time_utc = ''
        date_time_local = ''
    return date_time_utc, date_time_local


def check_dates(date_start_local, date_end_local):
    """
    Function to check if the end date occurs before the start date.

    Inputs:
        - date_start_local (str): Start date and time in local time format.
        - date_end_local (str): End date and time in local time format.

    Returns:
        - None: This function doesn't return anything, but it raises an error if the end date occurs before the start date.

    Raises:
        - ValueError: If the end date occurs before the start date, an error is raised indicating the issue.
    """

    # Convert date strings to datetime objects
    date_start = dt.datetime.fromisoformat(date_start_local)
    date_end = dt.datetime.fromisoformat(date_end_local)

    # Check
    if date_end < date_start:
        st.error('The entered recording end occurs before recording start')


# Adding people and contact, by the press of a button
def display_input_row(index, authorized_roles):
    """
    Function to display an input row with fields for Name, Affiliation, Email Address, and Role.

    Inputs:
        - index (int): Index of the input row.
        - authorized_roles (list): List of authorized roles for the Role field.

    Returns:
        - None: This function doesn't return anything, it's responsible for displaying the input row UI.

    Side Effects:
        - Displays input fields for Name, Affiliation, Email Address, and Role on the Streamlit app.

    Note:
        - Each input field has a unique key generated based on the index to ensure proper functioning and reactivity.
    """

    # Create four columns for each input field: Name, Affiliation, Email Address, Role
    role_col, name_col, affiliation_col, email_col = st.columns(4)

    # Add text input fields for Name, Affiliation, Email Address, and Role
    role_col.selectbox('Role', authorized_roles, key=f'role_{index}')
    name_col.text_input('Name', key=f'name_{index}')
    affiliation_col.text_input('Affiliation', key=f'affiliation_{index}')
    email_col.text_input('Email Address', key=f'email_{index}')
