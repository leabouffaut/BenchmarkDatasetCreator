# Benchmark Dataset Creator
Léa Bouffaut, Ph.D. -- K. Lisa Yang Center for Conservation Bioacoustics, Cornell University

lea.bouffaut@cornell.edu

Motivations and objectives

Many bioacoustic projects are sitting on a goldmine of already annotated datasets. We want to create a standardized pipeline for creating, storing, sharing and using data that is flexible and repeatable to train and test AI models for different applications. More details at https://www.overleaf.com/read/yfcgvngmwfbs#e349e7

This notebook aims to create a benchmark dataset and standardize the following:

File duration
Sampling frequency
Mono channel
Bit depth
File name format
Selection table fields
It does NOT:

Filter the audio input beyond what is needed for resampling
Normalize the audio file amplitude
For example, this schematic view presents (top) a raven project with a selection table associated with several audio files of different lengths (bottom), the standardized benchmark clips, and associated annotations. Note that annotations at the junction between two export files and those in the remaining audio, which are too short compared to the selected export audio file duration, are ignored.

<img width="1225" alt="image" src="https://github.com/leabouffaut/BenchmarkDatasetCreator/assets/18257956/b1cfef2f-0d0f-48b8-ae43-4d4324a21e41">


### Necessary information in selection tables
This project uses Raven Pro 1.6 selection tables. 
Selection tables, by default, contain the necessary information to draw a time-frequency box around a call and an annotation column
* 'Begin Time (s)'
* 'End Time (s)'
* 'Low Frequency (Hz)'
* 'High Frequency (Hz)'
* 'Label'/'Tags'/Other

Selection tables can either be associated with (1) a single audio file or (2) multiple audio files. In the latter, the following additional fields must be present
* 'Begin Path'
* 'File Offset (s)'

We will consider that all selection tables contain all of the aforementioned fields, with a user-defined field for the label column.
