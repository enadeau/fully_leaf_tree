def plot_subgraph(graph, vertices):
    vertex_colors = {}
    vertex_colors['green'] = frozenset(vertices)
    return graph.plot(vertex_colors=vertex_colors,\
                      vertex_size=1000,\
                      layout='circular')

