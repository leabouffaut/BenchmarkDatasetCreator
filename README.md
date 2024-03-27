# Benchmark Dataset Creator
Léa Bouffaut, Ph.D. -- K. Lisa Yang Center for Conservation Bioacoustics, Cornell University

lea.bouffaut@cornell.edu

### Motivations and objectives

Many bioacoustic projects are sitting on a goldmine of already annotated datasets. We want to create a standardized pipeline for creating, storing, sharing and
using data that is flexible and repeatable  to train and test AI models for different applications. More details in https://www.overleaf.com/read/yfcgvngmwfbs#e349e7

This notebook aims to create a benchmark dataset and standardize the following:
* File duration
* Sampling frequency
* Mono channel
* Bit depth
* File name format
* Selection table fields

It also gives the option to change labels, e.g., to match our standardized label format.


<b>It does NOT:</b>
* Filter the audio input beyond what is needed for resampling
* Normalize the audio file amplitude


For example, this schematic view presents (top) a Raven Pro project with a selection table associated with several audio files of different lengths, (bottom) the standardized benchmark clips, and associated annotations. Note that annotations at the junction between two export files and those in the remaining audio, which are too short in comparison with the selected export audio file duration, are ignored.
![‎method_schematicV2](https://github.com/leabouffaut/BenchmarkDatasetCreator/assets/18257956/2f267ee4-54ed-43ce-ab63-fe7932811104)

### Necessary information in selection tables
This project uses Raven Pro 1.6 selection tables. Selection tables can either be associated with (1) a single audio file or (2) multiple audio files.
Selection tables, by default, contain the necessary information to draw a time-frequency box around a call, please make sure to have the required following fields, including an annotation column and variables that enable the code to retrieve the audio files:
* 'Begin Time (s)'
* 'End Time (s)'
* 'Low Frequency (Hz)'
* 'High Frequency (Hz)'
* 'Begin Path'
* 'File Offset (s)'
* 'Label'/'Tags'/Other

We will consider and test that all selection tables should contain all of the aforementioned fields, with a user-defined field for the label column. Note that 'Begin Path' should work from your current workstation (Unix and Windows mount servers and write paths differently)!

### Labels 
The following format is our suggested label format: 

`<LatinNameAccronym>.<Location>.<CallName>`

Where 
* `<LatinNameAccronym>` is a 6-letter combination of the first letters of each word,
* `<Location>` a 4-letter combination describing the geographical location of the recorder.
    - If underwater, give cardinal direction and abbreviation of the ocean/sea,
    - If on land, the first two letters specify the region, and the last two letters are the ISO 3166 country codes (see https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2#ZZ),

* `<CallName>` free-format vocalization descriptor.


### Outputs
Please refer to the [User-defined parameters](#User-defined-parameters) section to see the details on the output folder architecture. 
> [!NOTE]
>This notebook will assist you in creating:
> * Benchmark sound files based on user-input specifications
> * a corresponding Raven selection table for each sound file,
> * a two-column file-matching CSV (as used for Koogu) and,
> * a recap annotation CSV file that will match previous datasets, e.g., https://zenodo.org/records/7525805

## User-defined parameters <a id='User-defined-parameters'></a>
```ruby
export_settings = {
    'Original project name': '2021_CLOCCB_BermudaPlantBank_S1105', 
    'Audio duration (s)': 300,  
    'fs (Hz)': 8000, 
    'Bit depth': 24,
    'Export label': 'Tags',
    'Split export selections': [True, 1],
    'Export folder': 'benchmark_data'
    }
```

The field illustrated above is a series of user-defined parameters in the form of a [Python dictionary](https://realpython.com/python-dicts/#defining-a-dictionary) (surrounded by curly braces, entries separated by commas, typical entry: `'key word': 'value'`) to create the Benchmark dataset, note that the following fields can be filled in any specific order but must all be present:
* `Original project name`, helps you keep track of the origin of the data, should be written between as a string of characters, which in Python is between quotes `'Project'`. This code will create the folder architecture, please do not end this entry by "/" or "\" and avoid spaces " ".
* `Audio duration (s)` is the chosen export audio file duration for the Benchmark dataset in seconds. Our recommendation is to set it to encompass the vocalization(s) of interest but also some context. What is the minimum duration that would represent the signal's repetition or call/cue rate (with several annotations)?
* `fs (Hz)` is the sampling frequency in Hz, to be set at minima at double the maximum frequency of the signals of interest. If relevant, BirdNET uses fs = 48 kHz (see: [BirdNET Analyzer technical details](https://github.com/kahst/BirdNET-Analyzer?tab=readme-ov-file#technical-details))
* `Bit depth` determines the number of possible amplitude values we can record for each audio sample; for SWIFT units, it is set to 16 bits and for Rockhopper to 24 bits.
* `Export label` defines the name of the label column for the created export Raven selection tables
* `Split export selections` specifies the method when a selection is at the junction between two export audio files if it should be split (True) or not (False). In the case the split is selected, a second value should be entered to specify the minimum duration to report an annotation in the selection table in seconds, e.g., `[True, 3]` or `[False, ]`. If you have hundreds or even tens of selections of your target signals, we would recommend to set this parameter to false. This parameter can be handy if, for example, you selected "long" periods of background noise (long compared to the annotations of signals of interest) that could be split across two audio export files. In that case, you can set the minimun duration to something longer than your signals of interest or to 3 s if you plan to work with BirdNET. Another use case is if you have a very tight selection around your signal of interest (in time) and want even a very small portion of that signal to be labeled.
* `Export folder` is where the data will be saved following this structure (example where `<Project>` is 2013_UnivMD_Maryland_71485_MD0)
```
Export_folder/
│   README.md
│   file001.txt    
│
└───2013_UnivMD_Maryland_71485_MD02/
    │   2013_UnivMD_Maryland_71485_MD02_annotations.csv
    │   2013_UnivMD_Maryland_71485_MD02_audio_seltab_map.csv
    │
    └───audio/
    │   │   <Project>_<OriginalFileName>_<OriginalSamplingFrequency>_<OriginalChannel>_<FileTimeStamp>.flac
    │   │   2013_UnivMD_Maryland_71485_MD02_71485MD02_002K_M11_multi_20150626_031500Z_2kHz_ch03_0600s.flac
    │   │   ...
    │   
    └───annotations/
        │   <Project>_<OriginalFileName>_<OriginalSamplingFrequency>_<OriginalChannel>_<FileTimeStamp>.txt
        │   2013_UnivMD_Maryland_71485_MD02_71485MD02_002K_M11_multi_20150626_031500Z_2kHz_ch03_0600s.txt
        │   ...
```

