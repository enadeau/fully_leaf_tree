INFINITY = float('inf')

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
                forest = [(v, w) for w in self.g[v] if w != u]
                self.directedL[(u, v)][i] = self.Lf(forest, i - 1)
        return self.directedL[(u, v)][i]

    def Lf(self, forest, i):
        r"""
        Returns the leaf map value for the forest `forest` for size `i`.

        More precisely, if `F = \{T_1,\ldots,T_k\}` is a rooted forest then
        `self.Lf(F, i)` returns the maximal number of leaves that can be
        realized by a rooted induced subforest of `F` of size `i`.

        NOTE:

        The returned value is cached to avoid redundant computations.

        INPUT:

        - ``forest``: the induced subforest
        - ``i``: the size of the induced subforest

        OUTPUT:

        A non negative integer
        """
        (u, v) = forest[0]
        if len(forest) == 1:
            return self.Lt(u, v, i)
        else:
            forestp = forest[1:]
            nt1 = self.subtree_size(u, v)
            nfp = sum(self.subtree_size(x, y) for (x, y) in forestp)
            interval = range(max(0, i - nfp), min(nt1, i) + 1)
            return max(self.Lt(u, v, j) + self.Lf(forestp, i - j)\
                   for j in interval)
