# ---- #
# Util #
# ---- #

def directed_edges_iter(g):
    r"""
    Returns a generator over all directions of the edge of `g`.

    INPUT:

    - ``g``: an undirected graph

    OUTPUT:

    A generator over ordered pairs

    EXAMPLE:

        sage: sorted(list(directed_edges_iter(graphs.WheelGraph(3))))
        [(0, 1), (0, 2), (1, 0), (1, 2), (2, 0), (2, 1)]
    """
    for (u, v, label) in g.edge_iterator():
        yield (u, v)
        yield (v, u)

# --------------- #
# Dynamic Program #
# --------------- #

class LeafMapDynamicProgram(object):
    r"""
    A dynamic program for computing leaf maps for trees.

    INPUT:

    - ``g``: the tree
    """

    def __init__(self, g):
        self.g = g
        assert g.is_tree()
        self.directedL = {}
        self.edgeL = {}
        self.L = {}
        self.sizes = {}
        self.forest_edges = {}
        self.forest_size = {}
        self.forestL = {}

    def subtree_size(self, u, v):
        r"""
        Returns the size of the subtree induced by the arc `(u, v)`.

        INPUT:

        - ``u``: the origin of the arc
        - ``v``: the source of the arc

        OUTPUT

        A non negative integer

        EXAMPLE:

        Consider the perfectly balanced ternary tree of height `2`. Then each
        of its subtree are of size `4`::

            sage: T = graphs.BalancedTree(3, 2)
            sage: program = LeafMapDynamicProgram(T)
            sage: [program.subtree_size(0, i) for i in range(1, 4)]
            [4, 4, 4]
        """
        if (u, v) not in self.sizes:
            self.sizes[(u, v)] = sum(self.subtree_size(v, w)\
                    for w in self.g[v] if w != u) + 1
        return self.sizes[(u, v)]

    # ----------------------- #
    # Computing the leaf maps #
    # ----------------------- #

    def leaf_map(self):
        r"""
        Returns the leaf map of the graph associated with self.

        OUTPUT:

        A dictionary

        EXAMPLE:

        The perfectly balanced binary tree of height `2`:

            sage: T = graphs.BalancedTree(2, 2)
            sage: program = LeafMapDynamicProgram(T)
            sage: program.leaf_map()
            {0: 0, 1: 0, 2: 2, 3: 2, 4: 3, 5: 3, 6: 3, 7: 4}
        """
        if not self.L:
            L = self.edge_leaf_maps()
            self.L = dict((i, max(L[(u, v)][i] for (u, v, l) in \
                    self.g.edge_iterator())) for i in range(2,
                        self.g.num_verts() + 1))
            self.L[0] = 0
            self.L[1] = 0
        return self.L

    def edge_leaf_maps(self):
        r"""
        Returns the leaf maps for each edge in the graph associated with self.

        OUTPUT:

        A dictionary associating edges with a dictionary

        EXAMPLE:

        The perfectly balanced binary tree of height `2`:

            sage: T = graphs.BalancedTree(3, 2)
            sage: program = LeafMapDynamicProgram(T)
            sage: leaf_maps = program.edge_leaf_maps()
            sage: leaf_maps[(0, 1)].values()
            [2, 2, 3, 4, 4, 5, 5, 6, 7, 7, 8, 9]
        """
        if not self.edgeL:
            self.edgeL = dict(((u, v), {}) for (u, v, l) in \
                    self.g.edge_iterator())
            for (u,v, l) in self.g.edge_iterator():
                for i in range(2, self.g.num_verts() + 1):
                    ntuv = self.subtree_size(u, v)
                    ntvu = self.subtree_size(v, u)
                    interval = range(max(1, i - ntvu), min(i - 1, ntuv) + 1)
                    self.edgeL[(u, v)][i] = \
                            max(self.Lt(u, v, j) + self.Lt(v, u, i - j)\
                            for j in interval)
        return self.edgeL

    def Lt(self, u, v, i):
        r"""
        Returns the leaf map value for the arc `(u, v)` and size `i`.

        More precisely, if `T` is the rooted tree induced by the arc `(u, v)`,
        then `self.Lt(u, v, i)` returns the maximal number of leaves that can
        be realized by a rooted induced subtree of size `i` whose root is `v`.

        NOTE:

        The returned value is cached to avoid redundant computations.

        INPUT:

        - ``u``: the origin of the arc
        - ``v``: the source of the arc
        - ``i``: the size of the induced subtree

        OUTPUT:

        A non negative integer
        """
        n = self.subtree_size(u, v)
        assert i <= n
        if (u, v) not in self.directedL:
            self.directedL[(u, v)] = {}
        if i not in self.directedL[(u, v)]:
            if i == 0 or i == 1:
                self.directedL[(u, v)][i] = i
            else:
                self.directedL[(u, v)][i] = self.Lf(u, v, 0, i - 1)
        return self.directedL[(u, v)][i]

    def Lf(self, u, v, k, i):
        r"""
        Returns the leaf map value for the forest formed by the rooted subtrees
        `0, 1, ..., k` of `v` in direction `u \rightarrow v` for size `i`.

        More precisely, if `F = \{T_1,\ldots,T_k\}` is a rooted forest then
        `self.Lf(F, i)` returns the maximal number of leaves that can be
        realized by a rooted induced subforest of `F` of size `i`.

        NOTE:

        The returned value is cached to avoid redundant computations.

        INPUT:

        - ``u, v``: vertices such that ``(u, v)`` is an arc
        - ``k``: the index of the first child in the forest
        - ``i``: the size of the induced subforest

        OUTPUT:

        A non negative integer
        """
        if (u, v) not in self.forest_edges:
            self.forest_edges[(u, v)] = [(v, w) for w in self.g[v] if w != u]
            self.forest_size[(u, v)] = len(self.forest_edges[(u, v)])
            self.forestL[(u, v)] = [{} for _ in range(self.forest_size[(u, v)])]
        if i not in self.forestL[(u, v)][k]:
            forest_edges = self.forest_edges[(u, v)]
            forest_size = self.forest_size[(u, v)]
            w = forest_edges[k][1]
            if k == forest_size - 1:
                self.forestL[(u, v)][k][i] = self.Lt(v, w, i)
            else:
                nt1 = self.subtree_size(v, w)
                nfp = sum(self.subtree_size(x, y) for (x, y) in forest_edges[k+1:])
                interval = range(max(0, i - nfp), min(nt1, i) + 1)
                self.forestL[(u, v)][k][i] =\
                    max(self.Lt(v, w, j) + self.Lf(u, v, k + 1, i - j)\
                        for j in interval)
        return self.forestL[(u, v)][k][i]

    def leaf_map_with_example(self):
        r"""
        Returns the leaf function together with a dictionary giving fully
        leafed induced subtrees for each possible size.

        OUTPUT:

            An ordered pair of dictionaries

        EXAMPLE:

            sage: T = graphs.BalancedTree(2, 2)
            sage: program = LeafMapDynamicProgram(T)
            sage: (L,E) = program.leaf_map_with_example()
            sage: L
            {0: 0, 1: 0, 2: 2, 3: 2, 4: 3, 5: 3, 6: 3, 7: 4}
            sage: E
            {0: [[]],
             1: [[0]],
             2: [[1, 0]],
             3: [[1, 0, 2]],
             4: [[1, 3, 4, 0]],
             5: [[1, 0, 2, 5, 6]],
             6: [[1, 4, 0, 2, 5, 6]],
             7: [[1, 3, 4, 0, 2, 5, 6]]}
        """
        examples = dict([(i,self.example(i)) for i in range(self.g.num_verts() + 1)])
        return (self.leaf_map(), examples)

    # -------------------- #
    # Retrieving solutions #
    # -------------------- #

    def directed_tree_example(self, u, v, i):
        r"""
        Returns a fully leafed directed subtree of size `i` of the subtree
        rooted in `v` in direction `u \rightarrow v`.

        INPUT:

        - ``u, v``: vertices such that ``(u, v)`` is an arc
        - ``i``: the size of the directed subtree

        OUTPUT

        A list of vertices
        """
        if i == 0:
            return []
        else:
            return [v] + self.directed_forest_example(u, v, 0, i - 1)

    def directed_forest_example(self, u, v, k, i):
        r"""
        Returns a fully leafed directed subforest of size `i` of the forest
        formed by the rooted subtrees of `v` in direction `u \rightarrow v`.

        INPUT:

        - ``u, v``: vertices such that ``(u, v)`` is an arc
        - ``k``: the index of the first child in the forest
        - ``i``: the size of the directed subforest

        OUTPUT

        A list of vertices
        """
        if i == 0:
            return []
        else:
            forest_edges = self.forest_edges[(u, v)]
            forest_size = self.forest_size[(u, v)]
            forestL = self.forestL[(u, v)]
            w = forest_edges[k][1]
            if k == forest_size - 1:
                return self.directed_tree_example(v, w, i)
            else:
                nt1 = self.subtree_size(v, w)
                nfp = sum(self.subtree_size(x, y) for (x, y) in forest_edges[k+1:])
                interval = range(max(0, i - nfp), min(nt1, i) + 1)
                j = next(j for j in interval if self.Lt(v, w, j) +\
                        self.Lf(u, v, k + 1, i - j) == forestL[k][i])
                return self.directed_tree_example(v, w, j) +\
                       self.directed_forest_example(u, v, k + 1, i - j)


    def example(self, i):
        r"""
        Returns a fully leafed induced subtree of size ``i``.

        INPUT:

        ``i``: the number of vertices in the tree

        OUTPUT

        A list of lists
        """
        if i == 0:
            return [[]]
        elif i == 1:
            return [[next(self.g.vertex_iterator())]]
        else:
            L = self.leaf_map()
            edgeL = self.edge_leaf_maps()
            (u, v) = next(e for e in edgeL if edgeL[e][i] == L[i])
            ntuv = self.subtree_size(u, v)
            ntvu = self.subtree_size(v, u)
            interval = range(max(1, i - ntvu), min(i - 1, ntuv) + 1)
            j = next(j for j in interval\
                       if self.Lt(u, v, j) + self.Lt(v, u, i - j) == edgeL[(u,v)][i])
            return [self.directed_tree_example(u, v, j) +\
                    self.directed_tree_example(v, u, i - j)]
