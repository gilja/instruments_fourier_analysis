# **PyToneAnalyzer**

![Build Status](https://img.shields.io/badge/Author-Duje_Giljanović-green) ![Build Status](https://img.shields.io/badge/Version-0.1.0-green) ![Build Status](https://img.shields.io/badge/Licence-MIT-green)
\
![Build Status](https://img.shields.io/badge/OS-MacOS,_Linux_Windows-blue) ![Build Status](https://img.shields.io/badge/IDEs-VSCode,_JupyterLab-blue) 
\
\
\
PyToneAnalyzer is a Python package used to analyze the harmonic spectra of musical instruments.

It started as a simple script for the purpose of preparing a public lecture on different acoustic characteristics between various musical instruments. Using the script, I was able to explain why different instruments sound differently even when playing the same note, and why some notes, when played simultaneously, form consonant (i.e. nicely-sounding) chords, while others form dissonant (i.e. not-so-nicely-sounding) chords. Finally, I was able to tap into a vast field of psychoacoustics and touch on the topic of audio compression.

At the moment, the package is based on exploiting Fourier's theorem to decompose the periodic waveform into harmonic series. In the future, however, I am hoping to update its functionality by exploiting Machine Learning for more advanced analysis (attack, decay, sustain and release, ADSR).  
&nbsp;


## Features

- Working with an arbitrary number of audio files
- Setting the number of harmonics used in signal reconstruction 
- Simple GUI for playing audio, plotting graphs and saving results
- Showing harmonic power spectra
- Representing the signal as mathematical function f(t) 
- Plotting and saving functions of individual harmonics
- Showing signal reconstruction timeline by adding harmonics one by one
- Exporting sounds of individual harmonics as WAV files where loudness is proportional to the relative power of the harmonic

&nbsp;


## Installation

> Note! 
>
>PyToneAnalyzer requires Python 3.9 or newer to run.

It is advised to create a virtual environment to prevent possible clashes between the dependencies. This can be done, for example, using conda by running

```sh
conda create --name <env_name> python=3.9
conda activate <env_name>
```

The package can be installed simply using pip:

```sh
pip install PyToneAnalyzer
```

&nbsp;


## Usage

**Note: Since the package depends on ipywidgets, running the code in notebook cells is mandatory. Running the code in a standard Python file will result in figures and audio not being displayed!
The code has been tested to run with VSCode with Notebook API and JupyterLab. Jupyter Notebook seems to have some issues with ipywidgets, making it difficult to set up properly.**

The package comes with a default dataset and configuration file making, it plug-and-play for new users.

In the ```examples``` directory you can find the notebook which should help you get familiar with the tool. Below you can find some important details.

The first step is importing the necessary modules: 

```python
import os
import PyToneAnalyzer.config as cfg
import PyToneAnalyzer.io_utils as iou
import PyToneAnalyzer.waveform_plot_utils as wpu
import PyToneAnalyzer.fourier_math_utils as fmu
import PyToneAnalyzer.general_display_utils as gdu
```

Next, you must set up project directory structure:

```python
iou.create_directory_structure()
```

Now you are ready to import data!

> If you are running the tool for the first time, you are not likely to have your custom configuration file. Hence, the tool will use the default configuration and data files that are installed together with the source code. 

```python
files = [os.path.join(cfg.PATH_INSTRUMENT_SAMPLES, name) for name in os.listdir(cfg.PATH_INSTRUMENT_SAMPLES)]
files.sort(key=lambda x: x.lower()) # making sure the order is the same as in period_bounds.py config file
sounds = []

for file in files:
    path = os.path.join(cfg.PATH_INSTRUMENT_SAMPLES, file)
    sound, rate = iou.load_sound(path)
    sounds.append((sound, rate))
```

Keep in mind that imported audio files are converted to lowercase and sorted alphabetically. This order is crucial as you will see soon!

&nbsp;

## Custom configuration file

Once you are ready to analyze your own audio files, you will need to create your own configuration file. To make this easier for you, the template has been provided to you in the ```examples``` directory.

The first thing that you will want to address after downloading the template file is the section with __PATH__ variables

```
# Path constants
PATH_BASE = "absolute/path/to/the/project"
PATH_DATA = os.path.join(PATH_BASE, "data")
PATH_RESULTS = os.path.join(PATH_BASE, "results", "analysed")
PATH_INSTRUMENT_SAMPLES = os.path.join(PATH_DATA, "instrument_samples")
```

The __only__ thing to edit here is the __PATH_BASE__ which should point to the project directory. Once this has been set up, other paths are configured automatically. If you set the PATH_BASE variable to point to ~/Desktop, the tool will create directories ~/Desktop/data/instrument_samples and ~/Desktop/results in which it will search input audio files and store results, respectively.

>**Important**: Use absolute path for the PATH_BASE variable!

The next important configuration variables are WAVEFORM_ZOOM_PERCENTAGES, N_HARMONICS_PER_INSTRUMENT and PERIOD_BOUNDS.

```
# Set waveform zoom percentage for each instrument
WAVEFORM_ZOOM_PERCENTAGES = [
    0.008,  # cello
    0.0015,  # clarinet
    0.01,  # double bass
]

# Set the number of harmonics to be used in the Fourier analysis for each instrument
N_HARMONICS_PER_INSTRUMENT = [
    50,  # cello
    10,  # clarinet
    45,  # double bass
]

# one-period bounds for each instrument
PERIOD_BOUNDS = {
    "cello": [0.8284, 0.83604],
    "clarinet": [2.09145, 2.09334],
    "double_bass": [0.63845, 0.64609],
}
```


> **Important**: The number of elements in these three containers must **exactly match** the number of audio files in your data/instrument_samples directory! If this is not the case, the package will not work!

The WAVEFORM_ZOOM_PERCENTAGES variable indicates what portion of the waveform will be shown on the right-hand-side subplot when the following line is run 

```
wpu.plot_waveform(sounds, files)
```

You should play around with these percentages until you get the result that you are happy with.

![Alt text](https://github.com/gilja/instruments_fourier_analysis/blob/main/examples/waveform_cello_c3.png?raw=true "Waveform")


The WAVEFORM_ZOOM_PERCENTAGES variable indicates how many harmonics will be used, for each audio file, to reconstruct the original signal. The higher this number is, the better the reconstruction will be. While some instruments have a relatively simple harmonic footprint, others do not.

The PERIOD_BOUNDS variable is used to specify the starting and ending points of an arbitrary period. One full period can be easily determined by looking at the zoomed-in waveform and finding the two adjacent x-axis values at which the waveform starts to repeat. This can be easily done when running the application since one can zoom in even more on any part of the plot and determine the precise coordinate of any point on the graph with mouse hover. 
An example is shown below for clarinet playing C5.

![Alt text](https://github.com/gilja/instruments_fourier_analysis/blob/main/examples/waveform_clarinet_c5.png?raw=true "One period")

&nbsp;

### Setting up configuration in code

Once the configuration file has been prepared, it is time to set it up in the code. 

The first step is the same: 

```python
import os
import PyToneAnalyzer.config as cfg
import PyToneAnalyzer.io_utils as iou
import PyToneAnalyzer.waveform_plot_utils as wpu
import PyToneAnalyzer.fourier_math_utils as fmu
import PyToneAnalyzer.general_display_utils as gdu
```

However, now the following must be done!

```python
import PyToneAnalyzer

# Initialize with the custom configuration
PyToneAnalyzer.initialize_config("full_path_to_config_file/config.py")

# Get the ConfigManager instance and its configuration
cfg_manager = PyToneAnalyzer.ConfigManager.get_instance()
cfg = cfg_manager.config
```

This will allow you to get variables from the custom configuration file: 

```python
cfg.PATH_INSTRUMENT_SAMPLES
cfg.PERIOD_BOUNDS
...
```

The final step before adding your data is setting up the directory structure:

```python
iou.create_directory_structure()
```

This will create ```results/analyzed``` and ```data/instrument_samples``` directories.

&nbsp;

## Adding custom audio samples

Once the directory structure has been created, you are ready to introduce your audio samples. 
It is recommended that the naming convention is followed [instrument_name]-[note]_[16_bit.wav]. Some examples are shown below:

- sax-alto-c5_16_bit.wav
- oboe-c4_16_bit.wav
- cello-c3_16_bit.wav

>**Important**: It is absolutely crucial that audio files are in WAV format with a .wav extension.

>**MacOS users**: Make sure that there is no .DS_Store in the ```data/instrument_samples``` directory. Any non-WAV file in this directory will trigger the exception that will prevent the execution of the code. 

&nbsp;

# Citing PyToneAnalyzer

If you are using PyToneAnalyzer in your research, please acknowledge it by citing. For details on how to cite, please refer to the following [link](https://github.com/gilja/instruments_fourier_analysis/blob/main/CITATION.txt).

&nbsp;

## License

MIT

