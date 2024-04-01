# Create Benchmark Dataset Python script
#
# Léa Bouffaut, Ph.D. -- K. Lisa Yang Center for Conservation Bioacoustics, Cornell University
# lea.bouffaut@cornell.edu
#
# e.g. runs in Pycharm

import benchmark_dataset_creator as bc
import pandas as pd

# User-defined export settings dictionaryYY
export_settings = {
    'Original project name': '2021_CLOCCB_BermudaPlantBank_S1105',
    'Audio duration (s)': 300,
    'fs (Hz)': 8000,
    'Bit depth': 24,
    'Export label': 'Tags',
    'Split export selections': [True, 1],
    'Export folder': 'benchmark_data'
    }


# Run check on the user-defined entries
bc.check_export_settings(export_settings)

# User-defined path to selection table(s)
selection_table_path = '/Volumes/DCLDE/projects/2022_CLOCCB_IthacaNY_S1112/Atlantic_whales/2021_CLOCCB_BermudaPlantBank_S1105/annotations/'
bc.check_selection_tab(selection_table_path)

# Create directories
bc.create_path(export_settings)

# Load selection table
selection_table_df = bc.load_selection_table(selection_table_path)

if selection_table_df.empty == False:
    print(selection_table_df)

# User-defined label key, should be in the Selection table keys displaid above
label_key = 'Call Type'

# Test selection table and estimate size
# Remove duplicates (e.g., if we have both the spectrogram and waveform view)
selection_table_df.drop_duplicates(subset='Begin Time (s)', keep="last");

# Estimate the size of the dataset
bc.benchmark_size_estimator(selection_table_df, export_settings, label_key)

# Check & update labels
# Get a list of unique labels from the selection table
unique_labels = selection_table_df[label_key].unique()

# Print the list of unique labels
print('Unique label list:')
for lab in unique_labels:
    print(lab)

# New label dictionnary
new_labels_dict = {
    'NARW': 'EUBGLA.NWAO.Upcall',
    'na': 'BALMUS.NWAO.Dcall',
}

# Swap the labels
selection_table_df = bc.update_labels(selection_table_df, new_labels_dict, label_key)

# Create the dataset
import time
start_time = time.time()

bc.benchmark_creator(selection_table_df, export_settings, label_key)

print(f'The Benchmark Dataset Creator took {time.time() - start_time} s to run')