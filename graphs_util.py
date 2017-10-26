from itertools import product

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

def is_power_of_two(n):
    r"""
    Returns True if and only if ``n`` is a power of 2.

    INPUT:

    A natural number

    OUTPUT:

    A boolean

    EXAMPLES::

        sage: all(is_power_of_two(int(n)) for n in [1, 2, 4, 8, 16])
        True
        sage: any(is_power_of_two(int(n)) for n in [3, 5, 6, 7, 9])
        False
    """
    return n == 2 ** (n.bit_length() - 1)

def is_hypercube(graph):
    r"""
    Returns True if and only if ``graph`` is isomorphic to an hypercube.

    OUTPUT

    A boolean

    EXAMPLES:

    On classical families::

        sage: all(is_hypercube(graphs.CubeGraph(d)) for d in range(1, 8))
        True
        sage: any(is_hypercube(graphs.CompleteGraph(n)) for n in range(3, 8))
        False
        sage: any(is_hypercube(graphs.WheelGraph(n)) for n in range(3, 8))
        False

    If we swap two edges in the 5-cube graph, it is not an hypercube::

        sage: G = graphs.CubeGraph(5)
        sage: G.delete_edge('00100', '10100')
        sage: G.delete_edge('10011', '10111')
        sage: G.delete_edge('00100', '10100')
        sage: G.delete_edge('10011', '10111')
        sage: is_hypercube(G)
        False
    """
    d = graph.num_verts().bit_length() - 1
    n = 2 ** d
    if graph.num_verts() != n or not all(graph.degree(u) == d for u in graph):
        return False
    else:
        vertex_to_int = dict((u, None) for u in graph.vertex_iterator())
        int_to_vertex = [None for _ in range(n)]
        u = next(graph.vertex_iterator())
        vertex_to_int[u] = 0
        int_to_vertex[0] = u
        for (vi, v) in enumerate(graph.neighbors(u)):
            vertex_to_int[v] = 2 ** vi
            int_to_vertex[2 ** vi] = v
        for ui in range(3, n):
            vi = ui - 2 ** (ui.bit_length() - 1)
            if vi != 0:
                wi = ui - 2 ** (vi.bit_length() - 1)
                v = int_to_vertex[vi]
                w = int_to_vertex[wi]
                neighbors = set(graph.neighbors(v)) & set(graph.neighbors(w))
                if len(neighbors) != 2: return False
                while neighbors:
                    u = neighbors.pop()
                    if vertex_to_int[u] is None: break
                if vertex_to_int[u] is not None: return False
                int_to_vertex[ui] = u
                vertex_to_int[u] = ui
        return all(is_power_of_two(abs(vertex_to_int[u] - vertex_to_int[v]))\
                   for (u,v) in graph.edge_iterator(labels=False))


def plot_subgraph(graph, subgraph, **kwargs):
    r"""
    Plot the subgraph induced on graph by vertices in subgraph. The subgraph
    vertices and edges are outline in green.

    This function accepts any parameter accepted by Graph.plot

    INPUT:

    - ``graph``: a graph
    - ``subgraph``: iterable containers of vertices of ```graph``

    EXAMPLE::

        sage: plot_subgraph(graphs.PetersenGraph(), [1, 2, 3, 4])
        Graphics object consisting of 26 graphics primitives
    """
    vertex_colors = {}
    vertex_colors['white'] = set(graph) - set(subgraph)
    vertex_colors['green'] = subgraph
    edge_colors = {}
    edge_colors['green'] = [(u,v) for (u, v) in product(subgraph, subgraph) if \
            graph.has_edge(u, v)]
    kwargs['edge_colors'] = edge_colors
    kwargs['vertex_colors'] = vertex_colors
    return graph.plot(**kwargs)
