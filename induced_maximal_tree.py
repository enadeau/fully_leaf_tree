<<<<<<< HEAD
from graph_border import GraphBorder
=======
load('graph_border.py')
from datetime import datetime
>>>>>>> specialize_cube

def ComputeL(G, upper_bound_strategy='dist'):
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
    def treat_state():
        """Explore all the possible subtree of G and update the dictionnary L
        to keep track of the maximum.

        Branchs with including/excluding a vertex of the subtree.
        """
        m=B.subtree_size
        l=B.subtree_num_leaf()
        promising=sum([L[i]<B.leaf_potential(i) for i in range(m,n+1-B.num_rejected)])>0
        next_vertex=B.vertex_to_add()
        if next_vertex==None:
            #The subtree can't be extend
            L[m]=max(L[m],l)
        elif promising:
            B.add_to_subtree(next_vertex)
            treat_state()
            B.undo_last_user_action()
            B.reject_vertex(next_vertex)
            treat_state()
            B.undo_last_user_action()

    assert upper_bound_strategy in ['naive', 'dist']
    n=G.num_verts()
    L=dict([(i,0) for i in range(0,n+1)])
    B=GraphBorder(G, upper_bound_strategy)
    treat_state()
    return L

def CubeGraphLeafFunction(d, upper_bound_strategy):
    r"""
    Compute the leaf function for the cube graph of dimension d

    INPUT:
        d - dimension of the hypercube

    ALGORITHM:
        Use symmetry of the cube to partion the search state and minimizing 
        the number of configuration to explore.

    EXAMPLES:
        sage: ComputeL(graphs.CubeGraph(3))
        {0: 0, 1: 0, 2: 2, 3: 2, 4: 3, 5: 2, 6: 0, 7: 0, 8: 0}
    """
    def treat_state(max_deg):
        """Explore all the possible subtree with maximum degree max_deg of G and 
        update the dictionnary L to keep track of the maximum.

        Branchs with including/excluding a vertex of the subtree.
        """
        m=B.subtree_size
        l=B.subtree_num_leaf()
        promising=sum([L[i]<B.leaf_potential(i) for i in range(m,n+1-B.num_rejected)])>0
        next_vertex=B.vertex_to_add()
        if next_vertex==None:
            #The subtree can't be extend
            L[m]=max(L[m],l)
        elif promising:
            degree=B.add_to_subtree(next_vertex)
            if degree<=i:
                treat_state(max_deg)
            B.undo_last_user_action()
            B.reject_vertex(next_vertex)
            treat_state(max_deg)
            B.undo_last_user_action()

    #Number of vertices in the biggest induced snake in cube
    #See http://ai1.ai.uga.edu/sib/sibwiki/doku.php/records
    snake_in_the_box={1: 2, 2: 3, 3: 5, 4: 8, 5: 14, 6: 27, 7: 51, 8: 99}
    base_vertex='0'*d
    star_vertices=['0'*i + '1' + '0'*(d-i-1) for i in range(d)]
    extension_vertex='1'+'0'*(d-2)+'1'
    G=graphs.CubeGraph(d)
    n=G.num_verts()
    L=dict([(i,0) for i in range(n+1)])
    #Initialization for small value
    L[2]=2
    for i in range(3,d+2):
        L[i]=i-1
    #Initialization according to snake in the box
    if d<=8:
        for i in range(2,snake_in_the_box[d]):
            L[i]=2
    else:
        raise ValueError, "d is too big, no chance of sucess"

    for i in range(d,2,-1):
        #Initialization of a starting configuration with a i-pode
        B=GraphBorder(G, upper_bound_strategy)
        B.add_to_subtree(base_vertex)
        for j in range(d):
            if j<i:
                B.add_to_subtree(star_vertices[j])
            else:
                B.reject_vertex(star_vertices[j])
        if not i==d:
            B.add_to_subtree(extension_vertex)
        treat_state(i)
        print "Exploration for %s-pode complete at %s" %(i, str(datetime.now()))
        name = "L-dict-after-"+str(i)+"-pode.sobj"
        save(L, name)
        print "%s saved" %name
    return L
