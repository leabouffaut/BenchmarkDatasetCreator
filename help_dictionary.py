metadata = {
    'Project ID': "The name of your project. This entry will be used to  keep track of the origin of the data, "
                  "as a part of the folder architecture and file naming. Please do not end this entry by / or \ and "
                  "avoid spaces",
    'Deployment ID': "A number used to help distinguish groups of deployments",
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
        'Height/depth (m)': '<b>Terrestrial</b>: recorder height is reported relative to ground level.'
                            '<b>Aquatic/Marine</b>: recorder depths are entered relative to the surface',
        'Terrain elevation/water depth (m)':
            'Terrain elevation and water depth relative to sea level reported at the '
            'position of the recorder',
        'Env. context': '(Optional) Description of the environmental context , e.g., vegetation, weather, ocean-bottom '
                        'type, sea state, etc.',
    },
    'Sampling details': {
        'General': 'Information on the recording sampling. Times are entered either in local time or UTC.',
        'Time': {
            'UTC Start': '',
            'UTC End': '',
            'Local Start': '',
            'Local End': '',
        },
        'Digital sampling': {
            'Sample rate (kHz)': 'Recordings sampling frequency',
            'Sample Bits': 'Select the bit depth of the original data. The bit depth determines the number of possible '
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

export = {

}
