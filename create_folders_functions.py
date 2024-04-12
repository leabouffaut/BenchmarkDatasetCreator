# Group of functions supporting the creation of the filing system in 1_Project_creator

# Imports
from contextlib import contextmanager, redirect_stdout
from io import StringIO
import os
import sys
import shutil


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


def query_yes_no(question, default="yes"):
    """
    Ask a yes/no question via raw_input() and return their answer.

    Inputs:
        - question: A string that is presented to the user.
        - default: The presumed answer if the user just hits <Enter>. It must be "yes" (the default),
        "no", or None (meaning an answer is required from the user).

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


def path_print(start_path):
    """
    Prints the content of the folder designated by startpath
    """
    # Iterate through the directory tree starting from 'startpath'
    for root, dirs, files in os.walk(start_path):

        # Determine the depth of the current directory relative to 'startpath'
        level = root.replace(start_path, '').count(os.sep)

        # Calculate the indentation for displaying directory structure
        indent = ' ' * 4 * (level)

        # Print the name of the current directory
        print('{}{}/'.format(indent, os.path.basename(root)))

        # Calculate the indentation for displaying files within the directory
        sub_indent = ' ' * 4 * (level + 1)

        # Iterate through the files in the current directory
        for f in files:
            # Print the name of each file within the directory
            print('{}{}'.format(sub_indent, f))


def create_path(export_dict):
    """
    Function to create export folders following this architecture:
    Export folder/
    |... Original project name/
    |... |... audio/
    |... |... annotations/

    # Only used in Jupyter notebooks & .py files, streamlit has a different display system
    Displays a warning if the folders already exist, which can be overwritten based on user input.
    """
    # Construct paths for audio and annotations folders based on export settings
    audio_path = os.path.join(export_dict['Export folder'],
                              export_dict['Project ID'] + '_' +
                              export_dict['Deployment ID'],
                              'audio')
    annot_path = os.path.join(export_dict['Export folder'],
                              export_dict['Project ID'] + '_' +
                              export_dict['Deployment ID'],
                              'annotations')
    export_dict['Audio export folder'] = audio_path
    export_dict['Annotation export folder'] = annot_path

    # If the audio folder does not exist in path
    if not os.path.exists(audio_path):
        # Create the audio and annotations folders
        os.makedirs(audio_path)
        os.makedirs(annot_path)
        # Update export settings with the paths
        export_dict['Audio export folder'] = audio_path
        export_dict['Annotation export folder'] = annot_path

    # If the audio folder already exists
    else:
        # Display a warning message
        print(f'Warning: This folder already exists, data may be deleted: \n')
        print(path_print(os.path.join(export_dict['Export folder'],
                                      export_dict['Project ID'] + '_' +
                                      export_dict['Deployment ID'])))

        # Ask the user whether to delete existing data
        if query_yes_no(f'Delete data?', default="yes"):

            # Delete existing audio and annotations folders
            shutil.rmtree(audio_path)
            shutil.rmtree(annot_path)

            # Recreate audio and annotations folders
            os.makedirs(audio_path)
            os.makedirs(annot_path)

            # Update export settings with the new paths
            export_dict['Audio export folder'] = audio_path
            export_dict['Annotation export folder'] = annot_path
        else:
            # Prompt the user to change the export folder path
            print(f"Please change the export folder path")
