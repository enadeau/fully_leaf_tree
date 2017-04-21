from collections import deque

def ComputeL(G):
    """Compute the maximal number of leaves that can be obtain in a tree
     wich is an induced subgraph of size m of G for each m between 0 and
     |G|.
    
    INPUT:
        G - a graph, in wich the vertices are 0,1,2,...,n-1

    OUTPUT:
        A dictionnary L that associate to the number of vertices, the
        maximal number of leaves.
    """ 
    global L
    global vertice
    vertice = G.vertices()
    n=G.num_verts()
    L=dict([(i,0) for i in range(0,n+1)])
    ComputeLRecursive(G,0,n,set())
    return L

def ComputeLRecursive(G,i,n,V_add):
    """Explore all the possible subgraph of G and update the dictionnary L 
    to keep track of the maximum.
    
    INPUTS:
        G - the graph of the connected component of the original graph 
        (without the rejected vertices) containing the vertices of V_add
        i - the vertex of G, the procedure has to branch on.
        n - The number of vertices of the graph it explores
        V_add - A set of vertices that are already included in the solution
        
    OUTPUT:
        Branchs with including/excluding a vertex i of the solution. 
        When at the end of the research tree, updates a global dictonnary 
        L create by ComputeL(G)
    """
    global L
    (l,connexity_lack)=subgraphStat(G,V_add)
    acyclic=(l!=-1)
    m=len(V_add)
    promising=sum([L[m]<l*(connexity_lack==0)]+[L[m+j]<l+j-connexity_lack for j in range(1,G.num_verts()-m)])>0
    if i==n and acyclic and connexity_lack==0:
        #All vertices are either included are excluded
        L[m]=max(L[m],l)
    elif acyclic and promising and i<n:
        #The branch is valid and promising
        if vertice[i] in G.vertices():
            #The vertex is in the connected component G
            V_add.add(vertice[i])
            ComputeLRecursive(G,i+1,n,V_add)
            V_add.remove(vertice[i])
            neighbors_of_i=G.neighbors(vertice[i])
            G.delete_vertex(vertice[i])
            connected_component=G
            connectable=True
            if len(V_add)>0:
                for v in V_add: break #select an element of V_add
                C=G.connected_component_containing_vertex(v)
                connectable=V_add.issubset(C)
                if len(C)<G.num_verts():
                    connected_component=G.subgraph(vertices=C,algorithm="add")
            if connectable:
                #rejecting i does not separate V_add
                ComputeLRecursive(connected_component,i+1,n,V_add)
            G.add_vertex(vertice[i])
            for j in neighbors_of_i:
                G.add_edge(vertice[i],j)
        else:
            #The vertex is not in the connected component G
            ComputeLRecursive(G,i+1,n,V_add)

def subgraphStat(G,V):
    """Compute some statistics about the induced subgraph of G by V using
    an adaptation of the breadth-first search.
    
    INPUTS:
        G - a graph
        V - a subset of vertices
        
    OUTPUTS:
        l - number of leaves of the induced subgraph if it is a 
        forest, -1 if not.
        connexity_lack - A lower bound on the increase in the number of
        internals vertices require to connect the induced subgraph if it
        is a forest with value 0 iff the subforest is a tree. -1 if the
        induced subgraph is not a forest"""
    if len(V)==0:
        return 0,0

    visited=dict()
    number_of_component=0
    l=0
    for v in V:
        visited[v]=False
    while v!=None:
        #Explore a connected component
        number_of_component+=1
        Q=deque([v])
        while len(Q)>0: 
            v=Q.popleft()
            if visited[v]:
                #The subgraph is not acyclic
                return -1, -1
            visited[v]=True
            degree=0
            for son in G.neighbor_iterator(v):
                if son in V:
                    degree+=1
                    if not visited[son]:
                        Q.append(son)
            if degree==1:
                #The vertices is a leaf
                l+=1
        #Search for a new connected component
        v=None
        for s in V: 
            if not visited[s]:
                v=s
                break

    return l,int(number_of_component>1)
