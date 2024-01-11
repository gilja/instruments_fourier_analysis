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


## Features

- Working with an arbitrary number of audio files
- Setting the number of harmonics used in signal reconstruction 
- Simple GUI for playing audio, plotting graphs and saving results
- Showing harmonic power spectra
- Representing the signal as mathematical function f(t) 
- Plotting and saving functions of individual harmonics
- Showing signal reconstruction timeline by adding harmonics one by one
- Exporting sounds of individual harmonics as WAV files where loudness is proportional to the relative power of the harmonic

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

## Usage

**Note: Since the package is depending on ipywidgets, it is mandatory to run it as a notebook file. Running it as a standard Python file will result in figures and audio not being displayed!
The code has been tested to run with VSCode with Notebook API and JupyterLab. Jupyter Notebook seems to have some issues with ipywidgets which makes it difficult to set up properly.**

The package comes with default dataset and configuration file which makes it plug-and-play for new users.

In the ```examples``` directory you can find the notebook which should help you get familiar with the tool. Bellow you can find some important details.

The first step is importing necessary modules: 

```python
import os
import PyToneAnalyzer.config as cfg
import PyToneAnalyzer.io_utils as iou
import PyToneAnalyzer.waveform_plot_utils as wpu
import PyToneAnalyzer.fourier_math_utils as fmu
import PyToneAnalyzer.general_display_utils as gdu
```

Now you are ready to import data!

> If you are running the tool for the first time, you are not likely to have your custom configuration file. Hence, the tool will use default configuration and data files that are installed together with the source code. 

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


## Custom config file

Once you are ready to do the analysis on your own audio files, you will need to create your own configuration file. To make this easier to you, the template has been provided to you in the ```examples``` directory.

The first thing that you will want to address after downloading the template file is the section with __PATH__ variables

```
# Path constants
PATH_BASE = "absolute/path/to/the/project"
PATH_DATA = os.path.join(PATH_BASE, "data")
PATH_RESULTS = os.path.join(PATH_BASE, "results", "analysed")
PATH_INSTRUMENT_SAMPLES = os.path.join(PATH_DATA, "instrument_samples")
```

The __only__ thing to edit here is the __PATH_BASE__ which should point to the project directory. Once this has been set up, other paths are configured automatically. If you set the PATH_BASE variable to point to ~/Desktop, the tool will create directories ~/Desktop/data and ~/Desktop/results in which it will search input audio files and store results, respectively.

>**Important**: Use absolute path for the PATH_BASE variable

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

The WAVEFORM_ZOOM_PERCENTAGES indicates what portion of the waveform will be shown on the right-hand-side subplot when the following line is run 

```
wpu.plot_waveform(sounds, files)
```

as you can see on the next image. You should play around with these percentages until you get the result that you are happy with.









## Plugins

Dillinger is currently extended with the following plugins.
Instructions on how to use them in your own application are linked below.

| Plugin | README |
| ------ | ------ |
| Dropbox | [plugins/dropbox/README.md][PlDb] |
| GitHub | [plugins/github/README.md][PlGh] |
| Google Drive | [plugins/googledrive/README.md][PlGd] |
| OneDrive | [plugins/onedrive/README.md][PlOd] |
| Medium | [plugins/medium/README.md][PlMe] |
| Google Analytics | [plugins/googleanalytics/README.md][PlGa] |

## Development

Want to contribute? Great!

Dillinger uses Gulp + Webpack for fast developing.
Make a change in your file and instantaneously see your updates!

Open your favorite Terminal and run these commands.

First Tab:

```sh
node app
```

Second Tab:

```sh
gulp watch
```

(optional) Third:

```sh
karma test
```

#### Building for source

For production release:

```sh
gulp build --prod
```

Generating pre-built zip archives for distribution:

```sh
gulp build dist --prod
```

## Docker

Dillinger is very easy to install and deploy in a Docker container.

By default, the Docker will expose port 8080, so change this within the
Dockerfile if necessary. When ready, simply use the Dockerfile to
build the image.

```sh
cd dillinger
docker build -t <youruser>/dillinger:${package.json.version} .
```

This will create the dillinger image and pull in the necessary dependencies.
Be sure to swap out `${package.json.version}` with the actual
version of Dillinger.

Once done, run the Docker image and map the port to whatever you wish on
your host. In this example, we simply map port 8000 of the host to
port 8080 of the Docker (or whatever port was exposed in the Dockerfile):

```sh
docker run -d -p 8000:8080 --restart=always --cap-add=SYS_ADMIN --name=dillinger <youruser>/dillinger:${package.json.version}
```

> Note: `--capt-add=SYS-ADMIN` is required for PDF rendering.

Verify the deployment by navigating to your server address in
your preferred browser.

```sh
127.0.0.1:8000
```

## License

MIT

**Free Software, Hell Yeah!**

[//]: # (These are reference links used in the body of this note and get stripped out when the markdown processor does its job. There is no need to format nicely because it shouldn't be seen. Thanks SO - http://stackoverflow.com/questions/4823468/store-comments-in-markdown-syntax)

   [dill]: <https://github.com/joemccann/dillinger>
   [git-repo-url]: <https://github.com/joemccann/dillinger.git>
   [john gruber]: <http://daringfireball.net>
   [df1]: <http://daringfireball.net/projects/markdown/>
   [markdown-it]: <https://github.com/markdown-it/markdown-it>
   [Ace Editor]: <http://ace.ajax.org>
   [node.js]: <http://nodejs.org>
   [Twitter Bootstrap]: <http://twitter.github.com/bootstrap/>
   [jQuery]: <http://jquery.com>
   [@tjholowaychuk]: <http://twitter.com/tjholowaychuk>
   [express]: <http://expressjs.com>
   [AngularJS]: <http://angularjs.org>
   [Gulp]: <http://gulpjs.com>

   [PlDb]: <https://github.com/joemccann/dillinger/tree/master/plugins/dropbox/README.md>
   [PlGh]: <https://github.com/joemccann/dillinger/tree/master/plugins/github/README.md>
   [PlGd]: <https://github.com/joemccann/dillinger/tree/master/plugins/googledrive/README.md>
   [PlOd]: <https://github.com/joemccann/dillinger/tree/master/plugins/onedrive/README.md>
   [PlMe]: <https://github.com/joemccann/dillinger/tree/master/plugins/medium/README.md>
   [PlGa]: <https://github.com/RahulHP/dillinger/blob/master/plugins/googleanalytics/README.md>
