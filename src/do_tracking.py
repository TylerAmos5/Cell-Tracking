import tracking_utils
import read_nd2
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import cv2
import os
import math
from cell import Cell
import pandas as pd
import argparse
import time


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
        master_cells = tracking_utils.correct_links(master_cells,  distance_threshold=30)
        
        if i == (len(site0)-1):
            # cull remaining problematic cells from last frame
            remaining_problematics = tracking_utils.get_all_problematics(master_cells)
            master_cells = tracking_utils.cull_duplicates(master_cells, remaining_problematics)

        numcells.append(len(master_cells))

    remaining_death_row = tracking_utils.get_all_death_row(master_cells)
    print(remaining_death_row)

    dtype = [('cell', 'U10'), ('x', int), ('y', int), ('t', int),
             ('channel2_ratio', float), ('channel3_avg', float)]

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
    
    tracks['channel2_ratio'][1:] = [master_cells[i].channel2_ratio[j]
                                    for i in range(len(master_cells))
                                    for j in range(len(site0))]

    tracks['channel3_avg'][1:] = [master_cells[i].channel3_avg[j]
                                  for i in range(len(master_cells))
                                  for j in range(len(site0))]

    # Convert the structured numpy array to a Pandas DataFrame
    df = pd.DataFrame(tracks[1:])

    # plot individual channel data for each cell
    cell_IDs = df.groupby('cell')
    plots_dir = "mTOR_plots"
    os.makedirs(args.output_path + "/" + plots_dir, exist_ok=True)

    # Iterate over each group
    for cell_ID, group in cell_IDs:
        # convert frames to hours
        group['t_in_hours'] = group['t'] * 15 / 60
        # Plot the 't' column on the x-axis and 'channel3_avg' on the y-axis for each cell ID
        plt.figure()
        group.plot(x='t_in_hours', y='channel3_avg', kind='line', color='green', label='mTOR activity')
        plt.title(f'Cell ID: {cell_ID}')
        plt.xlabel('Time (hours)')
        plt.ylabel('1 / mVenus median (pixel intensity)')
        plt.axvline(x=18.75, color='gray', linestyle='--', label='mTORi added')
        plt.savefig(f'{args.output_path}/{plots_dir}/Cell_{cell_ID}.png')
        plt.close('all')  

    plots_dir = "CDK2ratio_plots"
    os.makedirs(args.output_path + "/" + plots_dir, exist_ok=True)
    
    


    for cell_ID, group in cell_IDs:
        # convert frames to hours 
        group['t_in_hours'] = group['t'] * 15 / 60
        # Plot the 't' column on the x-axis and 'channel2_ratio' on the y-axis for each cell ID
        plt.figure()
        group.plot(x='t_in_hours', y='channel2_ratio', kind='line', color='red')
        plt.title(f'Cell ID: {cell_ID}')
        plt.xlabel('Time (hours)')
        plt.ylabel('CDK2 nuclear to cytoplasm signal ratio')
        plt.ylim(0, 1.5)
        
        prev_row = group.iloc[0]
        scatter_x = []
        scatter_y = []
        for index, row in group.iterrows():
            # Check if the value was above 0.5 previously and now crosses below 0.5
            if prev_row['channel2_ratio'] > 1 and row['channel2_ratio'] < 1:
                # Find the approximate x position (time in hours) of the crossing
                x_crossing = (prev_row['t_in_hours'] + row['t_in_hours']) / 2
                scatter_x.append(x_crossing)
                scatter_y.append(1)
            prev_row = row
        
        # Plot scatter for cell division
        if scatter_x:  # Check if the list is not empty
            plt.scatter(scatter_x, scatter_y, color='blue', s=50, label='Cell division')

        # Create a legend
        legend_elements = [Line2D([0], [0], color='red', lw=2, label='CDK2 ratio'),
                           Line2D([0], [0], marker='o', color='w', markerfacecolor='blue', markersize=10, label='Cell division')]
        plt.legend(handles=legend_elements)
            
        plt.savefig(f'{args.output_path}/{plots_dir}/Cell_{cell_ID}.png')
        plt.close('all')   
    
    # Save the DataFrame to a CSV file
    well_name = os.path.basename(nd2)
    outfile_name = args.output_path + '/' + well_name + "_tracks.csv"
    outfile_name = outfile_name.replace('.nd2', '')
    default_out = '../' + well_name + "_tracks.csv"
    
    try:
        df.to_csv(outfile_name, index=False)
    except PermissionError:
        print("Could not write to designated file, writing to repository root")
        df.to_csv(default_out, index=False)

    end_time = time.time()
    execution_time = end_time - start_time
    print(f"Execution time: {execution_time} seconds")


if __name__ == '__main__':
    main()
