from datetime import datetime
import warnings
load('graph_border.py')
load('flis_trees.py')

def leaf_map(graph, algorithm='general', upper_bound_strategy='dist'):
    """
    Compute the leaf function of ``graph``.

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

    - ``G``: A simple graph
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

    OUTPUT:

    A pair ``(L, E)`` where ``L`` is a dictionnary representing the leaf
    function and ``E`` a dictionnary of list of examples of fully leafed trees
    for each size.  If ``L[i] == None`` no induced of size ``i`` exists in
    ``G``.

    EXAMPLE:

        sage: leaf_map(graphs.CompleteGraph(7))[0]
        {0: 0, 1: 0, 2: 2, 3: None, 4: None, 5: None, 6: None, 7: None}
        sage: leaf_map(graphs.CycleGraph(10))[0]
        {0: 0, 1: 0, 2: 2, 3: 2, 4: 2, 5: 2, 6: 2, 7: 2, 8: 2, 9: 2, 10: None}
        sage: leaf_map(graphs.WheelGraph(11))[0]
        {0: 0, 1: 0, 2: 2, 3: 2, 4: 3, 5: 4, 6: 5, 7: 2, 8: 2, 9: 2, 10: None, 11: None}
        sage: leaf_map(graphs.CompleteBipartiteGraph(7,5))[0]
        {0: 0, 1: 0, 2: 2, 3: 2, 4: 3, 5: 4, 6: 5, 7: 6, 8: 7, 9: None, 10: None, 11: None, 12: None}
        sage: leaf_map(graphs.PetersenGraph())[0]
        {0: 0, 1: 0, 2: 2, 3: 2, 4: 3, 5: 3, 6: 4, 7: 3, 8: None, 9: None, 10: None}
        sage: leaf_map(graphs.CubeGraph(3), algorithm='cube')[0]
        {0: 0, 1: 0, 2: 2, 3: 2, 4: 3, 5: 2, 6: None, 7: None, 8: None}
        sage: leaf_map(graphs.BalancedTree(2, 2), algorithm='tree')[0]
        {0: 0, 1: 0, 2: 2, 3: 2, 4: 3, 5: 3, 6: 3, 7: 4}
    """
    def explore_configuration():
        r"""
        Explore all interesting subtrees of ``G`` and update the dictionnary
        ``L`` to keep track of the maximum.
        """
        m = B.subtree_size
        l = B.subtree_num_leaf()
        promising = sum([L[i] < B.leaf_potential(i) for i in range(m,
            n + 1 - B.num_excluded)]) > 0
        next_vertex = B.vertex_to_add()
        if next_vertex == None:
            if L[m] == l:
                max_leafed_tree[m].append(copy(B.subtree_vertices))
            elif L[m] < l:
                max_leafed_tree[m] = [copy(B.subtree_vertices)]
                L[m] = l
        elif promising:
            B.include_vertex(next_vertex)
            explore_configuration()
            B.undo_last_operation()
            B.exclude_vertex(next_vertex)
            explore_configuration()
            B.undo_last_operation()

    assert upper_bound_strategy in ['naive', 'dist']
    assert algorithm in ['general', 'cube', 'tree']
    if algorithm == 'general':
        n = G.num_verts()
        L = dict([(i, None) for i in range(0, n+1)])
        max_leafed_tree = dict([(i, []) for i in range(n+1)])
        L[0] = 0
        max_leafed_tree[0] = [[]]
        B = Configuration(G, upper_bound_strategy)
        explore_configuration()
        return L, max_leafed_tree
    elif algorithm == 'tree':
        assert G.is_tree(), "G is not a tree"
        program = LeafMapDynamicProgram(G)
        return program.leaf_map_with_example()
    elif algorithm == 'cube':
        d = G.num_verts().bit_length() - 1
        assert G.num_verts() == 2 **d
        return _cube_graph_leaf_map(d)

