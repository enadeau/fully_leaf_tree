from collections import deque
import heapq

class GraphBorder():
    r"""
    Object represent a induced subtree of a graph and the surrounding of this subtree.
    The data structure also catch up a bit of the evolution of the tree over time.

    INPUT:
        G - The graph
        upper_bound_strategy - The strategy for the upper bound (either 'naive' or
            'dist')

    ATTRIBUTES:
        vertex_status: Dictionnary that store the state of each vertices with options.
        The status of a vertex v is of the form:
            - ("s",d) if v is in the subtree with degree d in the subtree;
            - ("b",p) if v is not in the subtree and is adjacent to exactly one
              vertex of the subtree which is p;
            - ("r",i) if v rejected of the subtree. If i==v the vertex was voluntary rejected
              from a potential subtree by the users. Otherwise it indicates that the addition
              of the vertex v to the subtree will form a cycle since vertex i was add to
              the subtree.
            - ("a",None) if v can eventually be add to the subtree but his addition will
              created a disconnected subgraph in the actual state (i.e v is not on the border
              of the subtree)

        graph: The graph used to induced the subtree

        num_leaf: The number of leaves of the subtree. Note that with this class a tree with only
        one vertex is consider to have one leaf but the function subtree_num_leaf makes
        the correction.

        border_size: The number of vertices in the border

        subtree_size: The number of vertices in the subtree

        num_rejected: The number of vertices that are rejected

        user_intervention_stack: Stack of the subtree vertices in the order of which the user
        explicitly specify the state (by addition or rejection). Last vertex the user acts on
        is on top.
    """

    def __init__(self, G, upper_bound_strategy):
        r"""
        Constructor of the graph border. Initialize the state of all vertices
        to ("a", None)
        """
        self.vertex_status=dict()
        self.graph=G
        self.num_leaf=0
        self.border_size=0
        self.subtree_size=0
        self.num_rejected=0
        self.user_intervention_stack=[]
        self.subtree_vertices=[]
        self.lp_dist_valid=False
        assert upper_bound_strategy in ['naive', 'dist']
        self.upper_bound_strategy = upper_bound_strategy
        for v in G.vertex_iterator():
            self.vertex_status[v]=("a", None)
        self.border_vertex=v

    def vertex_to_add(self):
        r"""
        Return a vertex of the graph that can extend the current solution into a tree.
        Return any vertex if the subtree is empty.
        Return None if the current solution can't be extend.
        """
        if self.vertex_status[self.border_vertex][0]=="b":
            return self.border_vertex
        elif self.subtree_size==0:
            #The subtree is empty, any non rejected vertex can be add
            for v in self.vertex_status:
                if self.vertex_status[v][0]=="a":
                    return v
        else:
            #The subtree is unempty, a vertex of the border must be add
            for v in self.vertex_status:
                if self.vertex_status[v][0]=="b":
                    return v
        return None

    def add_to_subtree(self,v):
        r"""
        Add a vertex of the border to the current solution or initiate a solution
        with a first vertex.

        INPUTS:
            v - A vertex of the border or if the subtree is empty any available vertex

        OUTPUT:
            Degree of the vertex v is attached to
        """
        assert self.vertex_status[v][0]=="b" or ("b",None) not in self.vertex_status.values()
        degree=0
        for u in self.graph.neighbor_iterator(v):
            (state,info)=self.vertex_status[u]
            if state=="a":
                self.vertex_status[u]=("b",None)
                self.border_size+=1
            elif state=="s":
                degree=info+1
                self.vertex_status[u]=(state,degree)
                if info==1:
                    self.num_leaf-=1
            elif state=="b":
                self.border_size-=1
                self.num_rejected+=1
                self.vertex_status[u]=("r",v)
            #If the vertices is already rejected we do nothing
        if self.vertex_status[v][0]=="b": #The vertex extend a current solution
            self.vertex_status[v]=("s",1)
            self.border_size-=1
        else: #The vertex is the first vertex to be set to "s"
            self.vertex_status[v]=("s",0)
        self.subtree_vertices.append(v)
        self.num_leaf+=1
        self.subtree_size+=1
        self.user_intervention_stack.append(v)
        self.lp_dist_valid=False
        return degree

    def _remove_last_addition(self,v):
        r"""
        Removes the last inserted vertex v to the subtree.
        """
        for u in self.graph.neighbor_iterator(v):
            (state,info)=self.vertex_status[u]
            #Impossible that state is available
            if state=="b":
                self.vertex_status[u]=("a", None)
                self.border_size-=1
            elif state=="s":
                self.vertex_status[u]=(state,info-1)
                if info==2:
                    self.num_leaf+=1
            #At this point the state must be "r"
            elif info==v:
                self.vertex_status[u]=("b", None)
                self.num_rejected-=1
                self.border_size+=1

        self.subtree_size-=1
        if self.subtree_size>0:
            self.vertex_status[v]=("b", None)
            self.border_size+=1
        else: #We remove the last vertex from the subtree
            self.vertex_status[v]=("a",None)
        self.num_leaf-=1
        self.subtree_vertices.pop()

    def reject_vertex(self,v):
        r"""
        Sets a vertex that is not in the solution to rejected.
        When a vertex v has been rejected using this method,
        his value in vertex_status is set to ("r",v)
        """
        assert self.vertex_status[v][0]=="b" or self.subtree_size==0
        self.vertex_status[v]=("r",v)
        if self.subtree_size!=0:
            #The element we reject is on the border
            self.border_size-=1
        self.num_rejected+=1
        self.user_intervention_stack.append(v)
        self.lp_dist_valid=False

    def _unreject_last_manual_rejection(self,v):
        r"""
        Cancel the last manual rejection. Vertex v must be te last rejected vertex.
        """
        self.num_rejected-=1
        if self.subtree_size==0:
            self.vertex_status[v]=("a",None)
        else:
            self.vertex_status[v]=("b",None)
            self.border_size+=1

    def undo_last_user_action(self):
        r"""
        Undo the last user intervention which is either and addition to the subtree
        or a rejection.
        """
        v=self.user_intervention_stack.pop()
        self.lp_dist_valid=False
        if self.vertex_status[v][0]=="s":
            self._remove_last_addition(v)
        else:
            self._unreject_last_manual_rejection(v)

    def subtree_num_leaf(self):
        r"""
        Return the number of leaf in the subtree
        """
        if self.subtree_size==1:
            return 0
        else:
            return self.num_leaf

    def subtree_vertices_with_degrees(self):
        r"""
        Generates the subtree vertices with their degree 
        in pair (vertex, degree)
        """
        for v in self.subtree_vertices:
            yield (v, self.vertex_status[v][1])

    def degree(self, u, exclude='r'):
        return sum(1 for v in self.graph.neighbor_iterator(u)
                     if self.vertex_status[v][0] not in exclude)

    def non_subtree_vertices_by_distance(self):
        r"""
        Returns a partition of the non subtree vertices with respect to their
        distance from the subtree internal vertices.
        """
        vertices = []
        visited = set()
        queue = deque()
        leaves = []
        for (u,d) in self.subtree_vertices_with_degrees():
            if d > 1: queue.append((u,0))
            elif d==1: leaves.append((u,1))
        queue.extend(leaves)
        #This if is used to speed up vertex_to_add
        if queue:
            self.border_vertex = queue[0][0]
        layer = []
        prev_d = 0
        while queue:
            (u, d) = queue.popleft()
            if u not in visited:
                if 1 <= prev_d and prev_d < d:
                    vertices.append(layer)
                    layer = []
                if self.vertex_status[u][0] != 's':
                    layer.append(u)
                prev_d = d
                visited.add(u)
                for v in self.graph.neighbor_iterator(u):
                    if self.vertex_status[v][0] != 'r' and not v in visited:
                        queue.append((v,d+1))
        vertices.append(layer)
        return vertices

    def leaf_potential_dist(self,i):
        assert self.subtree_size > 2
        if self.lp_dist_valid:
            if self.lp_dist_dict.has_key(i):
                return self.lp_dist_dict[i]
            else: return 0
        #Else we compute the dictionnary
        current_size = self.subtree_size
        current_leaf = self.num_leaf
        self.lp_dist_dict = dict()
        self.lp_dist_dict[current_size]=current_leaf
        vertices_by_dist = self.non_subtree_vertices_by_distance()
        max_size = self.subtree_size + sum(len(layer) for layer in vertices_by_dist)
        #Adding the leaf creator
        for _ in vertices_by_dist[0]:
            current_size += 1
            current_leaf += 1
            self.lp_dist_dict[current_size] = current_leaf
        current_dist = 1
        priority_queue = [(-self.degree(u), u) for u in vertices_by_dist[0]]
        if not priority_queue and len(vertices_by_dist) >= 2:
            priority_queue = [(-self.degree(u), u) for u in vertices_by_dist[1]]
            current_dist = 2
        heapq.heapify(priority_queue)
        while current_size < max_size:
            (d, u) = heapq.heappop(priority_queue)
            d = -d
            current_size += 1
            self.lp_dist_dict[current_size] = current_leaf
            if current_dist < len(vertices_by_dist):
                for v in vertices_by_dist[current_dist]:
                    heapq.heappush(priority_queue, (-self.degree(v), v))
            current_dist += 1
            current_leaf -= 1
            for _ in range(d-1):
                if current_size==max_size:
                    break
                current_size += 1
                current_leaf += 1
                self.lp_dist_dict[current_size] = current_leaf
        self.lp_dist_valid = True
        return self.leaf_potential_dist(i)

    def leaf_potential_weak(self,i):
        r"""
        Evaluate a maximal potential number of leaf for a subtree of i
        vertices build from the current subtree

        The size of the tree must be bigger than the current tree size.
        """
        if self.subtree_size<=i and i<=self.subtree_size+self.border_size:
            return self.num_leaf+i-self.subtree_size
        elif i>self.subtree_size+self.border_size:
            return self.num_leaf+i-self.subtree_size-1

    def leaf_potential(self,i):
        assert i>=self.subtree_size, "The size of the tree is not big enough"
        if self.upper_bound_strategy == 'naive' or self.subtree_size <= 2:
            return self.leaf_potential_weak(i)
        else:
            return self.leaf_potential_dist(i)

    def plot(self):
        r"""
        Plot a graph representation of the graph bordrer with following convention for
        node colors:
            green: The node is in the subtre
            yellow: The vertex is on the border
            red: The vertex is rejected by an other vertex
            black:The vertex is rejected by the user
            blue: If the vertex is available

        The vertex of the induced subtree are in green
        """
        vertex_color={"blue": [], "yellow": [], "black": [], "red": [], "green": []} 
        for v in self.graph.vertex_iterator():
            (state,info)=self.vertex_status[v]
            if state=="a":
                vertex_color["blue"].append(v)
            elif state=="b":
                vertex_color["yellow"].append(v)
            elif state=="s":
                vertex_color["green"].append(v)
            else: #state is "r"
                if info==v:
                    vertex_color["black"].append(v)
                else:
                    vertex_color["red"].append(v)
        
        tree_edge=[]
        for (u,v,label) in self.graph.edge_iterator():
            if self.vertex_status[v][0]=="s"==self.vertex_status[u][0]:
                tree_edge.append((u,v))

        return self.graph.plot(vertex_colors=vertex_color, edge_colors={"green": tree_edge})

    def __repr__(self):
        return "subtree_size: %s, num_leaf: %s, border_size: %s, num_rejected: %s," %(self.subtree_size,self.num_leaf, self.border_size, self.num_rejected)

class GraphBorderForCube(GraphBorder):
    r"""
    Specilization of graph border classes for cube
    """
    def __init__(self, G, upper_bound_strategy, max_deg):
        GraphBorder.__init__(self, G, upper_bound_strategy)
        self.max_deg = max_deg

    def degree(self, u, exclude='r'):
        r"""
        Compute the degree considering the maximum degree that is allowed
        """
        real_deg = sum(1 for v in self.graph.neighbor_iterator(u)
                     if self.vertex_status[v][0] not in exclude)
        return min(self.max_deg, real_deg)


