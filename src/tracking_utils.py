"""Functions for cell tracking.

    * is_pixel_inside_contour - checks if a pixel is inside a contour
    * get_center - gets center of a contour
    * do_watershed - segments an image with watershedding
    * dist_between_points - calculates the distance between two points
    * link_cell -
    * resolve_child_conflicts -
    * link_next_frame - links all of the cells in a new frame to 
                        the cell lineages in the master cell list 
                        (and all previous frames)
"""

import numpy as np
import matplotlib.pyplot as plt
import cv2
import os
import math
import read_nd2
from cell import Cell
import pandas as pd


def is_pixel_inside_contour(pixel, contour):
    """
    Checks if a pixel is inside a contour (is fluorescence inside a cell).

    Args:
        pixel: A tuple (x, y) representing the pixel's coordinates.
        contour: A list of contour points, obtained from cv2.findContours.

    Returns:
        True if the pixel is inside the contour, False otherwise.
    """
    try:
        x, y = pixel
        point = (x, y)
        return cv2.pointPolygonTest(contour, point, False) >= 0
    except:
        raise ValueError("pixel must be a tuple (x, y)")


def get_center(contour):
    """
    Gets center of contour.

    Args:
        contour: A list of contour points, obtained from cv2.findContours.

    Returns:
        The centroid of the contour (x,y).
    """
    # Calculate moments for the contour
    M = cv2.moments(contour)

    # Calculate the centroid (center) of the contour
    try:    
        cx = int(M["m10"] / M["m00"])
        cy = int(M["m01"] / M["m00"])
    except ZeroDivisionError:
        cx, cy = 0, 0 # Handle division by zero if the contour has no area 

    # add centroid to list of cell centers
    return ((cx, cy))


def do_watershed(movie, frame_num):
    """
    Segments an image with watershedding.

    Args:
        img: image to segment

    Returns:
        cells: list of cells (1 for each cell)
    """
    channel0_data = read_nd2.get_channel_rawData(movie, 0, frame_num, 0)
    rgb_nuc = np.dstack((channel0_data,
                         channel0_data, channel0_data))
    try:
        rgb_nuc = cv2.normalize(rgb_nuc, None, 0, 255,
                                cv2.NORM_MINMAX, dtype=cv2.CV_8U)
    except cv2.error:
        print("cv2.error: Could not normalize image")
        raise cv2.error
    
    # convert to grayscale
    try:
        grayscale = cv2.cvtColor(rgb_nuc, cv2.COLOR_BGR2GRAY)
    except cv2.error:
        print("Image not compatible with watershedding")
        raise cv2.error

    # threshold image
    thresh = cv2.threshold(grayscale, 0, 255,
                           cv2.THRESH_BINARY+cv2.THRESH_OTSU)[1]

    # get sure background area
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    sure_bg = cv2.dilate(thresh, kernel, iterations=3)

    # Distance transform
    dist = cv2.distanceTransform(thresh, cv2.DIST_L2, 5)

    # get foreground area
    ret, sure_fg = cv2.threshold(dist, 0.2 * dist.max(),
                                 255, cv2.THRESH_BINARY)
    sure_fg = sure_fg.astype(np.uint8)

    # get unknown area
    unknown = cv2.subtract(sure_bg, sure_fg)

    # connected components
    ret, markers = cv2.connectedComponents(sure_fg)
    markers = markers.astype(np.int32)
    # Add one to all labels so that background is not 0, but 1
    markers += 1
    # mark the region of unknown with zero
    markers[unknown == 255] = 0

    # apply watershed algorithm
    markers = cv2.watershed(rgb_nuc, markers)

    labels = np.unique(markers)

    cells = []
    for label in labels[2:]:
        # Create a binary image in which only the
        # area of the label is in the foreground
        # and the rest of the image is in the background
        target = np.where(markers == label,
                          255, 0).astype(np.uint8)

        # Perform contour extraction on the created binary image
        contours, hierarchy = cv2.findContours(target, cv2.RETR_EXTERNAL,
                                               cv2.CHAIN_APPROX_SIMPLE)

        # check if contour area is over a threshold
        try:
            cont_area = cv2.contourArea(contours[0])
        except IndexError:
            print("No contours found")
            raise IndexError
        
        area_threshold = 1000
        if cont_area > area_threshold:
            continue
        else:
            center = get_center(contours[0])
            cont_rect = cv2.boundingRect(contours[0])
            mVenus_avg = get_channel_data_within_contour(movie, frame_num, cont_rect, channel=2)
            curr_cell = Cell()
            curr_cell.add_coordinate(center)
            curr_cell.add_contour(cont_rect)
            curr_cell.add_channel3_avg(mVenus_avg)
            cells.append(curr_cell)

    return cells