def _cube_graph_leaf_map(d, upper_bound_strategy='dist', save_progress=False):
    r"""
    Computes the leaf function for the cube graph of dimension ``d``.

    See `leaf_map` for more details.

    INPUT:

    - ``d``: Dimension of the hypercube;
    - ``upper_bound_strategy``: The strategy for the upper bound (either
      'dist' or 'naive');
    - ``save_progress``: Indicates whether to save partial solutions,
      especially for long computations.

    OUTPUT:

    A pair ``(L, E)`` where ``L`` is a dictionnary representing the leaf
    function and ``E`` a dictionnary of list of examples of fully leafed trees
    for each size.  If ``L[i] == None`` no induced of size ``i`` exists in
    ``G``.

    ALGORITHM:

    Uses symmetries of the hypercube to avoid exploring many times isometric
    configurations.

    EXAMPLE:

        sage: _cube_graph_leaf_map(3)[0]
        {0: 0, 1: 0, 2: 2, 3: 2, 4: 3, 5: 2, 6: None, 7: None, 8: None}
        sage: list(_cube_graph_leaf_map(4)[0].values())
        [0, 0, 2, 2, 3, 4, 3, 4, 3, 4, None, None, None, None, None, None, None]
    """
    def explore_configuration(max_deg):
        r"""
        Explore all the possible subtrees with maximum degree ``max_deg`` of
        ``G`` and update the dictionnary ``L`` to keep track of the maximum.

        Branchs with including/excluding a vertex of the subtree.
        """
        m = B.subtree_size
        l = B.subtree_num_leaf()
        promising = sum([L[i] < B.leaf_potential(i) for i in range(m,
            n + 1 - B.num_excluded)]) > 0
        next_vertex = B.vertex_to_add()
        if next_vertex == None:
            if L[m] == l:
                max_leafed_tree[m].append(copy(B.subtree_vertices))
            elif L[m] < l:
                max_leafed_tree[m] = [copy(B.subtree_vertices)]
                L[m] = l
        elif promising:
            degree = B.include_vertex(next_vertex)
            if degree <= i:
                explore_configuration(max_deg)
            B.undo_last_operation()
            B.exclude_vertex(next_vertex)
            explore_configuration(max_deg)
            B.undo_last_operation()
    assert upper_bound_strategy in ['naive', 'dist']
    # Number of vertices in the biggest induced snake in cube
    # See http://ai1.ai.uga.edu/sib/sibwiki/doku.php/records
    snake_in_the_box = {1: 2, 2: 3, 3: 5, 4: 8, 5: 14, 6: 27, 7: 51, 8: 99}
    base_vertex = '0' * d
    star_vertices = ['0' * i + '1' + '0' * (d - i - 1) for i in range(d)]
    extension_vertex = '1' + '0' * (d - 2) + '1'
    G = graphs.CubeGraph(d)
    n = G.num_verts()
    L = dict([(i, None) for i in range(n + 1)])
    max_leafed_tree = dict([(i, []) for i in range(n + 1)])
    # Initialization for small value
    L[0] = 0
    max_leafed_tree[0] = [[]]
    L[1] = 0
    max_leafed_tree[1].append([base_vertex])
    L[2] = 2
    max_leafed_tree[2].append([base_vertex, star_vertices[0]])
    for i in range(3, d + 2):
        L[i] = i - 1
        max_leafed_tree[i].append([base_vertex]+star_vertices[:i - 1])
    # Initialization according to snake-in-the-box
    if d <= 8:
        for i in range(2, snake_in_the_box[d] + 1):
            L[i] = max(2, L[i])
    else:
        raise ValueError, "d is too big, no chance of sucess"
    # Main computations
    for i in range(d - 1, 2, -1):
        # Initialization of a starting configuration with a i-pode
        B = Configuration(G, upper_bound_strategy, i)
        B.include_vertex(base_vertex)
        for j in range(d):
            if j < i:
                B.include_vertex(star_vertices[j])
            else:
                B.exclude_vertex(star_vertices[j])
        B.include_vertex(extension_vertex)
        explore_configuration(i)
        if save_progress:
            print "Exploration for %s-pode complete at %s" %\
                    (i, str(datetime.now()))
            name = "L-dict-after-" + str(i) + "-pode.sobj"
            save(L, name)
            print "%s saved" %name
            name = "Max-leafed-tree-after" + str(i) + "-pode.sobj"
            save(max_leafed_tree, name)
            print "%s saved" %name
    # Add examples if fully leafed tree are snakes
    for i in range(d + 1, n + 1):
        if L[i] == 2 and i not in [2, 3]:
            if (i, d) == (5, 3):
                max_leafed_tree[5] = [['000', '100', '110', '111', '011']]
            else:
                warnings.warn(("Warning: This program cannot return an example"
                        " of fully leafed tree of size %s" %i))
    return (L, max_leafed_tree)
