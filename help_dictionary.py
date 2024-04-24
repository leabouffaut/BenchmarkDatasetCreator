metadata = {
    'Project ID': # Becomes ProjectId in the standard
        "The name of your project. This entry will be used to  keep track of the origin of the data, "
        "as a part of the folder architecture and file naming. Please do not end this entry by / or \ and "
        "avoid spaces",
    'Deployment ID': # Becomes DeploymentId in the standard
        "A number used to help distinguish groups of deployments",
    'Data stewardship': {
        'General': "Information and contact of the people/institutions/groups that contributed to this dataset. "
                   "Show and fill the fields of entry by pushing the 'Add co-creator' button",
        'Role': '',
        'Name': '',
        'Affiliation': '',
        'Email Address': '',
        'DOI': "(Optional) DOI of an associated publication."
    },
    'Instrument': {
        'General': "Information on the recording equipment",
        'Type': 'Select the recording equipment used to collect the original data.',
        'Settings': 'If Other is selected in recording equipment, please add details '
                    'about the recording set up in this field otherwise (Optional) Details '
                    'on instrument settings, e.g., gain, recording schedule, etc.',
    },
    'Deployment': {
        'General': "Information on the deployment location and conditions. "
                   "The Latitude and Longitude (°) entries take 6 decimals to enable sub-meter "
                   "precision at all latitudes. The map is used as a visual tool to verify "
                   "user entry.",
        'Position': {
            'Lat.': '',
            'Lon.': '',
        },
        'Height/depth (m)': # becomes ElevationInstrument_m to follow the standard
            '<b>Terrestrial</b>: recorder height is reported relative to ground level.'
            '<b>Aquatic/Marine</b>: recorder depths are entered relative to the surface',
        'Terrain elevation/water depth (m)': # becomes Elevation_m to follow the standard
            'Terrain elevation and water depth relative to sea level reported at the '
            'position of the recorder',
        'Env. context': '(Optional) Description of the environmental context , e.g., vegetation, weather, ocean-bottom '
                        'type, sea state, etc.',
    },
    'Sampling details': {
        'General': 'Information on the recording sampling. Times are entered either in local time or UTC.',
        'Time': { # Becomes Timestamp in the standard
            'UTC Start': '',
            'UTC End': '',
            'Local Start': '',
            'Local End': '',
        },
        'Digital sampling': {
            'Sample rate (kHz)': # Becomes SampleRate_kHz in the standard
                'Recordings sampling frequency',
            'Sample Bits': # Becomes SampleBits in the standard
                'Select the bit depth of the original data. The bit depth determines the number of possible '
                'amplitude values we can record for each audio sample; for SWIFT units, it is set to 16 bits and '
                'for Rockhopper to 24 bits.',
            'Clipping': 'Where there any clipping in the data? Clipping clipping is a form of waveform distortion that '
                        'occurs when an amplifier is pushed beyond its maximum limit (e.g., the source signal is too '
                        'loud), pushing it to overdrive. In that case, the output voltage is pushed to its maximum value.',
            'Data Modifications': '(Optional) Was the data modified e.g., resampled, normalized, filtered etc.?',
        },
    },
    'Annotations': {
        'General': "Fill up information about the annotation protocol",
        'Target signals': {
            'Kind': 'SpeciesID: the label are produced at the species level \n, '
                    'CallID: the labels are produced at the call level',
        },
        'Non-target signals': {
            'Noise': '',
            'Bio': '',
            'Anthro': '',
            'Geo': '',
        },
        'Annotation protocol': "(Optional) Details on the annotation protocol e.g., number of analysts, rules, "
                               "verification protocol etc.",
    }
}

folder = {
    'Project ID': "The name of your project. This entry will be used to  keep track of the origin of the data, "
                  "as a part of the folder architecture and file naming. Please do not end this entry by / or \ and "
                  "avoid spaces",
    'Deployment ID': "A number used to help distinguish groups of deployments",
    'Export folder': "Export folder is where the data and metadata will be saved.",
    'Audio export folder': '',  # Created without user input - Path to export audio
    'Annotation export folder': '',  # Created without user input - Path to export annotations
    'Metadata folder': '',  # Created without user input - Path to export Metadata
    'Metadata file': '',  # Created without user input - Full path + name of the Metadata file
    'Annotation CSV file': '',  # Created without user input - Full path + name of the recap CSV annotation file
    'Audio-Seltab Map CSV file': '',  # Created without user input - Full path + name of the CSV audio-annotation
    # association file

}

url = "https://docs.google.com/spreadsheets/d/1ScxYST26QIGE2d_ovEI1NtyPDmpWeMHJJ2LEu4nFwOw/edit?usp=sharing"

export = {
    'Digital sampling': {
        'Audio duration (s)': "Set  the chosen export audio file duration for the Benchmark dataset in minutes. Our "
                              "recommendation is to set it to encompass the vocalization(s) of interest but also some "
                              "context. What is the minimum duration that would represent the signal's repetition or "
                              "call/cue rate (with several annotations)?",
        'fs (Hz)': 'The sampling frequency is to be set at minima at double the maximum frequency of the signals of '
                   'interest. If relevant, BirdNET uses fs = 48 kHz.',
        'Bit depth': 'The bit depth determines the number of possible amplitude values we can record for each audio '
                     'sample; for SWIFT units, it is set to 16 bits and for Rockhopper to 24 bits.',
    },
    'Selections': {
        'Export label': "Defines the name of the label column for the created export Raven selection tables",
        'Split export selections': {
            'General':
                "Split export selection specifies the method when a selection is at the junction "
                "between two export audio files. [Recommended] If you have hundreds or even tens of "
                "selections of your target signals, we would recommend to keep this parameter set to "
                "false. [Other] This parameter can be handy if, for example, you selected long periods "
                "of background noise (long compared to the annotations of signals of interest) that "
                "could be split across two audio export files. In that case, you can set the minimum "
                "duration to something longer than your signals of interest or to 3 s if you plan to "
                "work with BirdNET. Another use case is if you have a very tight selection around your "
                "signal of interest (in time) and want even a very small portion of that signal to be "
                "labeled.",
            'Minimum duration (s)':
                "Specify the minimum duration to report an annotation in the selection table in seconds",
        },
        'Path':
            "(1) a complete path to a <b>selection table</b> if dealing with a single "
            "audio file in total or a project with multiple audio files, e.g. "
            "`'SelectionTable/MD02_truth_selections.txt'`"
            "(2) a path to a <b>folder</b> if dealing with one selection table associated"
            " with a single audio file, e.g., `'SelectionTables/'`",
        'Label': "User-defined label key, should be a column title in the displayed Selection table",
        'Label editor': {
            'Help': '💡 To update existing labels, edit the `New labels` column.',
            'Label list': "Look up the [Yang Center species list](%s) for existing standardized labels and add yours "
                          "to the list!" % url
        },

    },
    'Export folder': "Export folder is where the data will be saved.",

}