def get_channel_data_within_contour(movie, frame_num, contour, channel):
    """
    doc string
    """
    # get desired channel raw data
    frame_data = read_nd2.get_frame_data(movie, 0, frame_num)
    
    # get bounding rectangle
    x, y, w, h = contour
    
    # get channel data from rectangle
    roi = frame_data[y:y+h, x:x+w, channel]
    
    # compute average pixel value within contour
    average_pixel_val = roi.mean()

    return average_pixel_val


def dist_between_points(coord_a, coord_b):
    """
    Calculates the distance between two points.

    Args:
        coord_a: first coordinate (x,y).
        coord_b: second coordinate (x,y).

    Returns:
        distance: the distance between coord_a and coord_b.
    """
    try:
        x1, y1 = coord_a
        x2, y2 = coord_b
    except ValueError:
        raise ValueError("coord_a and coord_b must be tuples (x, y)")

    # Calculate the Euclidean distance between the two points
    distance = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
    return distance


def link_cell(parent_cell, curr_frame_cells):
    """
    Links a parent cell (cell from the previous frame) to two 
    cells in the current frame based on closest proximity.

    Args:
        parent_cell: A cell object to be linked to a cell in curr_frame_cells.
        curr_frame_cells: A list of all cells in the current (newest) frame.

    Returns:
        output (dict): A dictionary containing the two cells in the current frame
        closest to the parent cell and their corresponding distances from the parent cell.
    """
    # get most recent coordinate of cell from dictionary
    prev_point = parent_cell.get_most_recent_coord()
    # initialize list of distances
    dists = {}
    for curr_cell in curr_frame_cells:
        try:
            curr_point = curr_cell.coords[0]
        except IndexError:
            # not gonna kill process bc it can continue to next cells
            print("No coordinates found") 
        # get distance from every other point
        dists[curr_cell] = dist_between_points(prev_point, curr_point)

    # add coord with smallest distance
    curr_smallest_dists = [float('inf'), float('inf')]
    closest_cells = [None, None]
    for dist_cell in dists:
        if dists[dist_cell] < curr_smallest_dists[0]:
            curr_smallest_dists[0] = dists[dist_cell]
            closest_cells[0] = dist_cell
        elif dists[dist_cell] < curr_smallest_dists[1]:
            curr_smallest_dists[1] = dists[dist_cell]
            closest_cells[1] = dist_cell

    output = {}
    output[closest_cells[0]] = curr_smallest_dists[0]
    output[closest_cells[1]] = curr_smallest_dists[1]
    return output

def get_cells_to_cull(cell_list, dist_threshold):
    """
    Checks if any cells share a position in the most recent frame,
    and decides which cells should be culled based on distance between
    their two most recent coordinates.
    
    Args:
        cell_list (list): A list of cell objects.

    Returns:
        cells_to_cull (set): A set containing the cells that should be culled.
    """

    cells_to_cull = []
    positions_dict = {}
    for curr_cell in cell_list:
        # get most recent position
        curr_position = curr_cell.get_most_recent_coord()
        # get distance between two most recent coords
        curr_dist = dist_between_points(curr_cell.coords[len(curr_cell.coords)-2],
                                                      curr_position)

        is_duplicate = False
        # if position is already in list, figure out which cell should be culled
        for comparison_cell in positions_dict:
            # FIRST, get cells to cull based on duplicates
            comparison_position = positions_dict[comparison_cell]
            if curr_position == comparison_position:
                # check which cell was closer to new position

                try:
                    comparison_dist = dist_between_points(comparison_cell.coords[len(comparison_cell.coords)-2],
                                                        comparison_position)
                except IndexError:
                    print("No coordinates found for linking")
                    raise IndexError
                
                if comparison_dist < curr_dist:
                    cells_to_cull.append(curr_cell)
                    is_duplicate = True
                else:
                    cells_to_cull.append(comparison_cell)
        # SECOND, get cells to cull based on big jumps
        if not is_duplicate:
            # check if current position is over a threshold from previous position
            if curr_dist > dist_threshold:
                cells_to_cull.append(curr_cell)

        # add to positions list
        positions_dict[curr_cell] = curr_position
    
    cells_to_cull = set(cells_to_cull)           
    return cells_to_cull


