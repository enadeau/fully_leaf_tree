from collections import deque
import heapq

class InducedSubtreeConfiguration(object):
    r"""
    Vertex status
    """
    INCLUDED = 0 # The vertex is included
    EXCLUDED = 1 # The vertex is excluded
    BORDER = 2   # The vertex is on the border
    NOT_SEEN = 3 # The vertex has not been discovered yet

    r"""
    A configuration of an induced subtree for a fixed graph.

    This object is used for facilitating the enumeration of all induced
    subtrees of a graph. It offers basic operations, such as forcing the
    inclusion or exclusion of a fixed vertex in the subtree.

    We say that a vertex ``v`` is in the *border* if it is not included, not
    excluded and adjacent to exactly one included vertex.

    ATTRIBUTES:

    - ``graph``: The graph in which the configuration lives.

    - ``subtree_vertices``: The vertices that are in the subtree.

    - ``subtree_size``: The number of vertices in the subtree (included)

    - ``num_leaf``: The number of leaves of the subtree.

    - ``num_excluded: The number of vertices that are rejected

    - ``border_size``: The number of vertices in the border

    - ``vertex_status``: A dictionary that store the state of each vertex. The
      status of a vertex ``v`` is of one of the following forms:

      * ``(INCLUDED, d)`` if ``v`` is in the subtree and has degree ``d`` in
        the subtree;
      * ``(EXCLUDED, u)`` if ``v`` is excluded from the subtree, where ``u`` is
        the vertex that caused the exclusion of ``v``. In particular, if ``u ==
        v``, then it means that the vertex was manually excluded by a call to
        the function ``exclude_vertex(v)``.
      * ``(BORDER, u)`` if ``v`` is not in the subtree and is adjacent to
        exactly one vertex of the subtree which is ``u``;
      * ``(NOT_SEEN, None)`` otherwise. This means that ``v`` is not included,
        not excluded and is not adjacent to another included vertex.

    - ``history``: A stack of vertices, in the order according to which they
      have been manually included or manually excluded.

    - ``upper_bound_strategy``: The strategy chosen for computing the leaf
      potential. The leaf potential is an upper bound on the number of leaves
      that any extension of the current configuration could have. Currently,
      the available strategies are either 'naive' or 'dist'.

    - ``lp_dist_dict``: A dictionary indicating all possible leaf potentials
      for the `dist` strategy.

    - ``lp_dist_valid``: A boolean indicating if the structure has changed
      since the last computation of ``lp_dist_dict``.

    - ``border_vertex``: A candidate border vertex.
    """

    def __init__(self, G, upper_bound_strategy = 'dist'):
        r"""
        Constructor of the graph border. Initialize the state of all vertices
        to ("a", None)

        INPUT:
            G - The graph
            upper_bound_strategy - The strategy for the leaf potential (either
                'naive' or 'dist')
        """
        self.graph = G
        self.subtree_vertices = []
        self.subtree_size = 0
        self.num_leaf = 0
        self.num_excluded = 0
        self.border_size = 0
        self.vertex_status = dict()
        for v in G.vertex_iterator():
            self.vertex_status[v] = (InducedSubtreeConfiguration.NOT_SEEN, None)
        self.history = []
        assert upper_bound_strategy in ['naive', 'dist']
        self.upper_bound_strategy = upper_bound_strategy
        self.lp_dist_valid = False
        self.border_vertex = v

    def vertex_to_add(self):
        r"""
        Return a vertex of the graph that can extend the current solution into a
        tree. If the subtree is empty, it's any non-rejected vertex. If the
        current solution can't be extend returns None. Otherwise, return a
        border vertex.
        """
        if self.vertex_status[self.border_vertex][0] == InducedSubtreeConfiguration.BORDER:
            return self.border_vertex
        elif self.subtree_size == 0:
            #The subtree is empty, any non rejected vertex can be add
            for v in self.vertex_status:
                if self.vertex_status[v][0] == InducedSubtreeConfiguration.NOT_SEEN:
                    return v
        else:
            #The subtree is not empty, a vertex of the border must be add
            for v in self.vertex_status:
                if self.vertex_status[v][0] == InducedSubtreeConfiguration.BORDER:
                    return v
        return None

    def add_to_subtree(self, v):
        r"""
        Add a vertex of the border to the current solution or initiate a
        solution with a first vertex.

        INPUT:
            v - A vertex of the border or if the subtree is empty any available
                vertex

        OUTPUT:
            Degree of the parent of v after the addition
        """
        assert self.vertex_status[v][0] == InducedSubtreeConfiguration.BORDER or (InducedSubtreeConfiguration.BORDER, None) not in \
                self.vertex_status.values(), "Invalid vertex to add"
        degree = 0
        for u in self.graph.neighbor_iterator(v):
            (state, info) = self.vertex_status[u]
            if state == InducedSubtreeConfiguration.NOT_SEEN:
                self.vertex_status[u] = (InducedSubtreeConfiguration.BORDER, None)
                self.border_size += 1
            elif state == InducedSubtreeConfiguration.INCLUDED:
                degree = info + 1
                self.vertex_status[u] = (state, degree)
                if info == 1:
                    self.num_leaf -= 1
            elif state == InducedSubtreeConfiguration.BORDER:
                self.border_size -= 1
                self.num_excluded += 1
                self.vertex_status[u] = (InducedSubtreeConfiguration.EXCLUDED, v)
            #If the vertices is already rejected we do nothing
        if self.vertex_status[v][0] == InducedSubtreeConfiguration.BORDER:
            #The vertex extend a current solution
            self.vertex_status[v] = (InducedSubtreeConfiguration.INCLUDED, 1)
            self.border_size -= 1
        else:
            #The vertex is the first vertex to be set to INCLUDED
            self.vertex_status[v] = (InducedSubtreeConfiguration.INCLUDED, 0)
        self.subtree_vertices.append(v)
        self.num_leaf += 1
        self.subtree_size += 1
        self.history.append(v)
        self.lp_dist_valid = False
        return degree

    def _remove_last_addition(self, v):
        r"""
        Reverts the last addition process. v must be the last added vertex and
        the addition must be the last modification to the structure.
        """
        for u in self.graph.neighbor_iterator(v):
            (state, info) = self.vertex_status[u]
            #Impossible that state is available
            if state == InducedSubtreeConfiguration.BORDER:
                self.vertex_status[u] = (InducedSubtreeConfiguration.NOT_SEEN, None)
                self.border_size -= 1
            elif state == InducedSubtreeConfiguration.INCLUDED:
                self.vertex_status[u] = (state, info - 1)
                if info == 2:
                    self.num_leaf += 1
            #At this point the state must be EXCLUDED
            elif info == v:
                self.vertex_status[u] = (InducedSubtreeConfiguration.BORDER, None)
                self.num_excluded -= 1
                self.border_size += 1
        self.subtree_size -= 1
        if self.subtree_size > 0:
            self.vertex_status[v] = (InducedSubtreeConfiguration.BORDER, None)
            self.border_size += 1
        else: #We remove the last vertex from the subtree
            self.vertex_status[v] = (InducedSubtreeConfiguration.NOT_SEEN, None)
        self.num_leaf -= 1
        self.subtree_vertices.pop()

    def exclude_vertex(self, v):
        r"""
        Sets a vertex that is not in the solution to rejected.
        When a vertex v has been rejected using this method,
        his value in vertex_status is set to (EXCLUDED,v)
        """
        assert self.vertex_status[v][0] == InducedSubtreeConfiguration.BORDER or self.subtree_size == 0
        self.vertex_status[v] = (InducedSubtreeConfiguration.EXCLUDED, v)
        if self.subtree_size != 0:
            #The element we reject is on the border
            self.border_size -= 1
        self.num_excluded += 1
        self.history.append(v)
        self.lp_dist_valid = False

    def _unreject_last_manual_rejection(self, v):
        r"""
        Reverts the last manual rejection. v must be the last rejected vertex
        and the rejection must be the last modification to the structure.
        """
        self.num_excluded -= 1
        if self.subtree_size == 0:
            self.vertex_status[v] = (InducedSubtreeConfiguration.NOT_SEEN, None)
        else:
            self.vertex_status[v] = (InducedSubtreeConfiguration.BORDER, None)
            self.border_size += 1

    def undo_last_user_action(self):
        r"""
        Undo the last user intervention which is either and addition to the
        subtree or a rejection.
        """
        v = self.history.pop()
        self.lp_dist_valid = False
        if self.vertex_status[v][0] == InducedSubtreeConfiguration.INCLUDED:
            self._remove_last_addition(v)
        else:
            self._unreject_last_manual_rejection(v)

    def subtree_num_leaf(self):
        r"""
        Return the number of leaf in the subtree
        """
        if self.subtree_size == 1:
            return 0
        else:
            return self.num_leaf

    def subtree_vertices_with_degrees(self):
        r"""
        Generates the subtree vertices with their degrees
        in pair (vertex, degree)
        """
        for v in self.subtree_vertices:
            yield (v, self.vertex_status[v][1])

    def degree(self, u, exclude=EXCLUDED):
        r"""
        Compute the degree of the vertices u in the graph border excluding
        vertices with state in exlcude. Default value for exclude is EXCLUDED
        """
        return sum(1 for v in self.graph.neighbor_iterator(u)
                     if self.vertex_status[v][0] not in exclude)

    def non_rejected_vertices_by_distance_with_degree(self):
        r"""
        Return a partition of the vertices that are not rejected with
        respect to their distance from the subtree internal vertices.

        The first layer is distance 1 which are the leaves of the subtree and
        the yellow vertices connected to inner vertices.

        The partition contains pairs (u, d) where u is the vertex
        and d the degree of the u. The degree doesn't count rejected vertex.
        """
        assert self.subtree_size>2, "No inner vertices in the green tree"
        vertices = []
        visited = set()
        queue = deque()
        #Add inner vertices to the queue
        queue.extend(((u, 0) for u in self.subtree_vertices\
                if self.vertex_status[u][1]>1))
        layer = []
        prev_dist = 0
        while queue:
            (v, dist) = queue.popleft()
            if v not in visited:
                visited.add(v)
                if prev_dist < dist:
                    if prev_dist > 0:
                        vertices.append(layer)
                    layer = []
                degree = 0
                for u in self.graph.neighbor_iterator(v):
                    if self.vertex_status[u][0] != InducedSubtreeConfiguration.EXCLUDED:
                        degree += 1
                        if u not in visited:
                            queue.append((u, dist+1))
                layer.append((v, degree))
                prev_dist = dist
        vertices.append(layer)
        return vertices

    def non_subtree_vertices_by_distance(self):
        r"""
        Returns a partition of the non subtree vertices with respect to their
        distance from the subtree internal vertices.
        """
        vertices = []
        visited = set()
        queue = deque()
        leaves = []
        for (u,d) in self.subtree_vertices_with_degrees():
            if d > 1: queue.append((u,0))
            elif d == 1: leaves.append((u,1))
        queue.extend(leaves)
        #This if is used to speed up vertex_to_add
        if queue:
            self.border_vertex = queue[0][0]
        layer = []
        prev_d = 0
        while queue:
            (u, d) = queue.popleft()
            if u not in visited:
                if 1 <= prev_d and prev_d < d:
                    vertices.append(layer)
                    layer = []
                if self.vertex_status[u][0] != InducedSubtreeConfiguration.INCLUDED:
                    layer.append(u)
                prev_d = d
                visited.add(u)
                for v in self.graph.neighbor_iterator(u):
                    if self.vertex_status[v][0] != InducedSubtreeConfiguration.EXCLUDED and not v in visited:
                        queue.append((v,d+1))
        vertices.append(layer)
        return vertices

    def _max_degree(self, d):
        r"""
        Return d since nothing bound the degree  of a vertices in the subtree.
        This method is itended to be redefine when useful
        """
        return d

    def leaf_potential_dist(self,i):
        r"""
        Compute an upper bound on the number of leaves that an extension of self
        to i green vertices can reach.

        Better bound then leaf_potential_weak but it takes more time to compute.
        """
        assert self.subtree_size > 2
        if self.lp_dist_valid:
            if self.lp_dist_dict.has_key(i):
                return self.lp_dist_dict[i]
            else:
                return 0
        #Else we compute the dictionnary
        current_size = self.subtree_size
        current_leaf = self.num_leaf
        self.lp_dist_dict = dict()
        self.lp_dist_dict[current_size] = current_leaf
        vertices_by_dist = self.non_rejected_vertices_by_distance_with_degree()
        #Adding the leaf creator
        for (v, d) in vertices_by_dist[0]:
            if self.vertex_status[v][0] == InducedSubtreeConfiguration.BORDER:
                current_size += 1
                current_leaf += 1
                self.lp_dist_dict[current_size] = current_leaf
        max_size = current_size + sum(len(layer) for layer in vertices_by_dist[1:])
        current_dist = 1
        priority_queue = [(-d, u) for (u, d) in vertices_by_dist[0] if d > 1]
        heapq.heapify(priority_queue)
        while current_size < max_size and priority_queue:
            (d, u) = heapq.heappop(priority_queue)
            degree = -d
            if current_dist < len(vertices_by_dist):
                for (v, d) in vertices_by_dist[current_dist]:
                    if d > 1:
                        heapq.heappush(priority_queue, (-d, v))
                current_dist += 1
            current_leaf -= 1
            leaf_to_add = min(self._max_degree(degree)-1, max_size-current_size)
            for _ in range(leaf_to_add):
                current_size += 1
                current_leaf += 1
                self.lp_dist_dict[current_size] = current_leaf
        self.lp_dist_valid = True
        return self.leaf_potential_dist(i)

    def leaf_potential_weak(self,i):
        r"""
        Evaluate a maximal potential number of leaf for a subtree of i
        vertices build from the current subtree.

        The size of the tree must be bigger than the current tree size.
        """
        if self.subtree_size <= i and i <= self.subtree_size + self.border_size:
            return self.num_leaf + i - self.subtree_size
        elif i > self.subtree_size + self.border_size:
            return self.num_leaf + i - self.subtree_size - 1

    def leaf_potential(self, i):
        r"""
        Compute an upper bound on the number of leaf that can be reach by
        extending the current configuration to i vertices
        """
        assert i >= self.subtree_size, "The size of the tree is not big enough"
        if self.upper_bound_strategy == 'naive' or self.subtree_size <= 2:
            return self.leaf_potential_weak(i)
        else:
            return self.leaf_potential_dist(i)

    def plot(self):
        r"""
        Plot a graph representation of the graph bordrer with following
        convention for node colors:
            green: The node is in the subtree
            yellow: The vertex is on the border
            red: The vertex is rejected by an other vertex
            black:The vertex is rejected by the user
            blue: If the vertex is available

        Edges of the subtree are green.
        """
        vertex_color = {"blue": [], "yellow": [], "black": [], "red": [], "green": []}
        for v in self.graph.vertex_iterator():
            (state,info) = self.vertex_status[v]
            if state == "a":
                vertex_color["blue"].append(v)
            elif state == "b":
                vertex_color["yellow"].append(v)
            elif state == "s":
                vertex_color["green"].append(v)
            else: #state is "r"
                if info == v:
                    vertex_color["black"].append(v)
                else:
                    vertex_color["red"].append(v)

        tree_edge = []
        for (u, v, label) in self.graph.edge_iterator():
            if self.vertex_status[v][0] == InducedSubtreeConfiguration.INCLUDED\
                                        == self.vertex_status[u][0]:
                tree_edge.append((u,v))

        return self.graph.plot(vertex_colors=vertex_color,
                edge_colors={"green": tree_edge})

    def __repr__(self):
        d = (self.subtree_size, self.num_leaf, self.border_size,
                self.num_excluded)
        s = "subtree_size:%s, num_leaf:%s, border_size:%s, num_excluded:%s" %d
        return s

class InducedSubtreeConfigurationForCube(InducedSubtreeConfiguration):
    r"""
    Specilization of graph border classes for cube
    """
    def __init__(self, G, max_deg, upper_bound_strategy = 'dist'):
        r"""
        Constructor of the graph border. Initialize the state of all vertices
        to (NOT_SEEN, None).

        INPUT:
            G - The graph
            max_deg - The maximal degree authorized for a vertex in the subtree
            upper_bound_strategy - The strategy for the leaf potential (either
                'naive' or 'dist')
        """

        InducedSubtreeConfiguration.__init__(self, G, upper_bound_strategy)
        self.max_deg = max_deg

    def _max_degree(self, d):
        r"""
        Return the minimum of then and self.max_deg
        """
        return min (d, self.max_deg)
