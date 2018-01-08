load('flis_configuration.py')

class SearchTree(object):

    def __init__(self, configuration):
        self.root = configuration
        v = self.root.vertex_to_add()
        if v != None:
            self.left = deepcopy(configuration)
            self.left.include_vertex(v)
            self.left = SearchTree(self.left)
            self.right = deepcopy(configuration)
            self.right.exclude_vertex(v)
            self.right = SearchTree(self.right)
        else:
            self.left = None
            self.right = None

    def digraph(self):
        if self.left != None:
            left = self.left.digraph()
            right = self.right.digraph()
            G = left.union(right)
            G.add_vertex(self.root)
            G.add_edge(self.root, self.left.root, 'include')
            G.add_edge(self.root, self.right.root, 'exclude')
            return G
        else:
            return DiGraph([[self.root],[]])

    def plot(self, node_labels='graph', edge_labels=None):
        assert node_labels in ['graph', 'stab_card']
        assert edge_labels in [None]
        P = Poset(self.digraph())
        if node_labels == 'graph':
            view(P)
        elif node_labels == 'stab_card':
            raise NotImplementedError