def cull_duplicates(cell_list, problematic_cells):
    """
    Removes a given subset of cells (here, problematic cells) from a list of cells.

    Args:
        cell_list (list): A list of cell objects.
        problematic_cells (list): A list of cell objects to be removed from cell list.

    Returns:
        resolved_tracks: A list of all cells in cell list that are not in problematic_cells.
    """

    culled_set = set(cell_list).difference(set(problematic_cells))

    resolved_tracks = list(culled_set)
    return resolved_tracks


def resolve_child_conflicts(candidates, child_dist_thresh):
    """
    Ensures that each child only has one parent. Checks if new cell and possible
    child tracks are plausible (i.e. below a certain distance threshold). Matches 
    each child to its most likely parent based on proximity, and drops other possible parents.

    Args:
        candidates: A list with len(master_cell_list) where each entry is a 
                    dictionary with two values. Each dictionary entry has a 
                    key (a cell) and a value (the distance of that cell from 
                    the cell with a corresponding index in the master cell list).
        child_dist_thresh (int): The maximum distance between the parent cell
                    and possible child cell such that the child cell can be assigned to
                    that parent.

    Returns:
        resolved_tracks: A list with same length as candidates list, where each entry
                         is a list of length 0, 1, or 2. 
                         - If length is 0, the cell with corresponding index in the
                           master cell list should be culled.
                         - If length is 1, it contains a cell object which should be 
                           matched to the cell with corresponding index in the master cell list. 
                         - If length is 2, it contains 2 cell objects: that cell 
                           object to be matched, as well as a "newborn" child cell to be 
                           added to the master cell list with its parent being matched 
                           to the cell with corresponding index in the master cell list.
    """
    # loop over candidates
    # print(candidates.shape)
    resolved_tracks = np.empty(len(candidates), dtype=object)
    for i in range(0, len(candidates)):

        # dictionary with 2 entries, key is cell, value is distance
        curr_candidates = candidates[i]
        keys = list(curr_candidates.keys())

        try:
            most_likely_cell = keys[0]
            most_likely_dist = curr_candidates[most_likely_cell]
            pot_child_cell = keys[1]
            pot_child_dist = curr_candidates[pot_child_cell]
        except IndexError:
            print("Candidates missing")
            raise IndexError

        # check that any potential child is within threshold
        # if not, because original most likely distance is within threshold,
        # add most likely cell -- NOT pot_child
        if pot_child_dist > child_dist_thresh:
            resolved_tracks[i] = [most_likely_cell]
        # check if potential child is most likely of any other cell
        # if not, check if it's a potential child of any others
        else:
            owns_child = True

            for comparison_candidates in candidates:
                try:
                    comparison_keys = list(comparison_candidates.keys())
                    comp_most_likely_cell = comparison_keys[0]
                    comp_pot_child_cell = comparison_keys[1]
                    comp_pot_child_dist = comparison_candidates[comp_pot_child_cell]
                except IndexError:
                    print("Candidates missing")
                    raise IndexError
                
                if pot_child_cell == comp_most_likely_cell:
                    owns_child = False
                    # resolved_tracks[i] = [most_likely_cell]
                    break
                elif pot_child_cell == comp_pot_child_cell:
                    # check distances between child and two master cells

                    if pot_child_dist >= comp_pot_child_dist:
                        # if child is closer to current cell,
                        # add it to resolved track
                        owns_child = False
                        
            if owns_child is True:
                resolved_tracks[i] = [most_likely_cell, pot_child_cell]
            else:
                resolved_tracks[i] = [most_likely_cell]

    return resolved_tracks


