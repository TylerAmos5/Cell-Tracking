"""Functions for cell tracking.

    * is_pixel_inside_contour - checks if a pixel is inside a contour
    * get_center - gets center of a contour
    * do_watershed - segments an image with watershedding
    * dist_between_points - calculates the distance between two points
    * link_cell -
    * resolve_conflicts -
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
    Checks if a pixel is inside a contour.

    Args:
        pixel: A tuple (x, y) representing the pixel's coordinates.
        contour: A list of contour points, obtained from cv2.findContours.

    Returns:
        True if the pixel is inside the contour, False otherwise.
    """
    x, y = pixel
    point = (x, y)
    return cv2.pointPolygonTest(contour, point, False) >= 0


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
    if M["m00"] != 0:
        cx = int(M["m10"] / M["m00"])
        cy = int(M["m01"] / M["m00"])
    else:
        cx, cy = 0, 0  # Handle division by zero if the contour has no area

    # add centroid to list of cell centers
    return ((cx, cy))


def do_watershed(img):
    """
    Segments an image with watershedding.

    Args:
        img: image to segment

    Returns:
        cells: list of cells (1 for each cell)
    """
    # img = cv2.normalize(img, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
    # convert to grayscale
    grayscale = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

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
    markers = cv2.watershed(img, markers)

    labels = np.unique(markers)

    cells = []
    for label in labels[2:]:
        # Create a binary image in which only the
        # area of the label is in the foreground
        # and the rest of the image is in the background
        target = np.where(markers == label,
                          255, 0).astype(np.uint8)

        # Perform contour extraction on the created binary image
        contours, hierarchy = cv2.findContours(
            target, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )

        # check if contour area is over a threshold
        cont_area = cv2.contourArea(contours[0])
        area_threshold = 1000
        if cont_area > area_threshold:
            continue
        else:
            center = get_center(contours[0])
            cont_rect = cv2.boundingRect(contours[0])
            curr_cell = Cell()
            curr_cell.add_coordinate(center)
            curr_cell.add_contour(cont_rect)
            cells.append(curr_cell)

    return cells


def dist_between_points(coord_a, coord_b):
    """
    Calculates the distance between two points.

    Args:
        coord_a: first coordinate (x,y).
        coord_b: second coordinate (x,y).

    Returns:
        distance: the distance between coord_a and coord_b.
    """
    x1, y1 = coord_a
    x2, y2 = coord_b

    # Calculate the Euclidean distance between the two points
    distance = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
    return distance


def link_cell(parent_cell, curr_frame_cells):
    """
    ....

    Args:
        parent_cell:
        curr_frame_cells:

    Returns:
        output:
    """
    # get most recent coordinate of cell from dictionary
    prev_point = parent_cell.get_most_recent_coord()
    # initialize list of distances
    dists = {}
    for curr_cell in curr_frame_cells:
        curr_point = curr_cell.coords[0]
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

def get_cells_to_cull(cell_list):
    """
    Checks if any cells share a position in the most recent frame,
    and decides which cells should be culled based on distance between
    their two most recent coordinates.
    
    Args:
        cell_list:

    Returns:
        cells_to_cull:
    """
    cells_to_cull = []
    positions_dict = {}
    for curr_cell in cell_list:
        # get most recent position
        curr_position = curr_cell.get_most_recent_coord()
        # if position is already in list, figure out which cell should be culled
        for comparison_cell in positions_dict:
            comparison_position = positions_dict[comparison_cell]
            if curr_position == comparison_position:
                # check which cell was closer to new position
                comparison_dist = dist_between_points(comparison_cell.coords[len(comparison_cell.coords)-2],
                                                      comparison_position)
                curr_dist = dist_between_points(curr_cell.coords[len(curr_cell.coords)-2],
                                                      curr_position)
                if comparison_dist < curr_dist:
                    cells_to_cull.append(curr_cell)
                else:
                    cells_to_cull.append(comparison_cell)
        # add to positions list
        positions_dict[curr_cell] = curr_position
    
    cells_to_cull = set(cells_to_cull)           
    return cells_to_cull
        

