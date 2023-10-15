class Cell:
    def __init__(self, coords=None, contours=None, parent=None, children=None):
        if coords is None:
            coords = []
        if contours is None:
            contours = []
        if children is None:
            children = []
        self.coords = coords
        self.contours = contours
        self.parent = parent
        self.children = children


    def add_coordinate(self, coord):
        self.coords.append(coord)

    def add_contour(self, contour):
        self.contours.append(contour)
    
    def add_child(self, child):
        self.children.append(child)
    
    def add_parent(self, p):
        self.parent = p

    def get_most_recent_coord(self):
        most_recent_coord = self.coords[len(self.coords)-1]
        return most_recent_coord

    def __str__(self):
        return f"Cell: Coords={self.coords}, Num Contours={len(self.contours)}"