def link_next_frame(master_cell_list, movie, frame_num):
    """
    Links all of the cells in a new frame to the cell
    lineages in the master cell list (and all previous frames).
    Cells must be matched to their position in the next frame,
    as well as any possible children (maximum 1), in the event
    of a division. This is based on proximity.

    Args:
        master_cell_list: list of cells
        curr_frame: image from current frame to segment
        frame_num: frame number (used to note cell "birthdays")

    Returns:
        new_cells: updated list of cells based on new data
    """
    # get all the cells in the current frame
    curr_frame_cells = do_watershed(movie, frame_num)

    # check cells against previous frame
    candidates = np.empty(len(master_cell_list), dtype=object)
    for i in range(0, len(master_cell_list)):
        # get closest two cells
        cell = master_cell_list[i]
        closest_cells = link_cell(cell, curr_frame_cells)
        candidates[i] = closest_cells

    # now we have list of possible candidates
    # want to make sure that each cell has
    # one & only one candidate child (or 2 in the case it divided)
    resolved_tracks = resolve_child_conflicts(candidates, 50)

    # initialize list of new cells to add
    new_cells = []
    # loop over resolved tracks and add to master cell list
    for i in range(0, len(master_cell_list)):
        # get current cell from master cell list
        curr_cell = master_cell_list[i]
        # if there was a big gap, cull cell, don't add to new cell list
        if len(resolved_tracks[i]) == 0:
            pass
        # if there's one child, add it to master cell object
        elif len(resolved_tracks[i]) == 1:
            # add coord and contour from closest cell to master cell object
            curr_cell.add_coordinate(resolved_tracks[i][0].coords[0])
            curr_cell.add_contour(resolved_tracks[i][0].contours[0])
            curr_cell.add_channel3_avg(resolved_tracks[i][0].channel3_avg[0])
            new_cells.append(curr_cell)
        elif len(resolved_tracks[i]) == 2:
            # create new cell in master list with parent history
            new_cell = Cell(parent=curr_cell, birthday=frame_num)

            # give child its tracking
            new_cell.add_coordinate(resolved_tracks[i][1].coords[0])
            new_cell.add_contour(resolved_tracks[i][1].contours[0])
            new_cell.add_channel3_avg(resolved_tracks[i][1].channel3_avg[0])
            new_cells.append(new_cell)

            # give parent its child
            curr_cell.add_child(new_cell)
            # give parent its tracking info
            curr_cell.add_coordinate(resolved_tracks[i][0].coords[0])
            curr_cell.add_contour(resolved_tracks[i][0].contours[0])
            curr_cell.add_channel3_avg(resolved_tracks[i][0].channel3_avg[0])
            new_cells.append(curr_cell)

    # add newborn cells to master cell list
    return new_cells


# def correct_links(cell_list):
#     """
#     Corrects a cell list by identifying and culling problematic cells.

#     Args:
#         cell_list (list): A list of cell objects.

#     Returns:
#         corrected_cell_list (list): A modified list of cell objects after culling problematic cells.
#     """
#     try:
#         problematic_cells = get_cells_to_cull(cell_list)
#     except IndexError:
#         print("cell list is empty")
#         raise IndexError
    
#     if problematic_cells is not None:
#         corrected_cell_list = cull_duplicates(cell_list, problematic_cells)
#     else:
#         corrected_cell_list = cell_list
    
#     return corrected_cell_list


# KEEP TO REIMPLEMENT TRACK HEALING

def track_healing(cell_list, dist_thresh):
    # iterate over cell list and attempt healing
    # if healing is done, make unproblematic
    healed_tracks = np.empty(len(cell_list), dtype=object)
    for i, cell in enumerate(cell_list):
        # get most recent coord
        most_recent_coord = cell.get_most_recent_coord()
        # get coord from 2 frames ago
        two_frames_ago_coord = cell.coords[len(cell.coords)-3]
        # if dist between positions is below threshold, heal track
        if dist_between_points(most_recent_coord, two_frames_ago_coord) < dist_thresh:
            # set coord from 1 frame ago to avg of recent positions
            healed_x = (most_recent_coord[0] + two_frames_ago_coord[0])/2
            healed_y = (most_recent_coord[1] + two_frames_ago_coord[1])/2
            healed_pos = (healed_x, healed_y)
            cell.coords[len(cell.coords)-2] = healed_pos
            # make unproblematic
            cell.make_unproblematic_cell()
        else:
            # increment problematic status
            cell.increment_problematic()
        # so now all cells should be either 0 or 2 problematic status
        # i.e. to live or to die (no more on death row)
        healed_tracks[i] = cell
    
    return healed_tracks

