import sys

sys.path.insert(0, 'src/')  # noqa

import tracking_utils
import unittest
import read_nd2
import numpy as np
import random
import cv2
import tifffile
# import os
from cell import Cell


class TestCellTracking(unittest.TestCase):
    # def test_readND2(self):
    #     movie = read_nd2.read_nd2("test/data/WellD01_ChannelmIFP,mCherry,YFP_Seq0000.nd2")
    #     site0 = read_nd2.get_site_data(movie, 0)
    #     frame0_nuc_channel = read_nd2.get_channel_rawData(movie, 0, 0, 0)

    #     self.assertEqual(len(site0), 6)
    #     self.assertEqual(frame0_nuc_channel.shape, (2048, 2044))

    # def test_readND2_bad_access(self):
    #     movie = read_nd2.read_nd2("test/data/WellD01_ChannelmIFP,mCherry,YFP_Seq0000.nd2")
    #     with self.assertRaises(KeyError):
    #         read_nd2.get_site_data(movie, 2)
    #     with self.assertRaises(IndexError):
    #         read_nd2.get_channel_rawData(movie, 0, 0, 3)

    # def test_readND2_bad_file(self):
    #     with self.assertRaises(read_nd2.nd2reader.exceptions.InvalidFileType):
    #         read_nd2.read_nd2("test/data/WellD01_ChannelmIFP,mCherry,YFP_Seq0000.nd")

    #     with self.assertRaises(FileNotFoundError):
    #         read_nd2.read_nd2("test/data/fake.nd2")


    # testing get_center()
    def test_get_center_output_type(self):
        test_contour = (np.array([[[1297, 2030]], [[1296, 2031]],
                                  [[1294, 2031]], [[1293, 2032]],
                                  [[1291, 2032]], [[1290, 2033]],
                                  [[1289, 2033]], [[1288, 2032]],
                                  [[1287, 2033]], [[1281, 2033]],
                                  [[1280, 2032]], [[1279, 2033]],
                                  [[1278, 2032]], [[1277, 2033]],
                                  [[1276, 2033]], [[1273, 2036]],
                                  [[1272, 2035]], [[1271, 2036]],
                                  [[1270, 2036]], [[1269, 2037]],
                                  [[1268, 2037]], [[1267, 2038]],
                                  [[1266, 2038]], [[1265, 2039]],
                                  [[1264, 2039]], [[1265, 2040]],
                                  [[1264, 2041]], [[1264, 2042]],
                                  [[1261, 2045]], [[1259, 2045]],
                                  [[1259, 2046]], [[1302, 2046]],
                                  [[1304, 2044]], [[1304, 2043]],
                                  [[1307, 2040]], [[1306, 2039]],
                                  [[1306, 2038]], [[1305, 2037]],
                                  [[1305, 2036]], [[1304, 2035]],
                                  [[1304, 2034]], [[1303, 2033]],
                                  [[1302, 2033]], [[1300, 2031]],
                                  [[1298, 2031]]]))
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
        r = tracking_utils.dist_between_points((0, 0), (0, rand))
        a = rand
        self.assertEqual(a, r)

    def test_dist_between_points_same_point(self):
        r = tracking_utils.dist_between_points((0, 1), (0, 1))
        a = 0
        self.assertEqual(a, r)

    def test_dist_between_points_random_points(self):
        g = (random.randint(1, 100), random.randint(1, 100))
        h = (random.randint(1, 100), random.randint(1, 100))
        r = tracking_utils.dist_between_points(g, h)
        a = ((g[0]-h[0])**2 + (g[1]-h[1])**2)**0.5
        self.assertEqual(a, r)

    # testing do_watershed()
    def test_do_watershed_black_image(self):
        img = np.zeros((100, 100, 3), dtype=np.uint8)
        cells = tracking_utils.do_watershed(img)
        self.assertIsInstance(cells, list)  # check if the result is a list
        for cell in cells:
            # check if each item in the list is an instance of the Cell class
            self.assertIsInstance(cell, Cell)
        # see if list of cells empty for blank image
        self.assertEqual([], cells)

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

    def test_do_watershed_test_image_varied_size_brightness(self):
        img = cv2.imread("test/data/test_image_varied_size_brightness_15.png")
        cells = tracking_utils.do_watershed(img)
        self.assertIsInstance(cells, list)
        for cell in cells:
            self.assertIsInstance(cell, Cell)
        self.assertLess(len(cells), 15)  # count number of cells in image

    def test_do_watershed_test_image_some_overlap(self):
        img = cv2.imread("test/data/test_image_some_overlap_28.png")
        cells = tracking_utils.do_watershed(img)
        self.assertIsInstance(cells, list)
        for cell in cells:
            self.assertIsInstance(cell, Cell)
        self.assertLess(len(cells), 28)  # count number of cells in image

    # testing resolve_child_conflicts()
    def test_resolve_child_conflicts_empty_candidates(self):
        candidates = []
        resolved_tracks = tracking_utils.resolve_child_conflicts(candidates, 50)
        for cell in resolved_tracks:
            for i in cell:
                self.assertIsInstance(i, Cell)

    def test_resolve_child_conflicts_no_conflicts(self):
        # # make synthetic cell list to test on
        candidates = []
        cell_1 = Cell()
        cell_2 = Cell()
        cell_3 = Cell()
        cell_4 = Cell()
        # candidates is a numpy array of dictionaries,
        # keys are the cell objects, there are two,
        # the first is the most likely cell, the second is the child cell

        candidates = [{cell_1: 2, cell_4: 10}, {cell_2: 3, cell_3: 5}]
        resolved_tracks = tracking_utils.resolve_child_conflicts(candidates, 50)
        for cell in resolved_tracks:
            for i in cell:
                self.assertIsInstance(i, Cell)
        expected_output = [[cell_1, cell_4], [cell_2, cell_3]]

        self.assertEqual(expected_output[0][0], resolved_tracks[0][0])
        self.assertEqual(expected_output[1][0], resolved_tracks[1][0])

    def test_resolve_child_conflicts_with_shared_child(self):
        # test for if two share a child but one is closer
        candidates = []
        cell_1 = Cell()
        cell_2 = Cell()
        cell_3 = Cell()
        # candidates is a numpy array of dictionaries,
        # keys are the cell objects, there are two,
        # the first is the most likely cell, the second is the child cell

        candidates = [{cell_1: 2, cell_3: 10}, {cell_2: 3, cell_3: 5}]
        resolved_tracks = tracking_utils.resolve_child_conflicts(candidates, 50)
        for cell in resolved_tracks:
            for i in cell:
                self.assertIsInstance(i, Cell)
        expected_output = [[cell_1], [cell_2, cell_3]]
        self.assertEqual(expected_output[0][0], resolved_tracks[0][0])
        self.assertEqual(expected_output[1][0], resolved_tracks[1][0])

    def test_resolve_child_conflicts_with_potential_child_already_cell(self):
        candidates = []
        cell_1 = Cell()
        cell_2 = Cell()
        cell_3 = Cell()
        # candidates is a numpy array of dictionaries,
        # keys are the cell objects, there are two,
        # the first is the most likely cell, the second is the child cell

        # dictionary with key as cell object, value as distance
        # from potential parent in previous frame
        candidates = [{cell_1: 2, cell_2: 10}, {cell_2: 3, cell_3: 5}]
        resolved_tracks = tracking_utils.resolve_child_conflicts(candidates, 50)
        for cell in resolved_tracks:
            for i in cell:
                self.assertIsInstance(i, Cell)
        expected_output = [[cell_1], [cell_2, cell_3]]
        self.assertEqual(expected_output[0][0], resolved_tracks[0][0])
        self.assertEqual(expected_output[1][0], resolved_tracks[1][0])

    def test_resolve_child_conflicts_with_same_child_same_dist(self): # this should pass once pull new changes
        candidates = []
        cell_1 = Cell()
        cell_2 = Cell()
        cell_3 = Cell()
        # candidates is a numpy array of dictionaries,
        # keys are the cell objects, there are two,
        # the first is the most likely cell, the second is the child cell
        candidates = [{cell_1: 2, cell_3: 5}, {cell_2: 3, cell_3: 5}]
        # dictionary with key as cell object, value as distance
        # from potential parent in previous frame
        resolved_tracks = tracking_utils.resolve_child_conflicts(candidates, 50)
        for cell in resolved_tracks:
            for i in cell:
                self.assertIsInstance(i, Cell)
        # child should go to neither if distance is equal
        expected_output = [[cell_1], [cell_2]]
        self.assertEqual(expected_output[0][0], resolved_tracks[0][0])
        self.assertEqual(expected_output[1][0], resolved_tracks[1][0])

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
        # closest cell should be in the output
        self.assertIn(curr_frame_cells[0], output)
        # second closest cell should be in the output
        self.assertIn(curr_frame_cells[1], output)

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
        # closest cell should be in the output
        self.assertIn(curr_frame_cells[0], output)
        # second closest cell should be in the output
        self.assertIn(curr_frame_cells[1], output)

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
        # closest cell should be in the output
        self.assertIn(curr_frame_cells[0], output)
        # will automatically take first closest cell if two are equidistant
        self.assertIn(curr_frame_cells[1], output)

    def test_link_cell_no_movement_from_image(self):
        master_cells = tracking_utils.do_watershed(cv2.imread("test/data/test_image_9cells.png"))
        curr_frame_cells = master_cells
        r = tracking_utils.link_cell(master_cells[0], curr_frame_cells)
        self.assertEqual(len(r), 2)
        # original cell should be in the output
        self.assertIn(curr_frame_cells[0], r)

    # test get_cells_to_cull()
    def test_get_cells_to_cull(self):
        # make synthetic cell list to test on
        test_cell_list = []
        test_positions = [(10, 10), (2, 5), (100, 7),
                          (100, 7), (10, 10), (55, 55)]
        test_previous_positions = [(9, 9), (3, 5), (150, 70),
                                   (90, 8), (11, 11), (54, 60)]
        for i in range(6):
            test_cell = Cell()
            test_cell.add_coordinate(test_previous_positions[i])
            test_cell.add_coordinate(test_positions[i])
            test_cell_list.append(test_cell)

        # expected output
        output = [[(9, 9), (10, 10)], [(150, 70), (100, 7)]]

        # test get_cells_to_cull function
        to_cull_list = tracking_utils.get_cells_to_cull(test_cell_list, 100)
        for item in to_cull_list:
            self.assertIn(item.coords, output)

    def test_get_cells_to_cull_no_duplicates(self):
        # make synthetic cell list to test on
        test_cell_list = []
        test_positions = [(10, 11), (2, 5), (100, 9),
                          (100, 7), (10, 10), (55, 55)]
        test_previous_positions = [(9, 9), (3, 5), (150, 70),
                                   (90, 8), (11, 11), (54, 60)]
        for i in range(6):
            test_cell = Cell()
            test_cell.add_coordinate(test_previous_positions[i])
            test_cell.add_coordinate(test_positions[i])
            test_cell_list.append(test_cell)

        # expected output
        output = []

        # test get_cells_to_cull function
        to_cull_list = tracking_utils.get_cells_to_cull(test_cell_list, 100)
        for item in to_cull_list:
            self.assertIn(item.coords, output)

    # test cull_duplicates()
    def test_cull_duplicates_no_histories(self):
        # make synthetic cell list to test on
        test_cell_list = []
        test_positions = [(10, 11), (2, 5)]
        for i in range(2):
            test_cell = Cell()
            test_cell.add_coordinate(test_positions[i])
            test_cell_list.append(test_cell)
        # list of one of the cells to be culled
        to_cull_cell_list = []
        to_cull_cell_list.append(test_cell_list[0])

        # test culling function
        not_culled_list = tracking_utils.cull_duplicates(test_cell_list, to_cull_cell_list)
        self.assertEqual(test_cell_list[1], not_culled_list[0])

    def test_cull_duplicates_more_complex(self):
        # make synthetic cell list to test on
        test_cell_list = []
        test_positions = [(10, 10), (2, 5), (100, 7),
                          (100, 7), (10, 10), (55, 55)]
        test_previous_positions = [(9, 9), (3, 5), (150, 70),
                                   (90, 8), (11, 11), (54, 60)]
        for i in range(6):
            test_cell = Cell()
            test_cell.add_coordinate(test_previous_positions[i])
            test_cell.add_coordinate(test_positions[i])
            test_cell_list.append(test_cell)

        # cells to be culled
        to_cull_cell_list = []
        to_cull_cell_list.append(test_cell_list[0])
        to_cull_cell_list.append(test_cell_list[2])   

        # expected output
        output = [[(54, 60), (55, 55)],
                  [(90, 8), (100, 7)],
                  [(11, 11), (10, 10)],
                  [(3, 5), (2, 5)]]

        # test culling function
        not_culled_list = tracking_utils.cull_duplicates(test_cell_list, to_cull_cell_list)
        for item in not_culled_list:
            self.assertIn(item.coords, output)

    def test_cull_duplicates_no_duplicates(self):
        # make synthetic cell list to test on
        test_cell_list = []
        test_positions = [(10, 11), (2, 5), (100, 9),
                          (100, 7), (10, 10), (55, 55)]
        test_previous_positions = [(9, 9), (3, 5), (150, 70),
                                   (90, 8), (11, 11), (54, 60)]
        for i in range(6):
            test_cell = Cell()
            test_cell.add_coordinate(test_previous_positions[i])
            test_cell.add_coordinate(test_positions[i])
            test_cell_list.append(test_cell)

        # expected output
        output = [[(54, 60), (55, 55)],
                  [(90, 8), (100, 7)],
                  [(11, 11), (10, 10)],
                  [(3, 5), (2, 5)],
                  [(9, 9), (10, 11)],
                  [(150, 70), (100, 9)]]

        # test culling function
        not_culled_list = tracking_utils.cull_duplicates(test_cell_list, [])
        for item in not_culled_list:
            self.assertIn(item.coords, output)

    # test link_next_frame()
    def test_link_next_frame_same_image(self):
        image = tifffile.imread("test/data/test_frame_4_cells.tif")
        master_cells = tracking_utils.do_watershed(image)
        curr_frame = image
        orig_cell_coords = []
        for cell in master_cells:
            for coords in cell.coords:
                x = coords[0]
                y = coords[1]
                coord = [(x, y)]
            orig_cell_coords.append(coord)
        output = tracking_utils.link_next_frame(master_cells, curr_frame, 1)
        self.assertEqual(len(output), 4)
        for i, cell in enumerate(output):
            self.assertIsInstance(cell, Cell)
            # all cells should have same location as previous frame
            # because same image
            self.assertEqual(cell.coords[0], orig_cell_coords[i][0])
            self.assertEqual(cell.coords[1], orig_cell_coords[i][0])

    def test_link_next_frame_different_images_movement(self):
        image_1 = tifffile.imread("test/data/test_frame_4_cells.tif")
        image_2 = tifffile.imread("test/data/test_frame_4_cells_movement_v2.tif")
        master_cells = tracking_utils.do_watershed(image_1)
        curr_frame = image_2
        orig_cell_coords = []
        for cell in master_cells:
            for coords in cell.coords:
                x = coords[0]
                y = coords[1]
                coord = [(x, y)]
            orig_cell_coords.append(coord)
        output = tracking_utils.link_next_frame(master_cells, curr_frame, 3)
        # print(output)
        self.assertEqual(len(output), 4)
        for i, cell in enumerate(output):
            self.assertIsInstance(cell, Cell)
            # previous frame in output should be same as image_1 current frame
            self.assertEqual(cell.coords[0], orig_cell_coords[i][0])
            # cells will now have moved
            self.assertNotEqual(cell.coords, orig_cell_coords[i])

    def test_link_next_frame_different_images_new_cell(self):
        image_1 = tifffile.imread("test/data/test_frame_4_cells.tif")
        image_2 = tifffile.imread("test/data/test_frame_5_cells_v2.tif")
        master_cells = tracking_utils.do_watershed(image_1)
        curr_frame = image_2
        orig_cell_coords = []
        for cell in master_cells:
            for coords in cell.coords:
                x = coords[0]
                y = coords[1]
                coord = (x, y)
            orig_cell_coords.append(coord)
        # print("original:", orig_cell_coords)
        output = tracking_utils.link_next_frame(master_cells, curr_frame, 3)
        # print("output:")
        # print(output)
        # self.assertEqual(len(output), 5)  # should now be 5 tracked cells
        for i, cell in enumerate(output):
            self.assertIsInstance(cell, Cell)
            # previous frame in output should be same as image_1 current frame
            self.assertIn(cell.coords[0], orig_cell_coords)
            # cells will now have moved
            # print(cell.coords)
            self.assertNotIn(cell.coords[1], orig_cell_coords)


def main():
    unittest.main()


if __name__ == '__main__':
    main()
