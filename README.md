# Cell-Tracking

## Description

This software is designed to track individual live cells and record protein dynamics using fluorescent time-lapse microscopy data acquired by a Nikon microscope. This type of analysis is used to examine single cells’ protein dynamics as they progress through the cell cycle. This software is designed to handle three live-cell fluorescent markers representing a variety of cellular processes. For example, these could be markers for cell proliferation, activation of a specific pathway, or nuclear markers. The signal from each of these markers is represented in individual non-overlapping channels, allowing for each channel to be analyzed individually or multiplexed together to provide robust information about the cells active processes. For example, this analysis might be conducted to examine the protein dynamics of proliferating cancer cells. Anti-proliferation drugs could be added to cells and then compared to untreated cells, revealing differences in signaling pathway activation in the presence of drug. 

This code was developed to work for ND2 files with three channels and two sites per well. We intend to visualize single cell traces and compare fluorescence values between cells. The current code tracks single cells throughout a movie. The current output is “'filename'_tracks.csv”, containing cell IDs and corresponding locations in each frame throughout the input movie. Image segmentation via watershedding is conducted on the first frame to identify nuclei to create a list of master cell IDs. Then, each frame that follows is segmented to identify nuclei and is linked to the cells identified in the previous frame. We developed a “Cell” class that stores a cell’s location in each frame, the outline of its nucleus, identities of parent and children, and the “birthday” if the cell was not present in the first frame. This helps analyze the data with single cell resolution.

## Installation

### Clone the repository

```
git clone https://github.com/TylerAmos5/Cell-Tracking.git
```

### Setting up an environment

This program relies on a series of packages which are detailed in the environment.yml file. Create a new environment with the same dependencies by running the following code.
### If you do not already have mamba installed, run the following three lines
```
cd $HOME
curl -L -O https://github.com/conda-forge/miniforge/releases/latest/download/Mambaforge-pypy3-Linuxx86_64.sh
bash Mambaforge-pypy3-Linux-x86_64.sh.sh
```
Next, use mamba to create a new environment from the provided environment.yml file.
```
mamba env create -f environment.yml -n <your_environtment_name>
```
Then, you must allow mamba to activate and deactivate environments. To do this, run the following line:
```
mamba init
```
Now, you must restart your shell for the changes to take place. You can do this by quitting the terminal or closing your window. 
Once you have reopened your shell, activate the new environment. 
```
mamba activate <your_environment_name>
```

## Accessing the test data file using LFS
### Install git large file storage (lfs)
#### Windows
If you have a Windows machine, git lfs should already be installed as a part of "git for windows"

#### Mac
If you have a Mac, you must install git lfs. 
If you have homebrew installed, run the following:
```
brew install git-lfs
```
If you do not have homebrew, visit this site and download the installation helper. 
https://git-lfs.com/

#### Accessing the test file
To download the test file as an example run before trying on your own data, run the following:
```
git lfs install
git lfs pull
```

## Usage

Basic do_tracking.py usage:

```
python src/do_tracking.py [-h] --file_path FILE_PATH --output_path OUTPUT_PATH

```
Use --file_path to specify the file path for the input ND2 file.
Use --output_path to specify the directory where the output will be saved. The file names themselves will be generated automatically based upon the input file name.

### Specifying additional parameters
```
--time_step
```
Use this parameter to specify how many minutes are between frames. The program will convert time time to hours
If this parameter is not defined, the program will plot frames on the x-axis

```
--drug_time
```
Use this parameter to specify what time drug was added to the cells in your experiment.
A vertical dotted line will be added on the plot to indicate when the drug was added.

```
--make_channel2_plots
--make_channel3_plots
```
Set these to false if you do not want to produce fluorescence graphs for each cell.
The default is True. 


### Files of note

The following files are all within the src directory.

#### src/do_tracking.py

Main script that calls functions from many of the other files.

#### src/read_nd2.py

Contains functions required for initial ND2 handling, and creates the initial data structure with movie data

#### src/tracking_utils.py

Contains functions required for cell tracking.

#### src/cell.py

Defines the cell object class.

#### src/plots.py
Generates dataframe containing location and fluorescent values for each cell.
This will also generate fluorecence plots for each cell if --make_channel(2/3)_plots is set to true.


#### test/unit/test_cell_tracking.py

Contains unit tests for some of the functions in tracking_utils.py. Additional tests are still under development.

### Examples

#### Running do_tracking.py directly with your own ND2 file:

```
python src/do_tracking.py --file_path='<your_path>/Cell-Tracking/doc/<your_filename>' --output_path='<your_output_path>'
```
#### Replace <your_path> with the relevant path on your device
This repository does not currently contain any ND2 files due to the large file size.


#### Running using snakemake:

Run the following code from the main repository directory. The file path included in the snakefile will need to be updated with the appropriate file path for your ND2 file.

```
snakemake -c1
```

#### Running unit tests:
```
python test/unit/test_cell_tracking.py
```

#### Running functional tests:
```
bash test/func/test_do_tracking.sh
```

## Updates


10/1/23: developed initial code for object detection and tracking. 
developed nd2 file I/O. 

10/15/23: added first pass at conflict resolution and object-oriented code

10/18/23: code updated to read nd2s and save the data in a nested dictionary

10/24/23: unit tests added (more still under development)

10/25/23: fixed issue with frames not iterating when nd2 read in, worked on debugging tracking workflow

10/27/23: ipynb files converted to python scripts

10/30/23: snakemake workflow added

11/10/23: worked on culling functions and testing framework

11/14/23: track healing and culling improved

11/21/23: try/except implemented

11/23/23: environments solved