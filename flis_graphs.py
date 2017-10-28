from datetime import datetime
import warnings
load('flis_configuration.py')
load('flis_trees.py')
load('graphs_util.py')

class flis_solver(object):
    r"""
    A program to compute the leaf map and fully leafed trees for graph.

    Given a simple graph `G = (V,E)` and `T` a subset of `V`, we say that T is
    a fully leafed induced subtree of size `i` if the following conditions are
    satisfied:

    1. `|T| = i` (`T` is of size `i`);
    2. The subgraph `G[T]` induced by `T` is a tree;
    3. The number of leaves of `G[T]` is maximum, i.e. there is no other
       induced subtree of size `i` having strictly more leaves than `G[T]`.

    The leaf function of a graph `G` of `n` vertices, denoted by `L_G`, is the
    function whose domain is `\{0,1,...,n\}` and such that `L_G(i)` is the
    number of leaves of a fully leafed induced subtree of size `i`.

    INPUT:

    - ``graph``: A simple graph
    - ``algorithm``: The algorithm used to compute the leaf map. Currently,
      there are three options:

      * ``'general'``: The branch and bound algorithm for general graphs;
      * ``'tree'``: A polynomial time algorithm based on dynamic programming;
      * ``'cube'``: A specialized branch and bound algorithm exploiting the
        symmetries of the hypercubes.

    - ``upper_bound_strategy``: The strategy for the upper bound in the branch
      and bound algorithm (either 'dist' or 'naive')

      * ``'naive'``: The bound is trivial (it is the number of available
        vertices);
      * ``'dist'``: The bound takes into account what vertices could
        potentially be added in the extension according to their distance.

    EXAMPLE::

        sage: flis_solver(graphs.CompleteGraph(7)).leaf_map()
        {0: 0, 1: 0, 2: 2, 3: None, 4: None, 5: None, 6: None, 7: None}
        sage: flis_solver(graphs.CycleGraph(10)).leaf_map()
        {0: 0, 1: 0, 2: 2, 3: 2, 4: 2, 5: 2, 6: 2, 7: 2, 8: 2, 9: 2, 10: None}
        sage: flis_solver(graphs.WheelGraph(11)).leaf_map()
        {0: 0, 1: 0, 2: 2, 3: 2, 4: 3, 5: 4, 6: 5, 7: 2, 8: 2, 9: 2, 10: None, 11: None}
        sage: flis_solver(graphs.CompleteBipartiteGraph(7,5)).leaf_map()
        {0: 0, 1: 0, 2: 2, 3: 2, 4: 3, 5: 4, 6: 5, 7: 6, 8: 7, 9: None, 10: None, 11: None, 12: None}
        sage: flis_solver(graphs.PetersenGraph()).leaf_map()
        {0: 0, 1: 0, 2: 2, 3: 2, 4: 3, 5: 3, 6: 4, 7: 3, 8: None, 9: None, 10: None}
        sage: flis_solver(graphs.CubeGraph(3), algorithm='cube').leaf_map()
        {0: 0, 1: 0, 2: 2, 3: 2, 4: 3, 5: 2, 6: None, 7: None, 8: None}
        sage: flis_solver(graphs.BalancedTree(2, 2), algorithm='tree').leaf_map()
        {0: 0, 1: 0, 2: 2, 3: 2, 4: 3, 5: 3, 6: 3, 7: 4}
        sage: flis_solver(graphs.CubeGraph(4), algorithm='cube').leaf_map().values()
        [0, 0, 2, 2, 3, 4, 3, 4, 3, 4, None, None, None, None, None, None, None]
    """

    def __init__(self, graph, algorithm='general', upper_bound_strategy='dist'):
        assert upper_bound_strategy in ['naive', 'dist'], ('Invalid'
                ' upper_bound_strategy')
        assert algorithm in ['general', 'cube', 'tree'], 'algorithm invalid'
        if algorithm == 'tree':
            assert graph.is_tree(), 'graph is not a tree'
        elif algorithm == 'cube':
            assert is_hypercube(graph), 'graph is not a hypercube'
        self.graph = graph
        self.n = self.graph.num_verts()
        self.algorithm = algorithm
        self.upper_bound_strategy = upper_bound_strategy
        self.lf = {}
        self.flt = {}

    def leaf_map(self):
        r"""
        Returns the leaf map of ``self.graph``.

        OUTPUT:

        A dictionnary ``L`` representing the leaf map. If ``L[i] == None`` no
        induced of size ``i`` exists in ``G``.
        """
        if not self.lf:
            self.lf = dict([(i, None) for i in range(0, self.n + 1)])
            self.flt = dict([(i, []) for i in range(self.n + 1)])
            self.lf[0] = 0
            self.flt[0] = [[]]
            if self.algorithm == 'tree':
                self._leaf_map_tree()
            elif self.algorithm == 'cube':
                d = self.n.bit_length() - 1
                self._leaf_map_hypercube(d)
            else:
                self._leaf_map_general()
        return self.lf


    def fully_leafed_subtrees(self, i=None):
        r"""
        Returns some fully leafed trees of ``self.graph`` of size ``i``.

        If ``i == None``, returns a dictionnary of examples for each size.

        OUTPUT:

        If ``i == None ``: A dictionnary of list of examples of fully leafed
        trees for each size.

        If i an interger:  A list of examples of fully leafed trees of size
        ``i``.
        """
        assert i in  range(self.n+1) or i == None, 'i invalid'
        if not self.flt:
            self.leaf_map()
        if i == None:
            return self.flt
        else:
            return self.flt[i]


    def _leaf_map_general(self):
        r"""
        Leaf map and examples computations with general algorithm.
        """
        self.configuration = Configuration(self.graph,
                self.upper_bound_strategy)
        self._explore_configuration()

    def _leaf_map_hypercube(self, d, save_progress = False):
        r"""
        Leaf map and examples computations with hypercube algorithm.

        INPUT:

        - ``d``: Dimension of the hypercube;
        - ``save_progress``: Indicates whether to save partial solutions,
          especially for long computations.

        ALGORITHM:

        Uses symmetries of the hypercube to avoid exploring many times isometric
        configurations.
        """
        # Number of vertices in the biggest induced snake in cube
        # See http://ai1.ai.uga.edu/sib/sibwiki/doku.php/records
        snake_in_the_box = {1: 2, 2: 3, 3: 5, 4: 8, 5: 14, 6: 27, 7: 51, 8: 99}
        base_vertex = '0' * d
        star_vertices = ['0' * i + '1' + '0' * (d - i - 1) for i in range(d)]
        extension_vertex = '1' + '0' * (d - 2) + '1'
        graph = graphs.CubeGraph(d)
        # Initialization for small value
        self.lf[1] = 0
        self.flt[1].append([base_vertex])
        self.lf[2] = 2
        self.flt[2].append([base_vertex, star_vertices[0]])
        for i in range(3, d + 2):
            self.lf[i] = i - 1
            self.flt[i].append([base_vertex]+star_vertices[:i - 1])
        # Initialization according to snake-in-the-box
        if d <= 8:
            for i in range(2, snake_in_the_box[d] + 1):
                self.lf[i] = max(2, self.lf[i])
        else:
            raise ValueError, ("dimension of hypercue is too big, "
                "no chance of sucess")
        # Main computations
        for i in range(d - 1, 2, -1):
            # Initialization of a starting configuration with a i-pode
            self.configuration = Configuration(self.graph,
                    self.upper_bound_strategy, i)
            self.configuration.include_vertex(base_vertex)
            for j in range(d):
                if j < i:
                    self.configuration.include_vertex(star_vertices[j])
                else:
                    self.configuration.exclude_vertex(star_vertices[j])
            self.configuration.include_vertex(extension_vertex)
            self._explore_configuration(max_deg=i)
            if save_progress:
                print "Exploration for %s-pode complete at %s" %\
                        (i, str(datetime.now()))
                name = "L-dict-after-" + str(i) + "-pode.sobj"
                save(self.lf, name)
                print "%s saved" %name
                name = "Max-leafed-tree-after" + str(i) + "-pode.sobj"
                save(self.flt, name)
                print "%s saved" %name
        # Add examples if fully leafed tree are snakes
        for i in range(d + 1, self.n + 1):
            if self.lf[i] == 2 and i not in [2, 3]:
                if (i, d) == (5, 3):
                    self.flt[5] = [['000', '100', '110', '111', '011']]
                else:
                    warnings.warn(("Warning: This program cannot return an"
                            " example of fully leafed tree of size %s" % i))

    def _leaf_map_tree(self):
        r"""
        Leaf map  and examples computation with tree algorithm.
        """
        program = LeafMapDynamicProgram(self.graph)
        (L, E) = program.leaf_map_with_example()
        self.lf = L
        self.flt = E

    def _explore_configuration(self, max_deg=Infinity):
        r"""
        Explores all the possible subtrees  with maximum degree ``max_deg`` of
        ``self.graph`` and updates ``self.lf`` and
        ``self.flt``  to keep track subtrees with the maximum
        number of leaves.
        """
        C = self.configuration
        m = C.subtree_size
        l = C.subtree_num_leaf()
        promising = any(self.lf[i] < C.leaf_potential(i) for i in range(m,
            self.n + 1 - C.num_excluded))
        next_vertex = C.vertex_to_add()
        if next_vertex == None:
            if self.lf[m] == l:
                self.flt[m].append(copy(C.subtree_vertices))
            elif self.lf[m] < l:
                self.flt[m] = [copy(C.subtree_vertices)]
                self.lf[m] = l
        elif promising:
            degree = C.include_vertex(next_vertex)
            if degree <= max_deg:
                self._explore_configuration(max_deg)
            C.undo_last_operation()
            C.exclude_vertex(next_vertex)
            self._explore_configuration(max_deg)
            C.undo_last_operation()
