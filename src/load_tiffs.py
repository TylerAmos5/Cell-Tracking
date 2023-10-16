import numpy as np
import matplotlib.pyplot as plt
import cv2
import os
import re

def extract_numbers(s):
    numbers = [int(num) for num in re.findall(r'\d+', s)]
    return numbers



# Im thinking we can make an outer function that can iterate through the folders.
# We'll have to go Row[A-H] > Column[1-12] > site[1-2] 
# This will follow the structure R_C_S
# Each site will have f=frames and 3 channels
# For each movie, there will be f*3=individual TIF images
#                   for Row
#                       for column
#                           for site
#                               export as separate frames and separate channels
#                               name as R_C_S_f_ch
#                               R = row, C=column,f=frame,  Ch=channel
#                         
# The ImageJ macro that we write should autosave images with this structure 
# It will require handling of the raw file name, so keep the original structure of the nd2 file around
# If this slows down our program too much, we can remove it and say it processes 1 movie at a time
def read_images_from_folder(folder_path):
    image_list = []

    # Check if the folder exists
    if not os.path.exists(folder_path):
        print(f"The folder '{folder_path}' does not exist.")
        return []

    # Get a list of files in the folder
    files = os.listdir(folder_path)
    file_list = []
    p = r'.tif'
    for file_name in files:
        if re.search(p, file_name):
            file_list.append(file_name)

    file_list = sorted(file_list,key=extract_numbers)
    print(file_list)
# sort filenames by frame
        # read in files in triplet to store the pixels from multiple images in one structure 
        # continue through all frames until 3 channels for each frame is stored. 
    # Iterate through the files and read images
    movie = []
    for i in range(0, len(file_list), 3):
        full_frame_channels = file_list[i:i+3]
        for j in range(3):
            cur_file = full_frame_channels[j]
            movie.append([])
            file_path = os.path.join(folder_path, cur_file)
            image = cv2.imread(file_path)
            if image is None:
                print('Failed to read pixels')
            else:
                pixel_matrix = np.array(image)
            
            movie[i].append(pixel_matrix)
         
    return movie
        
# set working directory
my_path = "/Users/tyleramos/Cell-Tracking/doc/TIFFS"

stack = read_images_from_folder(my_path)
print(len(stack))