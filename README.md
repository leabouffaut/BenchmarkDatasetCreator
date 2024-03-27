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

<div class="alert alert-block alert-info">
<b>This notebook will assit you in creating:</b> 
<ul>
  <li>Benchmark soundfiles based on user-input specifications</li>
  <li>a corresponding Raven selection table for each sound file, </li>
  <li>a two-colum file-matching csv (as used for Koogu) and,</li>
  <li>a recap annotation CSV file that will match previous datasets e.g, https://zenodo.org/records/7525805</li>
</ul>
</div>

