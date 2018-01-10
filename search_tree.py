load('flis_configuration.py')

class SearchTree(object):

    def __init__(self, configuration, method='std'):
        assert method in ['std', 'stab', 'stab2']
        if method in ['stab', 'stab2']:
            assert isinstance(configuration, StabilizedConfiguration)
        self.root = configuration
        v = self.root.vertex_to_add()
        if v != None:
            #Inclusion side
            self.left = copy(configuration)
            self.left.include_vertex(v)
            if method == 'stab2':
                for u in self.left.manual_rejection:
                    for w in self.left.vertex_orbit(u):
                        if self.left.vertex_status[w][0] == self.left.BORDER:
                            self.left.exclude_vertex(w)
            self.left = SearchTree(self.left, method=method)
            #Exclusion side
            self.right = copy(configuration)
            if method == 'std':
                self.right.exclude_vertex(v)
            elif method in ['stab', 'stab2']:
                for u in self.right.isometric_extension(v):
                    self.right.exclude_vertex(u)
            self.right = SearchTree(self.right, method=method)
        else:
            self.left = None
            self.right = None

    def size(self):
        r"""
        Return the number of configuration in the search tree
        """
        if self.left != None:
            return 1 + self.left.size() + self.right.size()
        else:
            return 1

    def subtree_iterator(self):
        r"""
        Iterate among all subtree in the leaves of the search tree
        """
        if self.left == None:
            yield self.root.subtree_vertices
        else:
            for a in self.left.subtree_iterator():
                yield a
            for a in self.right.subtree_iterator():
                yield a

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

    def test_property(self, test):
        r"""
        Test the property verified by the function test on all configuration
        of the search

        INPUT:

       - ``test``: A boolean function taking a configuraiton as parameter
        """
        if self.left != None:
            return test(self.root) and self.left.test_property(test) and \
                    self.right.test_property(test)
        else:
            return test(self.root)
