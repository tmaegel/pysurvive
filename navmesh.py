import triangle as tr


class NavMesh():

    """
    This NavMesh class create a navmesh (division of the
    walkable game world into triangles).
    Based on this navmesh AI can find paths through the
    game world to the destination (e.g. player).
    """

    mesh = []

    def __init__(self, _game):
        self.game = _game
        self.mesh = self._init_navmesh()

    def _init_navmesh(self, _offset=15):
        doors = []
        vertices = []
        segments = []
        holes = []

        def make_box(x, y, w, h):
            i = len(vertices)
            # 2d array that stores the xy position of each vertex.
            vertices.extend([[x, y],
                             [x + w, y],
                             [x + w, y + h],
                             [x, y + h]])
            # 2d array that stores segments.
            # egments are edges whose presence in the triangulation
            # is enforced. Each segment is specified by listing the
            # indices of its two endpoints.
            segments.extend([(i+0, i+1),
                             (i+1, i+2),
                             (i+2, i+3),
                             (i+3, i+0)])

        # Add rooms with offset (exlude walls at the sides) from navmesh.
        for room in self.game.room_sprites.sprites():
            make_box(room.x + _offset, room.y + _offset,
                     room.width - _offset * 2, room.height - _offset * 2)
            # Extract the doors of each room.
            # Do not append duplicates.
            for door in room.get_door():
                if door not in doors:
                    doors.append(door)

        # Add doors to navmesh to connect the rooms
        for door in doors:
            make_box(door.x, door.y, door.width, door.height)

        # for block in self.block_sprites.sprites():
        #     make_box(block.x + _offset, block.y + _offset,
        #              block.width - _offset * 2, block.height - _offset * 2)

        block = self.game.block_sprites.sprites()[-1]
        make_box(block.x, block.y, block.width, block.height)
        holes.append(block.get_center())

        A = dict(vertices=vertices, segments=segments, holes=holes)
        B = tr.triangulate(A, 'pA')

        mesh = []
        vertices = B['vertices'].tolist()
        # Create node objects based on the triangulation.
        for triangle in B['triangles'].tolist():
            polygon = []
            for index in triangle:
                point = vertices[index]
                polygon.append((point[0], point[1]))
            mesh.append(Triangle(polygon))

        # Find the neightbor nodes for each node
        for tri in mesh:
            tri.find_neighbors(mesh)

        return mesh

    def get_astar_path(self, start, end):
        """
        Returns a list of tuples as a path from the given start
        to the given end point.
        """

        path = []
        start_node = None
        end_node = None

        open_list = []
        closed_list = []

        # Find the triangles of start and end position.
        for tri in self.mesh:
            if tri.is_point_in_triangle(start):
                start_node = tri.nodes[0]  # Get first node
                break
        for tri in self.mesh:
            if tri.is_point_in_triangle(end):
                end_node = tri.nodes[0]  # Get first node
                break

        # Both point are located on the same triangle
        if start_node is end_node:
            path.append(start)
            path.append(end)
            return path
        # One or both points are outside all triangles
        elif not start_node or not end_node:
            print("warn: start and/or end point are outside of triangle.")
        # Both points are located on different triangles
        else:
            open_list.append(start_node)

            # Loop until you find the end
            while len(open_list) > 0:
                # Get the current node
                current_node = open_list[0]
                current_index = 0

                # To continue the search, simply choose the lowest F
                # score from all those that are on the open list.
                for index, item in enumerate(open_list):
                    if item.f < current_node.f:
                        current_node = item
                        current_index = index

                # Drop the starting node from the open list,
                # and add it to a closed list. We don't need
                # to look at again for now.
                open_list.pop(current_index)
                closed_list.append(current_node)

                # Found the goal
                if current_node == end_node:
                    current = current_node
                    path.append(end)  # Add end position
                    while current is not None:
                        path.append(current.position)
                        current = current.parent
                    path.append(start)  # Add start position
                    return path[::-1]  # Return reversed path

                # Look at all adjacent triangles and its nodes from
                # the current node.
                children = []
                for neighbor in current_node.triangle.neighbors:
                    for node in neighbor.nodes:
                        children.append(node)

                for node in children:
                    # Node is on the closed list
                    if node in closed_list:
                        continue

                    # Create the f, g, and h values
                    node.g = current_node.g + 1
                    node.h = (
                        ((node.position[0] - end_node.position[0]) ** 2)
                        + ((node.position[1] - end_node.position[1]) ** 2))
                    node.f = node.g + node.h

                    # Node is already in the open list
                    for open_node in open_list:
                        if node == open_node and node.g > open_node.g:
                            continue

                    # For each node save the current node as parent.
                    # This parent stuff is important when we want to
                    # trace our path.
                    node.parent = current_node

                    # Add the child to the open list
                    open_list.append(node)


