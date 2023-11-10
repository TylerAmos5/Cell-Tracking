import tracking_utils
import read_nd2
import numpy as np
import matplotlib.pyplot as plt
import cv2
import os
import math
import read_nd2
from cell import Cell
import pandas as pd

import argparse


def get_args():
    """Collect filename for movie"

    Returns
    -------
    args: argument input by the user for --file_path
    """
    parser = argparse.ArgumentParser(description='obtain ND2 file name ',
                                     prog='get_args')
    parser.add_argument('--file_path',
                        type=str,
                        help='.nd2 File',
                        required=True)

    args = parser.parse_args()
    return args


def main():
    args = get_args()
    nd2 = args.file_path

    movie = read_nd2.read_nd2(nd2)
    site0 = read_nd2.get_site_data(movie, 0)

    frame0_nuc_channel = read_nd2.get_channel_rawData(movie, 0, 0, 0)
    rgb_nuc = np.dstack((frame0_nuc_channel,
                         frame0_nuc_channel, frame0_nuc_channel))
    rgb_nuc = cv2.normalize(rgb_nuc, None, 0, 255,
                            cv2.NORM_MINMAX, dtype=cv2.CV_8U)

    master_cells = tracking_utils.do_watershed(rgb_nuc)

    # loop over remaining frames and do track linking
    numcells = []
    for i in range(1, len(site0)):
        cur_frame_nuc = read_nd2.get_channel_rawData(movie, 0,
                                                     i, 0)
        curr_rbg = np.dstack((cur_frame_nuc, cur_frame_nuc,
                              cur_frame_nuc))
        curr_rbg = cv2.normalize(curr_rbg, None, 0, 255,
                                 cv2.NORM_MINMAX, dtype=cv2.CV_8U)
        master_cells = tracking_utils.link_next_frame(master_cells,
                                                      curr_rbg, i)
        master_cells = tracking_utils.correct_links(master_cells, 30) # current distance threshold
        numcells.append(len(master_cells))

    dtype = [('cell', 'U10'), ('x', int), ('y', int), ('t', int)]

    # Create an empty array with the specified dtype
    tracks = np.empty((len(master_cells) * len(site0) + 1,), dtype=dtype)

    # Populate the 'tracks' array
    tracks['cell'][1:] = [str(i)
                          for i in range(len(master_cells))
                          for _ in range(len(site0))]

    tracks['x'][1:] = [int(master_cells[i].coords[j][0])
                       for i in range(len(master_cells))
                       for j in range(len(site0))]

    tracks['y'][1:] = [int(master_cells[i].coords[j][1])
                       for i in range(len(master_cells))
                       for j in range(len(site0))]

    tracks['t'][1:] = [j
                       for _ in range(len(master_cells))
                       for j in range(len(site0))]

    # Convert the structured numpy array to a Pandas DataFrame
    df = pd.DataFrame(tracks[1:])

    # Save the DataFrame to a CSV file
    df.to_csv("tracks.csv", index=False)


if __name__ == '__main__':
    main()
