# Update the path creation for the app
@st.cache_data
def create_path_app(export_settings):
    """
    Function to create export folders following this architecture:
    Export folder/
    |... Original project name/
    |... |... audio/
    |... |... annotations/

    Input:
        - export_settings: Dictionary containing export settings.
    Output:
        - status: Boolean True for ready False for not ready

    Displays a warning if the folders already exist, which can be overwritten based on user input.
    """
    # Construct paths for audio and annotations folders based on export settings
    audio_path = os.path.join(export_settings['Export folder'], export_settings['Original project name'], 'audio')
    annot_path = os.path.join(export_settings['Export folder'], export_settings['Original project name'], 'annotations')
    status = False

    # If the audio folder does not exist in path
    if not os.path.exists(audio_path):
        # Create the audio and annotations folders
        os.makedirs(audio_path)
        os.makedirs(annot_path)
        # Update export settings with the paths
        export_settings['Audio export folder'] = audio_path
        export_settings['Annotation export folder'] = annot_path
        status = True

    # If the audio folder already exists
    else:
        status = False
        # Display a warning message
        st.write(f'Warning: This folder already exists, data may be deleted: \n')

        output = st.empty()
        with st_capture(output.code):
            bc.path_print(os.path.join(export_settings['Export folder'], export_settings['Original project name']))

        # Ask the user whether to delete existing data
        if st.button('Delete data', help=None, on_click=None):
            # Delete existing audio and annotations folders
            shutil.rmtree(audio_path)
            shutil.rmtree(annot_path)

            # Recreate audio and annotations folders
            os.makedirs(audio_path)
            os.makedirs(annot_path)

            # Update export settings with the new paths
            export_settings['Audio export folder'] = audio_path
            export_settings['Annotation export folder'] = annot_path
            status = True

        elif st.button('Abort', help=None, on_click=None):
            # Prompt the user to change the export folder path
            output = st.empty()
            with st_capture(output.code):
                raise ValueError("Please change the export folder path")
            status = False

    return status