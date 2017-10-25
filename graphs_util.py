def directed_edges_iter(graph):
    r"""
    Returns a generator over all directions of the edge of `graph`.

    INPUT:

    - ``graph``: an undirected graph

    OUTPUT:

    A generator over ordered pairs

    EXAMPLE:

        sage: sorted(list(directed_edges_iter(graphs.WheelGraph(3))))
        [(0, 1), (0, 2), (1, 0), (1, 2), (2, 0), (2, 1)]
    """
    for (u, v, label) in graph.edge_iterator():
        yield (u, v)
        yield (v, u)
