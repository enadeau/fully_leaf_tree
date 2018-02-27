from collections import deque
import heapq

class Configuration(object):
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

    - ``num_excluded``: The number of vertices that are rejected

    - ``border_size``: The number of vertices in the border

    - ``vertex_status``: A dictionary that store the state of each vertex. The
      status of a vertex ``v`` is of one of the following forms:

      * ``(INCLUDED, d)`` if ``v`` is in the subtree and has degree ``d`` in
        the subtree;
      * ``(EXCLUDED, u)`` if ``v`` is excluded from the subtree, where ``u`` is
        the vertex that caused the exclusion of ``v``. In particular, if ``u ==
        v``, then it means that the vertex was manually excluded by a call to
        the function ``exclude_vertex(v)``.
      * ``(BORDER, None)`` if ``v`` is not in the subtree and is adjacent to
        exactly one vertex of the subtree;
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

    def __init__(self, graph, upper_bound_strategy='dist', max_degree=None):
        r"""
        Constructor of an induced subtree configuration.

        Some parameters are provided to improve the computation time.  For
        instance, it is possible to parametrize how the upper bound is computed
        (currently, only 'naive' or 'dist' are supported). Moreover, we can
        also parametrized the max allowed degree of the vertices in the
        subtree.

        INPUT:

        - ``graph``: The graph
        - ``upper_bound_strategy``: The strategy for the leaf potential.
        - ``max_degree``: The maximum allowed degree. No maximal degree if
          sets to ``None''.
        """
        self.graph = graph
        self.subtree_vertices = []
        self.subtree_size = 0
        self.num_leaf = 0
        self.num_excluded = 0
        self.border_size = 0
        self.vertex_status = dict()
        for v in graph.vertex_iterator():
            self.vertex_status[v] = (Configuration.NOT_SEEN, None)
        self.history = []
        assert upper_bound_strategy in ['naive', 'dist']
        self.upper_bound_strategy = upper_bound_strategy
        self.lp_dist_valid = False
        self.border_vertex = v
        if max_degree == None:
            self.max_degree_allowed_in_subtree = graph.num_verts()
        else:
            self.max_degree_allowed_in_subtree = max_degree

    def vertex_to_add(self):
        r"""
        Return any vertex of the graph that can included to the current
        solution to obtain an induced subtree.

        If no such vertex exists, the function returns ``None``.

        OUTPUT:

        A vertex or None
        """
        if self.vertex_status[self.border_vertex][0] == Configuration.BORDER:
            return self.border_vertex
        elif self.subtree_size == 0:
            for (v,(status,_)) in self.vertex_status.iteritems():
                if status == Configuration.NOT_SEEN:
                    return v
        else:
            for (v,(status,_)) in self.vertex_status.iteritems():
                if status == Configuration.BORDER:
                    return v
        return None

    def include_vertex(self, v):
        r"""
        Includes the vertex ``v`` to the current configuration.

        Assumes that the included vertex can be safely included. Also returns
        the degree in the subtree of the only vertex ``u`` with status
        ``INCLUDED`` adjacent to ``v`` after the inclusion.

        INPUT:

        ``v``: A vertex

        OUTPUT:

        An integer
        """
        assert self.vertex_status[v][0] == Configuration.BORDER or\
               (self.vertex_status[v][0] == Configuration.NOT_SEEN and \
               self.subtree_size == 0), "Invalid vertex to add"
        degree = 0
        for u in self.graph.neighbor_iterator(v):
            (state, info) = self.vertex_status[u]
            if state == Configuration.NOT_SEEN:
                self.vertex_status[u] = (Configuration.BORDER, None)
                self.border_size += 1
            elif state == Configuration.INCLUDED:
                degree = info + 1
                self.vertex_status[u] = (state, degree)
                if info == 1:
                    self.num_leaf -= 1
            elif state == Configuration.BORDER:
                self.border_size -= 1
                self.num_excluded += 1
                self.vertex_status[u] = (Configuration.EXCLUDED, v)
        if self.vertex_status[v][0] == Configuration.BORDER:
            self.vertex_status[v] = (Configuration.INCLUDED, 1)
            self.border_size -= 1
        else:
            self.vertex_status[v] = (Configuration.INCLUDED, 0)
        self.subtree_vertices.append(v)
        self.num_leaf += 1
        self.subtree_size += 1
        self.history.append(v)
        self.lp_dist_valid = False
        return degree

    def _undo_last_inclusion(self, v):
        r"""
        Reverts the inclusion of vertex ``v``.

        The last operation must be the inclusion of vertex ``v``.

        ``v``: The last included vertex
        """
        for u in self.graph.neighbor_iterator(v):
            (state, info) = self.vertex_status[u]
            if state == Configuration.BORDER:
                self.vertex_status[u] = (Configuration.NOT_SEEN, None)
                self.border_size -= 1
            elif state == Configuration.INCLUDED:
                self.vertex_status[u] = (state, info - 1)
                if info == 2:
                    self.num_leaf += 1
            elif info == v:
                self.vertex_status[u] = (Configuration.BORDER, None)
                self.num_excluded -= 1
                self.border_size += 1
        self.subtree_size -= 1
        if self.subtree_size > 0:
            self.vertex_status[v] = (Configuration.BORDER, None)
            self.border_size += 1
        else:
            self.vertex_status[v] = (Configuration.NOT_SEEN, None)
        self.num_leaf -= 1
        self.subtree_vertices.pop()

    def exclude_vertex(self, v):
        r"""
        Forces the exclusion of vertex ``v`` from the configuration.

        INPUT:

        ``v``: The vertex to exclude
        """
        assert self.vertex_status[v][0] == Configuration.BORDER or\
               self.subtree_size == 0, "Invalid vertex to exclude"
        self.vertex_status[v] = (Configuration.EXCLUDED, v)
        if self.subtree_size != 0:
            self.border_size -= 1
        self.num_excluded += 1
        self.history.append(v)
        self.lp_dist_valid = False

    def _undo_last_exclusion(self, v):
        r"""
        Reverts the exclusion of vertex ``v``.

        The last operation must be the exclusion of vertex ``v``.

        ``v``: The last excluded vertex
        """
        self.num_excluded -= 1
        if self.subtree_size == 0:
            self.vertex_status[v] = (Configuration.NOT_SEEN, None)
        else:
            self.vertex_status[v] = (Configuration.BORDER, None)
            self.border_size += 1

    def undo_last_operation(self):
        r"""
        Cancels the last operation on self.

        The operation is either an inclusion or an exclusion.
        """
        v = self.history.pop()
        self.lp_dist_valid = False
        if self.vertex_status[v][0] == Configuration.INCLUDED:
            self._undo_last_inclusion(v)
        else:
            self._undo_last_exclusion(v)

    def subtree_num_leaf(self):
        r"""
        Returns the number of leaf in the configuration subtree.

        OUTPUT:

        An integer
        """
        if self.subtree_size == 1:
            return 0
        else:
            return self.num_leaf

    def _subtree_vertices_with_degrees(self):
        r"""
        Returns a generator over ordered pairs ``(v,d)``, where ``v`` is a
        subtree vertex and ``d`` is its degree in the subtree.

        OUTPUT:

        A generator of ordered pairs
        """
        for v in self.subtree_vertices:
            yield (v, self.vertex_status[v][1])

    def degree(self, u):
        r"""
        Computes the degree of ``u``, taking into account excluded vertices.

        OUTPUT:

        An integer
        """
        return sum(1 for (v,(status,_)) in self.graph.neighbor_iterator(u)\
                     if status != Configuration.EXCLUDED)

    def _partition_by_distance(self):
        r"""
        Returns an ordered partition of the vertices that are not excluded with
        respect to their distance from the subtree internal vertices.

        The `i`-th layer contains pairs of the form `(u,d)`, where `u` is a
        vertex of degree `d` at distance exactly `i` from the inner vertices
        from the inner vertices of the subtree, for `i \geq 1`.

        OUTPUT:

        A list of list
        """
        assert self.subtree_size > 2,\
               "No inner vertices in the green tree"
        vertices = []
        visited = set()
        queue = deque()
        queue.extend(((u, 0) for u in self.subtree_vertices\
                             if self.vertex_status[u][1] > 1))
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
                    if self.vertex_status[u][0] != Configuration.EXCLUDED:
                        degree += 1
                        if u not in visited:
                            queue.append((u, dist+1))
                layer.append((v, degree))
                prev_dist = dist
        vertices.append(layer)
        return vertices

    def _leaf_potential_weak(self,i):
        r"""
        Compute an upper bound on the number of leaves that can be realized by
        any extension of self of size ``i``.

        This bound is rather naive and computed efficiently. It is the bound
        used when ``upper_bound_strategy`` is set to ``naive``.

        INPUT:

        ``i``: The size of the extension

        OUTPUT:

        An integer
        """
        if self.subtree_size <= i and i <= self.subtree_size + self.border_size:
            return self.num_leaf + i - self.subtree_size
        elif i > self.subtree_size + self.border_size:
            return self.num_leaf + i - self.subtree_size - 1

    def _leaf_potential_dist(self, i):
        r"""
        Compute an upper bound on the number of leaves that can be realized by
        any extension of self of size ``i``.

        This bound is tighter than the one returned by
        ``_leaf_potential_weak``, but takes more time to compute. It is the
        bound used when ``upper_bound_strategy`` is set to ``dist``.

        INPUT:

        ``i``: The size of the extension

        OUTPUT:

        An integer
        """
        assert self.subtree_size > 2
        if self.lp_dist_valid:
            if self.lp_dist_dict.has_key(i):
                return self.lp_dist_dict[i]
            else:
                return 0
        current_size = self.subtree_size
        current_leaf = self.num_leaf
        self.lp_dist_dict = dict()
        self.lp_dist_dict[current_size] = current_leaf
        vertices_by_dist = self._partition_by_distance()
        for (v, d) in vertices_by_dist[0]:
            if self.vertex_status[v][0] == Configuration.BORDER:
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
            leaf_to_add = min(self.max_degree_allowed_in_subtree - 1, degree - 1,\
                              max_size-current_size)
            for _ in range(leaf_to_add):
                current_size += 1
                current_leaf += 1
                self.lp_dist_dict[current_size] = current_leaf
        self.lp_dist_valid = True
        return self._leaf_potential_dist(i)

    def leaf_potential(self, i):
        r"""
        Computes an upper bound on the number of leaves that can be realized by
        any extension of self of size ``i``.

        The bounding strategy depends on the value of ``upper_bound_strategy``.

        INPUT:

        ``i``: The size of the extension

        OUTPUT:

        An integer
        """
        assert i >= self.subtree_size, "The size of the tree is not big enough"
        if self.upper_bound_strategy == 'naive' or self.subtree_size <= 2:
            return self._leaf_potential_weak(i)
        else:
            return self._leaf_potential_dist(i)

    def plot(self, **kwargs):
        r"""
        Returns a plot of self.

        The node are colored according to the following rules:

        - *green* if the node is in the subtree;
        - *red* if the vertex is excluded;
        - *yellow* if the vertex is on the border;
        - *blue* otherwise.

        Moreover, edges belonging to the induced subtree are colored in green.
        """
        vertex_color = {"blue": [], "yellow": [], "black": [], "red": [], \
                "green": []}
        for v in self.graph.vertex_iterator():
            (state,info) = self.vertex_status[v]
            if state == Configuration.NOT_SEEN:
                vertex_color["blue"].append(v)
            elif state == Configuration.BORDER:
                vertex_color["yellow"].append(v)
            elif state == Configuration.INCLUDED:
                vertex_color["green"].append(v)
            else:
                vertex_color["red"].append(v)

        tree_edge = []
        for (u, v, _) in self.graph.edge_iterator():
            if self.vertex_status[v][0] == Configuration.INCLUDED\
                                        == self.vertex_status[u][0]:
                tree_edge.append((u,v))
        kwargs['vertex_colors'] = vertex_color
        kwargs['edge_colors'] = {"green": tree_edge}
        return self.graph.plot(**kwargs)

    def __repr__(self):
        r"""
        Returns a string representation of self.
        """
        d = (self.subtree_size, self.num_leaf, self.border_size,
                self.num_excluded)
        s = "subtree_size:%s, num_leaf:%s, border_size:%s, num_excluded:%s" %d
        return s
