import nd2reader
import tifffile
import numpy as np

def read_nd2(nd2_filename):
    with nd2reader.Nd2(nd2_filename) as nd2_movie:
        nF = len(nd2_movie)
        nC = 3

        movie_dict = {}

        for frame_number, frame in enumerate(nd2_movie):
            frame_data = {}

            for channel_number in range(nC):
                frame_data[channel_number] = np.array(frame[channel_number])
            movie_dict[frame_number] = frame_data
    
    return movie_dict

def get_channel_rawData(movie_dict, frame, channel):
    channel_matrix = []
    if frame in movie_dict:
        frame_data = movie_dict[frame]
    
        if channel in frame_data:
            channel_matrix = frame_data[channel]
        else:
            print("Channel not found")
    else:
        print("frame not found")

    return channel_matrix    


nd2_filename = "../doc/WellD01_ChannelmIFP,mCherry,YFP_Seq0000.nd2"
test_movie = read_nd2(nd2_filename)
f0_c0 = get_channel_rawData(test_movie, 0, 0)
print(f0_c0)
print(type(test_movie[0][0]))
