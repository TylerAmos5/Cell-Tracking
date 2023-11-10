import sys

sys.path.insert(0,'src/') # noqa

import tracking_utils
import unittest
import numpy as np
import random
import cv2
# import os
from cell import Cell


class TestCellTracking(unittest.TestCase):

    # testing get_center()    
    def test_get_center_output_type(self):
        test_contour = (np.array([[[1297, 2030]], [[1296, 2031]], [[1294, 2031]],
                               [[1293, 2032]], [[1291, 2032]], [[1290, 2033]],
                               [[1289, 2033]], [[1288, 2032]], [[1287, 2033]],
                               [[1281, 2033]], [[1280, 2032]], [[1279, 2033]],
                               [[1278, 2032]], [[1277, 2033]], [[1276, 2033]],
                               [[1273, 2036]], [[1272, 2035]], [[1271, 2036]],
                               [[1270, 2036]], [[1269, 2037]], [[1268, 2037]],
                               [[1267, 2038]], [[1266, 2038]], [[1265, 2039]],
                               [[1264, 2039]], [[1265, 2040]], [[1264, 2041]],
                               [[1264, 2042]], [[1261, 2045]], [[1259, 2045]],
                               [[1259, 2046]], [[1302, 2046]], [[1304, 2044]],
                               [[1304, 2043]], [[1307, 2040]], [[1306, 2039]],
                               [[1306, 2038]], [[1305, 2037]], [[1305, 2036]], 
                               [[1304, 2035]], [[1304, 2034]], [[1303, 2033]],
                               [[1302, 2033]], [[1300, 2031]], [[1298, 2031]]]))
        r = tracking_utils.get_center(test_contour)
        self.assertEqual(len(r), 2)

    def test_get_center_square_contour(self):
        test_contour = (np.array([[[1, 1]], [[1, 5]], [[5, 5]], [[5, 1]]]))
        r = tracking_utils.get_center(test_contour)
        a = (3, 3)
        self.assertEqual(a, r)

    def test_get_center_divide_by_zero(self):
        zero_contour = (np.array([[[0, 0]], [[0, 0]], [[0, 0]],
                               [[0, 0]], [[0, 0]], [[0, 0]],
                               [[0, 0]], [[0, 0]], [[0, 0]],
                               [[0, 0]], [[0, 0]], [[0, 0]]]))
        r = tracking_utils.get_center(zero_contour)
        a = (0, 0)
        self.assertEqual(a, r)

    # testing is_pixel_inside_contour()
    def test_is_pixel_inside_contour_false(self):
        test_contour = (np.array([[[1, 1]], [[1, 5]], [[5, 5]], [[5, 1]]]))
        r = tracking_utils.is_pixel_inside_contour((6, 6), test_contour)
        self.assertEqual(False, r)

    def test_is_pixel_inside_contour_true(self):
        test_contour = (np.array([[[1, 1]], [[1, 5]], [[5, 5]], [[5, 1]]]))
        r = tracking_utils.is_pixel_inside_contour((2, 2), test_contour)
        self.assertEqual(True, r)

    def test_is_pixel_inside_contour_zero_contour(self):
        zero_contour = (np.array([[[0, 0]], [[0, 0]], [[0, 0]],
                               [[0, 0]], [[0, 0]], [[0, 0]],
                               [[0, 0]], [[0, 0]], [[0, 0]],
                               [[0, 0]], [[0, 0]], [[0, 0]]]))
        r = tracking_utils.is_pixel_inside_contour((2, 2), zero_contour)
        self.assertEqual(False, r)

    # testing dist_between_points()
    def test_dist_between_points(self):
        rand = random.randint(1, 100)
        r = tracking_utils.dist_between_points((0, 0),(0, rand))
        a = rand
        self.assertEqual(a, r)

    def test_dist_between_points_same_point(self):
        r = tracking_utils.dist_between_points((0, 1),(0, 1))
        a = 0
        self.assertEqual(a, r)

    def test_dist_between_points_random_points(self):
        g = (random.randint(1, 100), random.randint(1, 100))
        h = (random.randint(1, 100), random.randint(1, 100))
        r = tracking_utils.dist_between_points(g,h)
        a = ((g[0]-h[0])**2 + (g[1]-h[1])**2)**0.5
        self.assertEqual(a, r)

    # testing do_watershed()
    def test_do_watershed_black_image(self):
        img = np.zeros((100, 100, 3), dtype=np.uint8)           
        cells = tracking_utils.do_watershed(img)    
        self.assertIsInstance(cells, list)  # check if the result is a list
        for cell in cells:
            self.assertIsInstance(cell, Cell)  # check if each item in the list is an instance of the Cell class
        self.assertEqual([], cells) # see if list of cells empty for blank image

    def test_do_watershed_test_image(self):
        img = cv2.imread("test/data/test_image.png")  # image of "normal" size        
        cells = tracking_utils.do_watershed(img)    
        self.assertIsInstance(cells, list) 
        for cell in cells:
            self.assertIsInstance(cell, Cell)  
        self.assertNotEqual([], cells)  # should be cells in this image

    def test_do_watershed_test_image_9cells(self):
        img = cv2.imread("test/data/test_image_9cells.png")   
        cells = tracking_utils.do_watershed(img)
        self.assertIsInstance(cells, list)
        for cell in cells:
            self.assertIsInstance(cell, Cell)  
        self.assertEqual(len(cells), 9)  # count number of cells in image

    # def test_do_watershed_test_image_varied_size_brightness(self): # CURRENTLY FAILS
    #     img = cv2.imread("test/data/test_image_varied_size_brightness_15.png")
    #     cells = tracking_utils.do_watershed(img)
    #     self.assertIsInstance(cells, list)
    #     for cell in cells:
    #         self.assertIsInstance(cell, Cell)
    #     self.assertEqual(len(cells), 15) # count number of cells in image (program found 9)

    # def test_do_watershed_test_image_some_overlap(self): # CURRENTLY FAILS
    #     img = cv2.imread("test/data/test_image_some_overlap_28.png")   
    #     cells = tracking_utils.do_watershed(img)
    #     self.assertIsInstance(cells, list)
    #     for cell in cells:
    #         self.assertIsInstance(cell, Cell)
    #     self.assertEqual(len(cells), 28) # count number of cells in image (program found 23)

    # add tests to see if more than just cell count is correct???

    # testing resolve_conflicts()
    def test_resolve_child_conflicts(self):
        candidates = [] # update this with more realistic list of candidates
        resolved_tracks = tracking_utils.resolve_child_conflicts(candidates)
        for cell in resolved_tracks:
            self.assertIsInstance(cell, Cell)

    # these still need to be worked out:

    # def test_resolve_conflicts_no_conflicts(self):
    #     candidates = []
    #     r= cell_tracking_OO_KB_testing.resolve_conflicts(candidates)
    #     a = []
    #     self.assertEqual(a,r)

    # def test_resolve_conflicts_with_conflicts(self):
    #     candidates = []
    #     r = cell_tracking_OO_KB_testing.resolve_conflicts(candidates)
    #     a = []
    #     self.assertEqual(a,r)

    # def test_resolve_child_conflicts_empty_candidates(self):  # this isn't working
    #     candidates = []
    #     r = tracking_utils.resolve_child_conflicts(candidates)
    #     for cell in r:
    #         self.assertIsInstance(cell, Cell)
    #     print(r)
    #     a = np.array([], dtype=object)
    #     self.assertEqual(a, r)

    # testing link_cell()
    def test_link_cell(self):
        # Create dummy cells for testing
        class MockCell:
            def __init__(self, coords):
                self.coords = [coords]

            def get_most_recent_coord(self):
                return self.coords[-1]

        parent_cell = MockCell((0, 0))
        curr_frame_cells = [
            MockCell((1, 1)),
            MockCell((2, 2)),
            MockCell((3, 3)),
        ]

        output = tracking_utils.link_cell(parent_cell, curr_frame_cells)

        self.assertEqual(len(output), 2)  # should contain two cells
        self.assertIn(curr_frame_cells[0], output)  # closest cell should be in the output
        self.assertIn(curr_frame_cells[1], output)  # second closest cell should be in the output

    def test_link_cell_no_movement(self):
        # Create dummy cells for testing
        class MockCell:
            def __init__(self, coords):
                self.coords = [coords]

            def get_most_recent_coord(self):
                return self.coords[-1]

        parent_cell = MockCell((0, 0))
        curr_frame_cells = [
            MockCell((0, 0)),
            MockCell((2, 2)),
            MockCell((3, 3)),
        ]

        output = tracking_utils.link_cell(parent_cell, curr_frame_cells)
        
        self.assertEqual(len(output), 2)  # should contain two cells
        self.assertIn(curr_frame_cells[0], output)  # closest cell should be in the output
        self.assertIn(curr_frame_cells[1], output)  # second closest cell should be in the output

    def test_link_cell_two_equidistant_cells(self):
            # Create dummy cells for testing
            class MockCell:
                def __init__(self, coords):
                    self.coords = [coords]

                def get_most_recent_coord(self):
                    return self.coords[-1]

            parent_cell = MockCell((0, 0))
            curr_frame_cells = [
                MockCell((1, 1)),
                MockCell((2, 2)),
                MockCell((-2, -2)),
            ]

            output = tracking_utils.link_cell(parent_cell, curr_frame_cells)
            
            self.assertEqual(len(output), 2)  # should contain two cells
            self.assertIn(curr_frame_cells[0], output)  # closest cell should be in the output
            self.assertIn(curr_frame_cells[1], output)  # will automatically take first closestcell it finds if two are equidistant

    def test_link_cell_no_movement_from_image(self):
        master_cells = tracking_utils.do_watershed(cv2.imread("test/data/test_image_9cells.png"))
        curr_frame_cells = master_cells
        r = tracking_utils.link_cell(master_cells[0], curr_frame_cells)
        self.assertEqual(len(r), 2)
        self.assertIn(curr_frame_cells[0], r)  # original cell should be in the output

    # def test_check_unique(self):
    #     """
    #     Checks if any cells share a position in the most recent frame,
    #     and returns a dictionary of cells with shared positions, where
    #     the key is the cell and the value is the position.
        
    #     Args:
    #         cell_list:

    #     Returns:
    #         non_unique_cells:
    #     """
    #     non_uniques = {}
    #     positions_dict = {}
    #     for curr_cell in cell_list:
    #         # extract position
    #         curr_position = curr_cell.get_most_recent_coord()
    #         # if position is already in list, add both cells to non_unique list
    #         for comparison_cell in positions_dict:
    #             comparison_position = positions_dict[comparison_cell]
    #             if curr_position == comparison_position:
    #                 non_uniques[curr_cell] = curr_position
    #                 # check if comparison cell is already in non_uniques
    #                 not_in_dict = True
    #                 for non_unique_cell in non_uniques:
    #                     if non_unique_cell == comparison_cell:
    #                         not_in_dict = False
    #                         break
    #                 # if cell is not already in non_unique list, add it
    #                 if not_in_dict:
    #                     non_uniques[comparison_cell] = comparison_position
    #         # add to positions list
    #         positions_dict[curr_cell] = curr_position
                        
    #     return non_uniques


def main():
    unittest.main()


if __name__ == '__main__':
    main()