# def correct_links(cell_list, distance_threshold):

#     # get old problematic cells
#     old_problematics = get_all_problematics(cell_list)
#     # attempt to deal with these through track healing
#     if old_problematics is not None:
#         healed_tracks = track_healing(old_problematics, distance_threshold)
#         # see which of these are still problematic
#         still_problematics = get_all_problematics(healed_tracks)
#         # cull still problematic cells
#         if still_problematics is not None:
#             corrected_cell_list = cull_duplicates(cell_list, still_problematics)
#         else:
#             corrected_cell_list = cell_list
#         # now there should be no problematic cells left
#         # they have been either culled or healed
#         # so now, can get new problematic cells
#         current_problematic_cells = get_cells_to_cull(corrected_cell_list)
#         increment_all_problematics(current_problematic_cells)
#         return corrected_cell_list
#     else:
#         current_problematic_cells = get_cells_to_cull(cell_list)
#         # set problematic
#         increment_all_problematics(current_problematic_cells)
#         test = get_all_problematics(cell_list)
#         return cell_list

def increment_all_problematics(cell_list):
    """
    Iterates through list of problematic cells

    Args:
        cell_list (list): A list of cell objects.
    
    Returns:
        problematics_list: 
    """
    problematics_list = np.empty(len(cell_list), dtype=object)
    for i, cell in enumerate(cell_list): # cells_to_cull
        cell.increment_problematic()
        problematics_list[i] = cell
    
    return problematics_list

# gets all problematic cells from cell list
def get_all_problematics(cell_list):
    """
    Args:
        cell_list (list): A list of cell objects.
    
    Returns:
        problem_cells: 
    """
    problem_cells = []
    for cell in cell_list:
        if cell.problematic == 1:
            problem_cells.append(cell)
    if len(problem_cells) == 0:
        return None
    else:
        return problem_cells


def get_all_death_row(cell_list):
    """
    Args:
        cell_list (list): A list of cell objects.
    
    Returns:
        problem_cells: 
    """
    problem_cells = []
    for cell in cell_list:
        if cell.problematic == 2:
            problem_cells.append(cell)
    if len(problem_cells) == 0:
        return None
    else:
        return problem_cells


def correct_links(cell_list, distance_threshold):

    # get old problematic cells
    # all should have problematic value of 1 here
    old_problematics = get_all_problematics(cell_list)
    # attempt to deal with these through track healing
    if old_problematics is not None:
        healed_tracks = track_healing(old_problematics, distance_threshold)
        # see which of these are still problematic
        # 
        death_row = get_all_death_row(healed_tracks)
        # cull still problematic cells
        if death_row is not None:
            corrected_cell_list = cull_duplicates(cell_list, death_row)
        else:
            corrected_cell_list = cell_list
        # now there should be no problematic cells left
        # they have been either culled or healed
        # so now, can get new problematic cells
        # note distthresh is divided by 2 because distthresh is based on what is reasonable
        # for the cell to have moved across 2 frames, here we want only what is reasonable
        # movement for one frame
        current_problematic_cells = get_cells_to_cull(corrected_cell_list, distance_threshold/2)
        current_problematic_cells = increment_all_problematics(current_problematic_cells)

        corrected_cell_list = list(set(corrected_cell_list).difference(set(current_problematic_cells)))
        corrected_cell_list.extend(current_problematic_cells)

        return corrected_cell_list
    else:
        # if there are no problematics from the last frame, just get the current 
        # problematic cells and set to 1
        current_problematic_cells = get_cells_to_cull(cell_list, distance_threshold/2)
        # incremenet problematic for all current cells
        current_problematic_cells = increment_all_problematics(current_problematic_cells)

        corrected_cell_list = list(set(cell_list).difference(set(current_problematic_cells)))
        corrected_cell_list.extend(current_problematic_cells)

        return corrected_cell_list