load('flis_configuration.py')

def induced_subtree_generator(G, only_unisometric=False):
    r"""
    INPUT:
    - ``only_unisometric``: If true yield only one tree for each isometry
      classes
    """
    INCLUDED = 0
    EXCLUDED = 1
    if only_unisometric:
        C = ConfigurationForGenStab(G)
    else:
        C = Configuration(G)
    vertex_stack = []
    while True:
        next_vertex = C.vertex_to_add()
        while next_vertex != None:
            C.include_vertex(next_vertex)
            vertex_stack.append((INCLUDED, next_vertex))
            next_vertex = C.vertex_to_add()
        yield copy(C.subtree_vertices)
        while vertex_stack and vertex_stack[-1][0] == EXCLUDED:
            C.undo_last_operation()
            vertex_stack.pop()
        if len(vertex_stack) == 0:
            break
        (s, v) = vertex_stack.pop()
        C.undo_last_operation()
        C.exclude_vertex(v)
        vertex_stack.append((EXCLUDED, v))
