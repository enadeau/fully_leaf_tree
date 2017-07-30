load('graph_border.py')

def ComputeL(G):
    """Compute the maximal number of leaves that can be obtain in a tree
     wich is an induced subgraph of size m of G for each m between 0 and
     |G|.

    INPUT:
        G - a graph

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
    """
    global L
    global B
    n=G.num_verts()
    L=dict([(i,0) for i in range(0,n+1)])
    B=GraphBorder(G)
    ComputeLRecursive(G)
    return L

def ComputeLRecursive(G):
    """Explore all the possible subtree of G and update the dictionnary L
    to keep track of the maximum.

    INPUTS:
        G - the graph of the connected component of the original graph
        (without the rejected vertices) containing the vertices of V_add

    OUTPUT:
        Branchs with including/excluding a vertex of the subtree.
        When at the end of the research tree, updates a global dictonnary
        L create by ComputeL(G)
    """
    global L
    global B
    m=B.subtree_size
    l=B.subtree_num_leaf()
    #promising=sum([L[m]<l*(connexity_lack==0)]+[L[m+j]<l+j-connexity_lack for j in range(1,G.num_verts()-m)])>0
    promising=True
    next_vertex=B.vertex_to_add()
    if next_vertex==None:
        #The subtree can't be extend
        L[m]=max(L[m],l)
    elif promising:
        B.add_to_subtree(next_vertex)
        ComputeLRecursive(G)
        B.undo_last_user_action()
        B.reject_vertex(next_vertex)
        ComputeLRecursive(G)
        B.undo_last_user_action()
