import streamlit as st
import datetime as dt
import timezonefinder, pytz
import json


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


def test_json_fields(json_data):
    """
    Tests whether a JSON file has the specified fields and validates their formats.

    Inputs:
        - json_data: A dictionary representing the JSON data.

    Raises:
        - ValueError: If any required field is missing in the JSON data or if any field has an invalid format.
    """
    missing_data = False

    with open(json_data, "r") as file:
        json_data = json.load(file)

    print(json_data)

    required_fields = [
        "Original data",
        "Benchmarked data"
    ]

    for field in required_fields:
        if field not in json_data:
            missing_data = True
            raise ValueError(f"Missing field: {field}")

    if "Original data" in json_data:
        original_data = json_data["Original data"]
        original_data_fields = [
            "Project ID",
            "Deployment ID",
            "Data stewardship",
            "Instrument",
            "Deployment",
            "Sampling details",
            "Annotations",
            "Target signals",
            "Annotation protocol"
        ]

        for field in original_data_fields:
            if field not in original_data:
                missing_data = True
                raise ValueError(f"Missing field in 'Original data': {field}")

        if "Sampling details" in original_data:
            sampling_details = original_data["Sampling details"]
            sampling_details_fields = [
                "Time",
                "Digital sampling"
            ]

            for field in sampling_details_fields:
                if field not in sampling_details:
                    missing_data = True
                    raise ValueError(f"Missing field in 'Sampling details': {field}")

            if "Time" in sampling_details:
                time = sampling_details["Time"]
                time_fields = [
                    "UTC Start",
                    "UTC End",
                    "Local Start",
                    "Local End"
                ]

                for field in time_fields:
                    if field not in time:
                        missing_data = True
                        raise ValueError(f"Missing field in 'Time': {field}")

                    # Validate time format for UTC and Local timestamps
                    if field.startswith("UTC") or field.startswith("Local"):
                        try:
                            dt.datetime.strptime(time[field], "%Y-%m-%dT%H:%M:%SZ")
                        except ValueError:
                            missing_data = True
                            raise ValueError(f"Invalid format for '{field}': {time[field]}")

            if "Digital sampling" in sampling_details:
                digital_sampling = sampling_details["Digital sampling"]
                digital_sampling_fields = [
                    "Sample rate (kHz)",
                    "Sample Bits",
                    "Clipping",
                    "Data Modifications"
                ]

                for field in digital_sampling_fields:
                    if field not in digital_sampling:
                        missing_data = True
                        raise ValueError(f"Missing field in 'Digital sampling': {field}")

                    # Validate sample rate
                    if field == "Sample rate (kHz)" and not isinstance(digital_sampling[field], (int, float)):
                        missing_data = True
                        raise ValueError(f"Invalid format for 'Sample rate (kHz)': {digital_sampling[field]}")

                    # Validate sample bits
                    if field == "Sample Bits" and digital_sampling[field] not in [8, 16, 24]:
                        missing_data = True
                        raise ValueError(f"Invalid value for 'Sample Bits': {digital_sampling[field]}")

                    # Validate clipping
                    if field == "Clipping" and digital_sampling[field] not in ["Yes", "No"]:
                        missing_data = True
                        raise ValueError(f"Invalid value for 'Clipping': {digital_sampling[field]}")

        if "Data stewardship" in original_data:
            data_stewardship = original_data["Data stewardship"]
            for person in data_stewardship:
                required_person_fields = ["Role", "Name", "Affiliation", "Email Address"]
                for person_field in required_person_fields:
                    if person_field not in person:
                        missing_data = True
                        raise ValueError(f"Missing field in 'Data stewardship' for person: {person_field}")

        if "Instrument" in original_data:
            instrument = original_data["Instrument"]
            required_instrument_fields = ["Type", "Settings"]
            for field in required_instrument_fields:
                if field not in instrument:
                    missing_data = True
                    raise ValueError(f"Missing field in 'Instrument': {field}")

        if "Deployment" in original_data:
            deployment = original_data["Deployment"]
            required_deployment_fields = ["Position", "Height/depth (m)", "Terrain elevation/water depth (m)"]
            for field in required_deployment_fields:
                if field not in deployment:
                    missing_data = True
                    raise ValueError(f"Missing field in 'Deployment': {field}")

            if "Position" in deployment:
                position = deployment["Position"]
                if "Lat." not in position or "Lon." not in position:
                    missing_data = True
                    raise ValueError("Missing 'Lat.' or 'Lon.' in 'Position'")
                if not isinstance(position["Lat."], float) or not isinstance(position["Lon."], float):
                    missing_data = True
                    raise ValueError("'Lat.' and 'Lon.' in 'Position' must be floats")
                if not (-90.0 <= position["Lat."] <= 90.0):
                    missing_data = True
                    raise ValueError("'Lat.' in 'Position' must be between -90.0 and 90.0")
                if not (-180.0 <= position["Lon."] <= 180.0):
                    missing_data = True
                    raise ValueError("'Lon.' in 'Position' must be between -180.0 and 180.0")
                if not round(position["Lat."], 6) == position["Lat."]:
                    missing_data = True
                    raise ValueError("'Lat.' in 'Position' must have precision of up to 6 decimal places")
                if not round(position["Lon."], 6) == position["Lon."]:
                    missing_data = True
                    raise ValueError("'Lon.' in 'Position' must have precision of up to 6 decimal places")

    return missing_data


