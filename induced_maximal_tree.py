from graph_border import GraphBorder

class InducedSubtreeSolver(object):

    def __init__(self, G, upper_bound_strategy='dist'):
        """Compute the maximal number of leaves that can be obtain in a tree
         wich is an induced subgraph of size m of G for each m between 0 and
         |G|.

        INPUT:
            G - a graph
            upper_bound_strategy - The strategy for the upper bound (either
                'dist' or 'naive')

        OUTPUT:
            A dictionnary L that associate to the number of vertices, the
            maximal number of leaves.

        EXAMPLES:
            sage: ComputeL(graphs.CompleteGraph(7))
            {0: 0, 1: 0, 2: 2, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0}
            sage: ComputeL(graphs.CycleGraph(10))
            {0: 0, 1: 0, 2: 2, 3: 2, 4: 2, 5: 2, 6: 2, 7: 2, 8: 2, 9: 2, 10: 0}
            sage: ComputeL(graphs.WheelGraph(11))
            {0: 0, 1: 0, 2: 2, 3: 2, 4: 3, 5: 4, 6: 5, 7: 2, 8: 2, 9: 2, 10: 0, 11: 0}
            sage: ComputeL(graphs.CompleteBipartiteGraph(7,5))
            {0: 0, 1: 0, 2: 2, 3: 2, 4: 3, 5: 4, 6: 5, 7: 6, 8: 7, 9: 0, 10: 0, 11: 0, 12: 0}
            sage: ComputeL(graphs.PetersenGraph())
            {0: 0, 1: 0, 2: 2, 3: 2, 4: 3, 5: 3, 6: 4, 7: 3, 8: 0, 9: 0, 10: 0}
            sage: ComputeL(graphs.CubeGraph(3))
            {0: 0, 1: 0, 2: 2, 3: 2, 4: 3, 5: 2, 6: 0, 7: 0, 8: 0}
        """
        assert upper_bound_strategy in ['naive', 'dist']
        self.G = G
        self.upper_bound_strategy = upper_bound_strategy
        self.n = G.num_verts()

    def maximal_num_leaf(self, i):
        self.i = i
        self.B = GraphBorder(self.G, i, self.upper_bound_strategy)
        self.best = 0
        self._treat_state()
        return self.best

    def leaf_function(self):
        return dict((i, self.maximal_num_leaf(i))\
                    for i in range(self.n))

    def _treat_state(self):
        """Explore all the possible subtree of G and update the dictionnary L
        to keep track of the maximum.

        Branchs with including/excluding a vertex of the subtree.
        """
        l = self.B.subtree_num_leaf()
        promising = self.i >= self.B.subtree_size and \
                    self.B.leaf_potential(self.i) > self.best
        next_vertex = self.B.vertex_to_add()
        if next_vertex is None:
            if self.B.subtree_size == self.i:
                self.best = max(self.best, l)
        elif promising:
            self.B.add_to_subtree(next_vertex)
            self._treat_state()
            self.B.undo_last_user_action()
            self.B.reject_vertex(next_vertex)
            self._treat_state()
            self.B.undo_last_user_action()
