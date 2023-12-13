import tracking_utils
import read_nd2
import numpy as np
import matplotlib.pyplot as plt

import cv2
import os
import math
from cell import Cell
import pandas as pd
import argparse
import time
import plots

def get_args():
    """Collect filename for movie"

    Returns
    -------
    args: argument input by the user for --file_path and --output_dir
    """
    parser = argparse.ArgumentParser(description='obtain ND2 file name ',
                                     prog='get_args')
    parser.add_argument('--file_path',
                        type=str,
                        help='.nd2 File',
                        required=True)

    parser.add_argument('--output_path',
                        type=str,
                        help='Directory to write output file to',
                        required=True)
    parser.add_argument('--time_step',
                        help='Time step between frames (in minutes)',
                        required=False)
    parser.add_argument('--make_channel3_plots',
                        help='Create plots for channel 3',
                        required=False)
    parser.add_argument('--make_channel2_plots',
                        help='Create plots for channel 2',
                        required=False)
    parser.add_argument('--drug_time',
                        help='Time at which drug was added (in hours)',
                        required=False)

    args = parser.parse_args()
    return args


def main():
    start_time = time.time()
    args = get_args()
    nd2 = args.file_path
    movie = read_nd2.read_nd2(nd2)
    site0 = read_nd2.get_site_data(movie, 0)
    frame0 = read_nd2.get_frame_data(movie, 0, 0)
    master_cells = tracking_utils.do_watershed(frame0)

    if args.time_step is None:
        args.time_step = 1

    if args.make_channel3_plots is None:
        args.make_channel3_plots = True
    
    if args.make_channel2_plots is None:
        args.make_channel2_plots = True

    # loop over remaining frames and do track linking
    numcells = []
    for i in range(1, len(site0)):
        cur_frame = read_nd2.get_frame_data(movie, 0, i)
        cur_frame_nuc = read_nd2.get_channel_rawData(movie, 0,
                                                     i, 0)
        curr_nuc_rbg = np.dstack((cur_frame_nuc, cur_frame_nuc,
                                  cur_frame_nuc))

        curr_nuc_rbg = cv2.normalize(curr_nuc_rbg, None, 0, 255,
                                     cv2.NORM_MINMAX, dtype=cv2.CV_8U)

        master_cells = tracking_utils.link_next_frame(master_cells,
                                                      cur_frame, i)
        master_cells = tracking_utils.correct_links(master_cells,
                                                    distance_threshold=30)

        if i == (len(site0)-1):
            # cull remaining problematic cells from last frame
            remaining_problematics = tracking_utils.get_all_problematics(
                                     master_cells)
            master_cells = tracking_utils.cull_duplicates(
                           master_cells, remaining_problematics)

        numcells.append(len(master_cells))

    remaining_death_row = tracking_utils.get_all_death_row(master_cells)
    os.makedirs(args.output_path, exist_ok=True)
    # create a dataframe with the tracks and fluorescent data
    tracks = plots.create_tracks_dataframe(master_cells, site0, 'channel2_data',
                                           'channel3_data')
    
    channel3_output = args.output_path + "/channel3_plots"
    if args.make_channel3_plots:
        plots.plot_nuc_fluoro(tracks, 'channel3_data', args.time_step,
                              channel3_output, drug_time=args.drug_time)
    
    
    channel2_output = args.output_path + "/channel2_plots"
    if args.make_channel2_plots:
        plots.plot_cyto_nuc_ratio(tracks, 'channel2_data',
                                  args.time_step, channel2_output)
    
    # Save the DataFrame to a CSV file
    well_name = os.path.basename(nd2)
    outfile_name = args.output_path + '/' + well_name + "_tracks.csv"
    outfile_name = outfile_name.replace('.nd2', '')

    tracks.to_csv(outfile_name, index=False)
    
    end_time = time.time()
    execution_time = end_time - start_time
    print(f"Execution time: {execution_time} seconds")


if __name__ == '__main__':
    main()