def cull_duplicates(cell_list):
    """
    Ensures that two cells aren't assigned the same position in a new frame,
    and removes duplicate cells created from segmentation errors.
    Designed to resolve errors in segmentation where one cell is identified
    as multiple cells, or multiple cells as one, intermittently. 
    
    Args:
        cell_list:

    Returns:
        resolved_tracks:
    """

    # first, get list of cells to cull
    cells_to_cull = get_cells_to_cull(cell_list)
    # now remove these cells from cell list
    culled_set = set(cell_list).difference(cells_to_cull)

    resolved_tracks = list(culled_set)
    return resolved_tracks


def resolve_child_conflicts(candidates):
    """
    Ensures that each child only has one parent. Matches each child to its
    most likely parent based on proximity, and drops other possible parents.

    Args:
        candidates:

    Returns:
        resolved_tracks:
    """
    # loop over candidates
    # print(candidates.shape)
    resolved_tracks = np.empty(len(candidates), dtype=object)
    for i in range(0, len(candidates)):

        # dictionary with 2 entries, key is cell, value is distance
        curr_candidates = candidates[i]
        keys = list(curr_candidates.keys())

        most_likely_cell = keys[0]
        most_likely_dist = curr_candidates[most_likely_cell]
        pot_child_cell = keys[1]
        pot_child_dist = curr_candidates[pot_child_cell]

        # check if potential child is most likely of any other cell
        # if not, check if it's a potential child of any others

        owns_child = True

        for comparison_candidates in candidates:

            comparison_keys = list(comparison_candidates.keys())

            comp_most_likely_cell = comparison_keys[0]
            comp_pot_child_cell = comparison_keys[1]
            comp_pot_child_dist = comparison_candidates[comp_pot_child_cell]

            if pot_child_cell == comp_most_likely_cell:
                owns_child = False
                # resolved_tracks[i] = [most_likely_cell]
                break
            elif pot_child_cell == comp_pot_child_cell:
                # check distances between child and two master cells

                if pot_child_dist > comp_pot_child_dist:
                    # if child is closer to current cell,
                    # add it to resolved track
                    owns_child = False
                    break
        if owns_child is True:
            resolved_tracks[i] = [most_likely_cell, pot_child_cell]
        else:
            resolved_tracks[i] = [most_likely_cell]
    return resolved_tracks


def link_next_frame(master_cell_list, curr_frame, frame_num):
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
    curr_frame_cells = do_watershed(curr_frame)
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
    resolved_tracks = resolve_child_conflicts(candidates)

    # initialize list of new cells to add
    new_cells = []
    # loop over resolved tracks and add to master cell list
    for i in range(0, len(master_cell_list)):
        # get current cell from master cell list
        curr_cell = master_cell_list[i]
        # if there's one child, add it to master cell object
        if len(resolved_tracks[i]) == 1:
            # add coord and contour from closest cell to master cell object
            curr_cell.add_coordinate(resolved_tracks[i][0].coords[0])
            curr_cell.add_contour(resolved_tracks[i][0].contours[0])
            new_cells.append(curr_cell)
        elif len(resolved_tracks[i]) == 2:
            # create new cell in master list with parent history
            new_cell = Cell(parent=curr_cell, birthday=frame_num)

            # give child its tracking
            new_cell.add_coordinate(resolved_tracks[i][1].coords[0])
            new_cell.add_contour(resolved_tracks[i][1].contours[0])
            new_cells.append(new_cell)

            # give parent its child
            curr_cell.add_child(new_cell)
            # give parent its tracking info
            curr_cell.add_coordinate(resolved_tracks[i][0].coords[0])
            curr_cell.add_contour(resolved_tracks[i][0].contours[0])
            new_cells.append(curr_cell)

    # add newborn cells to master cell list
    return new_cells
