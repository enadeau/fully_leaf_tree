from networkx import Graph
from networkx.algorithms import is_tree
from networkx.drawing.nx_agraph import write_dot

INFINITY = float('inf')

# ---- #
# Util #
# ---- #

def directed_edges_iter(g):
    r"""
    Returns a generator over all directions of the edge of `g`.

    INPUT:

    - ``g``: an undirected graph

    OUTPUT

    A generator over ordered pairs
    """
    for (u,v) in g.edges_iter():
        yield (u,v)
        yield (v,u)

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
        assert is_tree(g)
        self.directedL = {}
        self.edgeL = {}
        self.L = {}
        self.sizes = {}

    def subtree_size(self, u, v):
        r"""
        Returns the size of the subtree induced by the arc `(u,v)`.

        INPUT:

        - ``u``: the origin of the arc
        - ``v``: the source of the arc

        OUTPUT

        A non negative integer
        """
        if (u,v) not in self.sizes:
            self.sizes[(u,v)] = sum(self.subtree_size(v, w)\
                    for w in self.g[v] if w != u) + 1
        return self.sizes[(u,v)]

    def leaf_map(self):
        r"""
        Returns the leaf map of the graph associated with self.

        OUTPUT:

        A dictionary
        """
        if not self.L:
            L = self.edge_leaf_maps()
            self.L = dict((i, max(L[(u,v)][i] for (u,v) in self.g.edges_iter()))\
                    for i in range(2, self.g.number_of_nodes() + 1))
        return self.L

    def edge_leaf_maps(self):
        r"""
        Returns the leaf maps for each edge in the graph associated with self.

        OUTPUT:

        A dictionary associating edges with a dictionary
        """
        if not self.edgeL:
            self.edgeL = dict(((u,v), {}) for (u,v) in self.g.edges_iter())
            for (u,v) in self.g.edges_iter():
                for i in range(2, self.g.number_of_nodes() + 1):
                    ntuv = self.subtree_size(u, v)
                    ntvu = self.subtree_size(v, u)
                    interval = range(max(1, i - ntvu), min(i - 1, ntuv) + 1)
                    self.edgeL[(u,v)][i] = \
                            max(self.Lt(u, v, j) + self.Lt(v, u, i - j)\
                            for j in interval)
        return self.edgeL

    def Lt(self, u, v, i):
        r"""
        Returns the leaf map value for the arc `(u,v)` and size `i`.

        More precisely, if `T` is the rooted tree induced by the arc `(u,v)`,
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
        if (u,v) not in self.directedL:
            self.directedL[(u,v)] = {}
        if i not in self.directedL[(u,v)]:
            if i == 0 or i == 1:
                self.directedL[(u,v)][i] = i
            else:
                forest = [(v, w) for w in self.g[v] if w != u]
                self.directedL[(u,v)][i] = self.Lf(forest, i - 1)
        return self.directedL[(u,v)][i]

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
        (u,v) = forest[0]
        if len(forest) == 1:
            return self.Lt(u, v, i)
        else:
            forestp = forest[1:]
            nt1 = self.subtree_size(u, v)
            nfp = sum(self.subtree_size(x, y) for (x, y) in forestp)
            interval = range(max(0, i - nfp), min(nt1, i) + 1)
            return max(self.Lt(u, v, j) + self.Lf(forestp, i - j)\
                   for j in interval)

# Main #
# ---- #

def example():
    r"""
    Illustrates the dynamic program on an example.
    """
    g = Graph()
    g.add_edges_from([('u1', 'u6'), ('u2', 'u6'), ('u3', 'u6'),\
                      ('u4', 'u8'), ('u5', 'u8'),\
                      ('u6', 'u'), ('u7', 'u'), ('u8', 'u'),\
                      ('v2', 'v3'), ('v2', 'v4'), ('v', 'v2'), ('v', 'v1'),\
                      ('u', 'v')])
    
    program = LeafMapDynamicProgram(g)
    L = program.leaf_map()
    (x,y) = ('v', 'u')
    Ltxy = [program.Lt(x, y, i) for i in range(program.subtree_size(x, y) + 1)]
    print('Lt(%s, %s) = %s' % (x, y, Ltxy))
    print('L[%s -> %s] = %s' % (x, y, program.directedL[(x,y)]))
    v = L.values()
    w = [v[i+1] - v[i] for i in range(1, len(v) - 1)]
    print(v)
    print(w)

example()
