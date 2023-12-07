import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D


def create_tracks_dataframe(master_cells, site, channel2, channel3):
        """
        Creates a dataframe that stores the cells'
        coordinates and fluorescent values for each channel

        Args:
            master_cells: list of cells
            site: site number
            channel2: name of channel 2
            channel3: name of channel 3
        """
        dtype = [('cell', 'U10'), ('x', int), ('y', int), ('t', int),
                 (channel2, float), (channel3, float)]

        # Create an empty array with the specified dtype
        tracks = np.empty((len(master_cells) * len(site) + 1,), dtype=dtype)

        # Populate the 'tracks' array
        tracks['cell'][1:] = [str(i)
                              for i in range(len(master_cells))
                              for _ in range(len(site))]

        tracks['x'][1:] = [int(master_cells[i].coords[j][0])
                           for i in range(len(master_cells))
                           for j in range(len(site))]

        tracks['y'][1:] = [int(master_cells[i].coords[j][1])
                           for i in range(len(master_cells))
                           for j in range(len(site))]

        tracks['t'][1:] = [j
                           for _ in range(len(master_cells))
                           for j in range(len(site))]

        tracks[channel2][1:] = [master_cells[i].channel2_data[j]
                                        for i in range(len(master_cells))
                                        for j in range(len(site))]

        tracks[channel3][1:] = [master_cells[i].channel3_data[j]
                                      for i in range(len(master_cells))
                                      for j in range(len(site))]

        # Convert the structured numpy array to a Pandas DataFrame
        df = pd.DataFrame(tracks[1:])
        return df

def plot_nuc_fluoro(tracks_df, channel_name, time_step, output_path, drug_time=None):
         """
         plot the average nuclear fluorescent value for the
         specified channel within the nucleus contour

         Args:
            tracks_df: dataframe with tracks and fluorescent data
            channel_name: name of the channel to plot
            time_step: time step between frames (in minutes)
            output_path: path to save the plots
            drug_time: time (in hours) when drug was added

         Returns:
            None
         """
         cell_IDs = tracks_df.groupby('cell')
         os.makedirs(output_path, exist_ok=True)

         # Iterate over each group
         for cell_ID, group in cell_IDs:
            # convert frames to hours
            if time_step == 1:
                group['t_in_hours'] = group['t']
            else:
                group['t_in_hours'] = group['t'] * int(time_step) / 60
            # Plot the 't' column on the x-axis and
            # 'channel3_avg' on the y-axis for each cell ID
            plt.figure()
            group.plot(x='t_in_hours', y=channel_name,
                    kind='line', color='green', label=channel_name)
            plt.title(f'Cell ID: {cell_ID}')
            plt.xlabel('Time (hours)')
            plt.ylabel('1 / mVenus median (pixel intensity)')
            if drug_time is not None:
                 plt.axvline(x=drug_time, color='gray', linestyle='--', label='drug added')
            plt.savefig(f'{output_path}/Cell_{cell_ID}.png')
            plt.close('all')


def plot_cyto_nuc_ratio(tracks_df, channel_name, time_step,
                            output_path, drug_time=None, mark_cell_divisions=True):
        """
         plot the average nuclear fluorescent value for the
         specified channel within the nucleus contour

         Args:
            tracks_df: dataframe with tracks and fluorescent data
            channel_name: name of the channel to plot
            time_step: time step between frames (in minutes)
            output_path: path to save the plots
            drug_time: time (in hours) when drug was added
            mark_cell_divisions: whether to mark cell divisions

         Returns:
            None
         """
        os.makedirs(output_path, exist_ok=True)
        cell_IDs = tracks_df.groupby('cell')
        for cell_ID, group in cell_IDs:
            # convert frames to hours
            if time_step == 1:
                group['t_in_hours'] = group['t']
            else:
                group['t_in_hours'] = group['t'] * int(time_step) / 60
            # Plot the 't' column on the x-axis and
            # 'channel2_ratio' on the y-axis for each cell ID
            plt.figure()
            group.plot(x='t_in_hours', y=channel_name,
                    kind='line', color='red')
            plt.title(f'Cell ID: {cell_ID}')
            plt.xlabel('Time (hours)')
            plt.ylabel('CDK2 nuclear to cytoplasm signal ratio')
            if drug_time is not None: 
                plt.axvline(x=drug_time, color='gray', linestyle='--', label='drug added')
                
            plt.ylim(0, 1.5)

            prev_row = group.iloc[0]
            scatter_x = []
            scatter_y = []
            for index, row in group.iterrows():
                # Check if the value was above 0.5 previously
                # and now crosses below 0.5
                if prev_row[channel_name] > 1 and row[channel_name] < 1:
                    # Find the approximate x position
                    # (time in hours) of the crossing
                    x_crossing = (prev_row['t_in_hours'] + row['t_in_hours']) / 2
                    scatter_x.append(x_crossing)
                    scatter_y.append(1)
                prev_row = row

            # Plot scatter for cell division
            if mark_cell_divisions:
                if scatter_x:  # Check if the list is not empty
                    plt.scatter(scatter_x, scatter_y, color='blue',
                                s=50, label='Cell division')

                # Create a legend
                legend_elements = [Line2D([0], [0], color='red', lw=2,
                                        label='CDK2 ratio'),
                                Line2D([0], [0], marker='o', color='w',
                                        markerfacecolor='blue', markersize=10,
                                        label='Cell division')]
                plt.legend(handles=legend_elements)

            plt.savefig(f'{output_path}/Cell_{cell_ID}.png')
            plt.close('all')
