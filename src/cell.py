import numpy as np


class Cell:
    def __init__(self, coords=None, contours=None,
                 parent=None, children=None, birthday=0, problematic=False):
        if coords is None:
            coords = []
        if contours is None:
            contours = []
        if children is None:
            children = []
        self.birthday = birthday
        self.coords = coords
        self.contours = contours
        self.parent = parent
        self.children = children
        self.problematic = problematic

        if self.parent is not None:
            history_length = len(parent.coords)
            backfill = [(-1, -1) for _ in range(history_length)]
            self.coords = backfill

    def add_coordinate(self, coord):
        self.coords.append(coord)

    def add_contour(self, contour):
        self.contours.append(contour)

    def add_child(self, child):
        self.children.append(child)

    def add_parent(self, p):
        self.parent = p

    def get_most_recent_coord(self):
        try:
            most_recent_coord = self.coords[len(self.coords)-1]
            return most_recent_coord
        except IndexError:
            print("IndexError: No coordinates found for this cell")
            raise IndexError

    def make_problematic_cell(self):
        self.problematic = True

    def make_unproblematic_cell(self):
        self.problematic = False

    def __str__(self):
        return f"Cell: Coords={self.coords}, Num Contours={len(self.contours)}"
