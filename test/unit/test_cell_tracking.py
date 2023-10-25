import sys

sys.path.insert(0,'src/') # noqa

import cell_tracking_OO_KB_testing
import unittest
import numpy as np
import random
import cv2
import os
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
        r = cell_tracking_OO_KB_testing.get_center(test_contour)
        self.assertEqual(len(r), 2)

    def test_get_center_square_contour(self):
        test_contour = (np.array([[[1, 1]], [[1, 5]], [[5, 5]], [[5, 1]]]))
        r = cell_tracking_OO_KB_testing.get_center(test_contour)
        a = (3,3)
        self.assertEqual(a, r)

    def test_get_center_divide_by_zero(self):
        zero_contour = (np.array([[[0, 0]], [[0, 0]], [[0, 0]],
                               [[0, 0]], [[0, 0]], [[0, 0]],
                               [[0, 0]], [[0, 0]], [[0, 0]],
                               [[0, 0]], [[0, 0]], [[0, 0]]]))
        r = cell_tracking_OO_KB_testing.get_center(zero_contour)
        a = (0,0)
        self.assertEqual(a, r)
    
    # testing is_pixel_inside_contour()
    def test_is_pixel_inside_contour_false(self):
        test_contour = (np.array([[[1, 1]], [[1, 5]], [[5, 5]], [[5, 1]]]))
        r = cell_tracking_OO_KB_testing.is_pixel_inside_contour((6,6), test_contour)
        self.assertEqual(False, r)

    def test_is_pixel_inside_contour_true(self):
        test_contour = (np.array([[[1, 1]], [[1, 5]], [[5, 5]], [[5, 1]]]))
        r = cell_tracking_OO_KB_testing.is_pixel_inside_contour((2,2), test_contour)
        self.assertEqual(True, r)

    def test_is_pixel_inside_contour_zero_contour(self):
        zero_contour = (np.array([[[0, 0]], [[0, 0]], [[0, 0]],
                               [[0, 0]], [[0, 0]], [[0, 0]],
                               [[0, 0]], [[0, 0]], [[0, 0]],
                               [[0, 0]], [[0, 0]], [[0, 0]]]))
        r = cell_tracking_OO_KB_testing.is_pixel_inside_contour((2,2), zero_contour)
        self.assertEqual(False, r)

    # testing dis_between_points()
    def test_dist_between_points(self):
        rand = random.randint(1, 100)
        r = cell_tracking_OO_KB_testing.dist_between_points((0,0),(0,rand))
        a = rand
        self.assertEqual(a,r)

    def test_dist_between_points_same_point(self):
        r = cell_tracking_OO_KB_testing.dist_between_points((0,1),(0,1))
        a = 0
        self.assertEqual(a,r)

    def test_dist_between_points_random_points(self):
        g = (random.randint(1, 100), random.randint(1, 100))
        h = (random.randint(1, 100), random.randint(1, 100))
        r = cell_tracking_OO_KB_testing.dist_between_points(g,h)
        a = ((g[0]-h[0])**2 + (g[1]-h[1])**2)**0.5
        self.assertEqual(a,r)

    # testing do_watershed()
    def test_do_watershed_black_image(self):
        img = np.zeros((100, 100, 3), dtype=np.uint8)           
        cells = cell_tracking_OO_KB_testing.do_watershed(img)    
        self.assertIsInstance(cells, list)  # check if the result is a list
        for cell in cells:
            self.assertIsInstance(cell, Cell)  # check if each item in the list is an instance of the Cell class
        self.assertEqual([], cells) # see if list of cells empty for blank image

    def test_do_watershed_test_image(self):
        img = cv2.imread("test/data/test_image.png")         
        cells = cell_tracking_OO_KB_testing.do_watershed(img)    
        self.assertIsInstance(cells, list)  # check if the result is a list
        for cell in cells:
            self.assertIsInstance(cell, Cell)  # check if each item in the list is an instance of the Cell class
        self.assertNotEqual([], cells) # should be cells in this image

    def test_do_watershed_test_image_9cells(self):
        img = cv2.imread("test/data/test_image_9cells.png")         
        cells = cell_tracking_OO_KB_testing.do_watershed(img)    
        self.assertIsInstance(cells, list)  # check if the result is a list
        for cell in cells:
            self.assertIsInstance(cell, Cell)  # check if each item in the list is an instance of the Cell class
        self.assertEqual(len(cells), 9) # count number of cells in image

    def test_do_watershed_test_image_varied_size_brightness(self): # CURRENTLY FAILS
        img = cv2.imread("test/data/test_image_varied_size_brightness_15.png")         
        cells = cell_tracking_OO_KB_testing.do_watershed(img)    
        self.assertIsInstance(cells, list)  # check if the result is a list
        for cell in cells:
            self.assertIsInstance(cell, Cell)  # check if each item in the list is an instance of the Cell class
        self.assertEqual(len(cells), 15) # count number of cells in image (program found 9)

    def test_do_watershed_test_image_some_overlap(self): # CURRENTLY FAILS
        img = cv2.imread("test/data/test_image_some_overlap_28.png")         
        cells = cell_tracking_OO_KB_testing.do_watershed(img)    
        self.assertIsInstance(cells, list)  # check if the result is a list
        for cell in cells:
            self.assertIsInstance(cell, Cell)  # check if each item in the list is an instance of the Cell class
        self.assertEqual(len(cells), 28) # count number of cells in image (program found 23)

if __name__ == '__main__':
    unittest.main()


def main():
    unittest.main()


if __name__ == '__main__':
    main()
