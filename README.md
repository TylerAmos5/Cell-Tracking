# Cell-Tracking

## Description

This software is designed to track individual live cells and record protein dynamics using fluorescent time-lapse microscopy data acquired by a Nikon microscope. This code was developed to work for ND2 files with three channels and two sites per well. Our goal is to further generalize this to accept any number of color channels and sites. Additionally, we intend to visualize single cell traces and compare fluorescence values between cells. The current code tracks single cells throughout a movie. The current output is “tracks.csv”, containing cell IDs and corresponding locations in each frame throughout the input movie. Image segmentation via watershedding is conducted on the first frame to identify nuclei to create a list of master cell IDs. Then, each frame that follows is segmented to identify nuclei and is linked to the cells identified in the previous frame. We developed a “Cell” class that stores a cell’s location in each frame, the outline of its nucleus, identities of parent and children, and the “birthday” if the cell was not present in the first frame. This helps analyze the data with single cell resolution.

## Installation

### Clone the repository

```
git clone https://github.com/TylerAmos5/Cell-Tracking.git
```

### Setting up an environment

This program relies on a series of packages which are detailed in the environment.yml file. Please install each of these dependencies before proceeding.

## Usage

Basic do_tracking.py usage:

```
python src/do_tracking.py [-h] --file_path FILE_PATH
```

### Files of note

The following files are all within the src directory.

#### src/do_tracking.py

Main script that calls functions from many of the other files.

#### src/read_nd2.py

Contains functions required for initial ND2 handling, import, and tiff conversion.

#### src/tracking_utils.py

Contains functions required for cell tracking.

#### src/cell.py

Defines the cell object class.

#### test/unit/test_cell_tracking.py

Contains unit tests for some of the functions in tracking_utils.py. Additional tests are still under development.

### Examples

#### Running do_tracking.py directly with your own ND2 file:

```
python src/do_tracking.py --file_path='/Users/tyleramos/Cell-Tracking/doc/WellD01_ChannelmIFP,mCherry,YFP_Seq0000.nd2'
# Please note that this file path will need to be replaced with the location of an ND2 file on your machine.
# This repository does not currently contain any ND2 files due to the large file size.
```

#### Running using snakemake:

Run the following code from the main repository directory. The file path included in the snakefile will need to be updated with the appropriate file path for your ND2 file.

```
snakemake -c1
```

#### Running unit tests:

Eventually these tests will run using continuous integration, but in the meantime they can be run using the following code.

```
python test/unit/test_cell_tracking.py
```

## Updates

10/1/23: developed initial code for object detection and tracking

10/15/23: added first pass at conflict resolution and object-oriented code

10/18/23: code updated to read nd2s and save the data in a nested dictionary

10/24/23: unit tests added (more still under development)

10/25/23: fixed issue with frames not iterating when nd2 read in, worked on debugging tracking workflow

10/27/23: ipynb files converted to python scripts

10/30/23: snakemake workflow added