def transform_original_metadata_to_ASA_standard(dict):
    """
        Transforms original metadata dictionary to the ASA (Acoustical Society of America) standard format.

        Inputs:
            - dict: Original metadata dictionary to be transformed.

        Returns:
            - Transformed metadata dictionary in the ASA standard.
    """

    # Global
    dict["ProjectId"] = dict.pop("Project ID")
    dict["DeploymentId"] = dict.pop("Deployment ID")

    # Data Stewardship
    dict["DataStewardship"] = dict.pop("Data stewardship")
    # Each person is entered as an element of the dict["DataStewardship"]  list,
    # so we need to deal with this slightly differently.
    for entry in range(len(dict["DataStewardship"])):
        dict["DataStewardship"][entry]["EmailAddress"] = \
            dict["DataStewardship"][entry].pop("Email Address")

    # Deployment
    dict['Deployment']["ElevationInstrument_m"] = dict['Deployment'].pop(
        "Height/depth (m)")
    dict['Deployment']["Elevation_m"] = dict[
        'Deployment'].pop("Terrain elevation/water depth (m)")

    # Sampling details
    dict["SamplingDetails"] = dict.pop("Sampling details")

    # Sampling details - Time
    dict["SamplingDetails"]["Timestamp"] = dict["SamplingDetails"].pop("Time")
    dict["SamplingDetails"]["Timestamp"]["StartUTC"] = \
        dict["SamplingDetails"]["Timestamp"].pop("UTC Start")
    dict["SamplingDetails"]["Timestamp"]["EndUTC"] = \
        dict["SamplingDetails"]["Timestamp"].pop("UTC End")
    dict["SamplingDetails"]["Timestamp"]["StartLocal"] = \
        dict["SamplingDetails"]["Timestamp"].pop("Local Start")
    dict["SamplingDetails"]["Timestamp"]["EndLocal"] = \
        dict["SamplingDetails"]["Timestamp"].pop("Local End")

    # Sampling details - Digital sampling
    dict["SamplingDetails"]["DigitalSampling"] = dict["SamplingDetails"].pop(
        "Digital sampling")
    dict["SamplingDetails"]["DigitalSampling"]["SampleRate_kHz"] = \
        dict["SamplingDetails"]["DigitalSampling"].pop("Sample rate (kHz)")
    dict["SamplingDetails"]["DigitalSampling"]["SampleBits"] = \
        dict["SamplingDetails"]["DigitalSampling"].pop("Sample Bits")
    dict["SamplingDetails"]["DigitalSampling"]["DataModifications"] = \
        dict["SamplingDetails"]["DigitalSampling"].pop("Data Modifications")

    # Annotations
    dict["Annotations"]["TargetSignals"] = dict["Annotations"].pop("Target signals")
    dict["Annotations"]["NonTargetSignals"] = dict["Annotations"].pop(
        "Non-target signals")
    dict["Annotations"]["AnnotationProtocol"] = dict["Annotations"].pop(
        "Annotation protocol")
    return dict


def transform_export_metadata_to_ASA_standard(export_metadata_dict):
    """
        Transforms original metadata dictionary to the ASA (Acoustical Society of America) standard format.

        Inputs:
            - export_metadata_dict: Original metadata dictionary to be transformed.

        Returns:
            - Transformed metadata dictionary in the ASA standard.
    """

    export_metadata_dict["ProjectId"] = export_metadata_dict.pop("Project ID")
    export_metadata_dict["DeploymentId"] = export_metadata_dict.pop("Deployment ID")

    export_metadata_dict['SignalProcessing']=export_metadata_dict.pop('Signal Processing')

    export_metadata_dict["DigitalSampling"] = export_metadata_dict.pop("Digital sampling")
    export_metadata_dict["DigitalSampling"]["NewAudioDuration_s"] = export_metadata_dict["DigitalSampling"].pop(
        "Audio duration (s)")
    export_metadata_dict["DigitalSampling"]["NewSampleRate_kHz"] = export_metadata_dict["DigitalSampling"].pop(
        "fs (Hz)")
    export_metadata_dict["DigitalSampling"]["NewSampleBits"] = export_metadata_dict["DigitalSampling"].pop("Bit depth")

    export_metadata_dict["Selections"] = export_metadata_dict.pop("Selections")
    export_metadata_dict["Selections"]["ExportLabel"] = export_metadata_dict["Selections"].pop("Export label")
    export_metadata_dict["Selections"]["SplitExportSelections_bool_s"] = export_metadata_dict["Selections"].pop(
        "Split export selections")
    export_metadata_dict["Annotations"]["UsedLabelList"] = export_metadata_dict["Annotations"].pop(
        "Used Label List")

    export_metadata_dict["ExportFolders"] = export_metadata_dict.pop("Export folders")
    export_metadata_dict["ExportFolders"]["ExportFolder"] = export_metadata_dict["ExportFolders"].pop("Export folder")
    export_metadata_dict["ExportFolders"]["AudioExportFolder"] = export_metadata_dict["ExportFolders"].pop(
        "Audio export folder")
    export_metadata_dict["ExportFolders"]["AnnotationExportFolder"] = export_metadata_dict["ExportFolders"].pop(
        "Annotation export folder")
    export_metadata_dict["ExportFolders"]["MetadataFolder"] = export_metadata_dict["ExportFolders"].pop(
        "Metadata folder")
    export_metadata_dict["ExportFolders"]["MetadataFileJSON"] = export_metadata_dict["ExportFolders"].pop(
        "Metadata file")
    export_metadata_dict["ExportFolders"]["AnnotationFileCSV"] = export_metadata_dict["ExportFolders"].pop(
        "Annotation CSV file")
    export_metadata_dict["ExportFolders"]["Audio-SeltabMapFileCSV"] = export_metadata_dict["ExportFolders"].pop(
        "Audio-Seltab Map CSV file")

    return export_metadata_dict
