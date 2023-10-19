import nd2reader
import tifffile
import numpy as np

def read_nd2(nd2_filename):
    with nd2reader.ND2Reader(nd2_filename) as nd2_movie:
        nd2_movie.iter_axes = 'v'
        well_data = {}
        for fov in range(nd2_movie.sizes['v']):
            frame_data = {}
            nd2_movie.iter_axes = 't'
            for f in range(nd2_movie.sizes['t']):
                nd2_movie.iter_axes = 'c'
                channel_data = []
                
                for c in range(nd2_movie.sizes['c']):
                    channel_data.append(nd2_movie[c])
                
                channel_data = np.array(channel_data)
                channel_data = channel_data.transpose((1, 2, 0))
                frame_data[f] = channel_data
            well_data[fov] = frame_data
                
        
    return well_data

def get_channel_rawData(well_data, site, frame, channel):
    return well_data[site][frame][channel]

def get_frame_data(well_data, site, frame):
    return well_data[site][frame]

def get_site_data(well_data, site):
    return well_data[site]


# nd2_filename = "../doc/WellD01_ChannelmIFP,mCherry,YFP_Seq0000.nd2"
# well_data = read_nd2(nd2_filename)
# site = 1
# frame = 5
# channel = 2
# print(len(get_frame_data(well_data, site, frame)))
# print(len(get_site_data(well_data, site)))
# print(len(well_data))