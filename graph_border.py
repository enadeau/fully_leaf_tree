class GraphBorder():
    r"""
    Object represent a induced subtree of a graph and the surrounding of this subtree.
    The data structure also catch up a bit of the evolution of the tree over time.
    
    ATTRIBUTES:
        vertex_status: Dictionnary that store the state of each vertices with options.
        The status of a vertex v is of the form:
            - ("s",d) if v is in the subtree with degree d in the subtree;
            - ("b",None) if v is not in the subtree and is adjacent to exactly one 
              vertex of the subtree;
            - ("r",i) if v rejected of the subtree. If i==v the vertex was voluntary rejected
              from a potential subtree by the users. Otherwise it indicates that the addition
              of the vertex v to the subtree will form a cycle since vertex i was add to
              the subtree.
            - ("a",None) if v can eventually be add to the subtree but his addition will
              created a disconnected subgraph in the actual state (i.e v is not on the border
              of the subtree)
        
        graph: The graph used to induced the subtree

        leaf: The number of leaves of the subtree. Note that with this class a tree with only
        one vertex is consider to have one leaf

        subtree_stack: Stack of the subtree vertices in the order they where added to the tree.
    """

    def __init__(self, G):
        r"""
        Constructor of the graph border. Initialize the state of all vertices
        to ("a", None)
        """
        self.vertex_status=dict()
        self.graph=G
        self.leaf=0
        self.subtree_stack=[]
        for v in G.vertex_iterator():
            self.vertex_status[v]=("a", None)

    def vertex_to_add(self):
        r"""
        Return a vertex of the graph that can extend the current solution into a tree.
        Return any vertex if the subtree is empty.
        Return None if the current solution can't be extend.
        """
        for v in self.vertex_status:
            if self.vertex_status[v][0]=="b":
                return v
        for v in self.vertex_status:
            if self.vertex_status[v][0]=="a":
                return v
        return None

    def add_to_subtree(self,v):
        r"""
        Add a vertex of the border to the current solution or initiate a solution
        with a first vertex.

        INPUTS:
            v - A vertex of the border or if the subtree is empty or any vertex if the
                the subtree is empty.
        """
        assert self.vertex_status[v][0]=="b" or ("b",None) not in self.vertex_status.values()
        for u in self.graph.neighbor_iterator(v):
            (state,info)=self.vertex_status[u]
            if state=="a":
                self.vertex_status[u]=("b",None)
            elif state=="s":
                self.vertex_status[u]=(state,info+1)
                if info==1:
                    self.leaf-=1
            elif state=="b":
                self.vertex_status[u]=("r",v)
            #If the vertices is already rejected we do nothing
        if self.vertex_status[v][0]=="b": #The vertex extend a current solution
            self.vertex_status[v]=("s",1)
        else: #The vertex is the first vertex to be set to "s"
            self.vertex_status[v]=("s",0)
        self.subtree_stack.append(v)
        self.leaf+=1

    def remove_last_addition(self):
        r"""
        Removes the last inserted vertex to the subtree.
        """
        assert len(self.subtree_stack)>0
        v=self.subtree_stack.pop()
        for u in self.graph.neighbor_iterator(v): 
            (state,info)=self.vertex_status[u]
            #Impossible that state is available
            if state=="b":
                self.vertex_status[u]=("a", None)
            elif state=="s":
                self.vertex_status[u]=(state,info-1)
                if info==2:
                    self.leaf+=1
            #At this point the state must be "r"
            elif info==v:
                self.vertex_status[u]=("b", None)
        if len(self.subtree_stack)>0:
            self.vertex_status[v]=("b", None)
        else: #We remove the last vertex from the subtree
            self.vertex_status[v]=("a",None)
        self.leaf-=1

    def reject_vertex(self,v):
        r"""
        Sets a vertex that is not in the solution to rejected.
        When a vertex v has been rejected using this method,
        his value in vertex_status is set to ("r",v)
        """
        assert self.vertex_status[v][0]!="s"
        self.vertex_status[v]=("r",v)