class Node():

    """
    Wrapper class for nodes.

    Based on this class, the total route can be determined later on.
    """

    def __init__(self, _triangle, _parent=None, _position=None):
        # Reference to its parents triangle.
        self.triangle = _triangle
        # For each node save the current node as parent.
        # This parent stuff is important when we want to
        # trace our path.
        self.parent = _parent
        # Node position.
        self.position = _position

        # Trac the movement costs from start or until end position.
        # G is the distance between the current node and the start node.
        self.g = 0
        # H is the heuristic — estimated distance from the current node
        # to the end node.
        self.h = 0
        # F is the total cost of the node.
        self.f = 0

    def __eq__(self, other):
        return self.position == other.position


class Triangle():

    """
    A triangle class for A* pathfinding.

    This class represented a triangle. The node point of this is
    the center of the triangle. Furthermore each triangle
    contains a list with the corresponding adjacent.

    Mutliple triangles and its nodes (center) build the route later.
    """

    def __init__(self, _triangle):
        # List of points of this node / triangle
        self.triangle = _triangle

        self.nodes = self._get_nodes()
        # Center point of this triangle is one possible node
        # self.nodes.append(Node(self, None, self._get_center()))

        # List of adjacent trianles
        self.neighbors = []

    def _get_center(self):
        """
        Get the center point of the triangle.
        """

        # ox = (ax + bx + cx) / 3
        # oy = (ay + by + cy) / 3
        ox = 0
        oy = 0
        for p in self.triangle:
            ox += p[0]
            oy += p[1]

        return (ox//3, oy//3)

    def _get_nodes(self):
        """
        Get all nodes of each triangle.

        A node is on the center of each side. But remove
        all nodes on the side that are adjacent to an obstacle.
        """
        p1 = None
        p2 = None
        nodes = []
        for i in range(len(self.triangle) + 1):
            if i >= len(self.triangle):
                p2 = self.triangle[0]
            else:
                p2 = self.triangle[i]
            if i != 0:
                nodes.append(
                    Node(self, None,
                         ((p2[0] - p1[0])//2 + p1[0],
                          (p2[1] - p1[1])//2 + p1[1])
                         ))
            p1 = p2

        return nodes

    def _remove_invalid_nodes(self, _nodes):
        """
        Remove all nodes on the side that are adjacent
        to an obstacle. If a node is shared by two
        triangle, this is a valid node.
        """

        nodes = []
        for node in self.nodes:
            for n in _nodes:
                if self is not n:
                    if node in n.nodes:
                        nodes.append(node)
                        break
        # Overwrite the nodes
        self.nodes = nodes

    def find_neighbors(self, _nodes):
        """
        Find all neighbor triangles.
        A neighbor is a triangle with 2 common points.
        """

        # Find neighbors
        for node in _nodes:
            common_points = 0
            if self is not node:
                for p in self.triangle:
                    if p in node.triangle:
                        common_points += 1
                    if common_points >= 2:
                        if node not in self.neighbors:
                            self.neighbors.append(node)

        self._remove_invalid_nodes(_nodes)

    def is_point_in_triangle(self, _point):
        """
        Returns True if the point is inside the triangle and returns False
        if it falls outside.

        :param point: is a tuple with two elements containing the
                      x, y coordinates respectively.
        :param triangle: is a tuple with three elements each element
                         consisting of a tuple of x, y coordinates.

        It works like this:
        Walk clockwise or counterclockwise around the triangle and
        project the point onto the segment we are crossing by using
        the dot product. Finally, check that the vector created is
        on the same side for each of the triangle's segments.
        """
        # Unpack arguments
        x, y = _point
        ax, ay = self.triangle[0]
        bx, by = self.triangle[1]
        cx, cy = self.triangle[2]
        # Segment A to B
        side_1 = (x - bx) * (ay - by) - (ax - bx) * (y - by)
        # Segment B to C
        side_2 = (x - cx) * (by - cy) - (bx - cx) * (y - cy)
        # Segment C to A
        side_3 = (x - ax) * (cy - ay) - (cx - ax) * (y - ay)

        # All the signs must be positive or all negative
        return (side_1 < 0.0) == (side_2 < 0.0) == (side_3 < 0.0)