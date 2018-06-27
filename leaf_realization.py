load('flis_graphs.py')


class LeafClassification(object):
    r"""
    Classify a family of graphs by leaf function

    INPUT:

    - ``family``: A iterable containers of graphs.

    """

    def __init__(self, family):
        self.family = family
        self.classified = False
        self.classes = None
        self._classify()

    def _classify(self, algorithm='tree'):
        r"""
        Classify the graph by leaf function
        """
        if not self.classified:
            self.classes = dict()
            for G in self.family:
                lf = FLISSolver(G, algorithm=algorithm).leaf_map()
                lf = tuple(lf.values())
                if self.classes.has_key(lf):
                    self.classes[lf].append(G)
                else:
                    self.classes[lf]=[G]
            self.classified = True

    def number_of_classes(self):
        r"""
        Returns the number differents leaf function for the family
        """
        return len(self.classes.keys())

    def average_class_size(self):
        r"""
        Returns the average number of elements by classes
        """
        total = sum(len(L) for L in self.classes.values())
        return float(total)/float(self.number_of_classes())


#--------------------------------------------------
#------------Graph recognition---------------------
#--------------------------------------------------

def is_k_caterpillar(G, k):
    r"""
    Check if a graph is k-caterpillar

    A graph is k-caterpillar if after removing k time the leaves you have
    a chain graph

    0-caterpillar is equivalent to a chain graph
    1-caterpillar is equivalent to caterpillar graph
    2-caterpillar is equivalent to lobster graph

    EXAMPLE::
    sage: is_k_caterpillar(Graph([(0, 1), (1, 2), (2, 3)]), 0)
    True
    sage: is_k_caterpillar(graphs.BalancedTree(2, 3), 1)
    False
    sage: is_k_caterpillar(graphs.BalancedTree(2, 2), 1)
    True
    sage: is_k_caterpillar(Graph([(0, 1), (1, 2), (2, 3), (3, 4)]), 1)
    True
    sage: is_k_caterpillar(Graph([(0, 1), (1, 2)]), 1)
    True
    sage: is_k_caterpillar(graphs.BalancedTree(2, 3), 2)
    True
    sage: is_k_caterpillar(graphs.BalancedTree(2, 4), 2)
    False
    sage: is_k_caterpillar(Graph([(0,1),(1,2),(2,3)]), 2)
    True
    sage: is_k_caterpillar(Graph(1), 2)
    True
    """
    assert k >= 0
    assert G.is_tree(), "G is not a tree"
    G = G.copy()
    #Removing the leaves k times
    for _ in range(k):
        leaves = []
        for v in G.vertex_iterator():
            if G.degree(v) == 1:
                leaves.append(v)
        G.delete_vertices(leaves)
    if G.num_verts() == 0:
        return True
    else:
        chain = Graph(1)
        chain.add_edges([(i,i+1) for i in range(G.num_verts() - 1)])
        return G.is_isomorphic(chain)

#--------------------------------------------------
#---------k-prefix normal word---------------------
#--------------------------------------------------

from itertools import product, combinations

def num_occurrences(word, letter):
    r"""
    Returns the number of occurrences of ``letter`` in ``word``.

    EXAMPLE::

        sage: num_occurrences(Word('01001'), '0')
        3
    """
    return sum(1 for wi in word if wi == letter)

def letter_complexity(word, letter, n):
    r"""
    Returns the ``letter`` complexity of ``word`` for ``n``.

    Let `a` be a letter, `w` be a word and `n` be a natural number. Then the
    `a`-complexity of `w` for `n` is the maximum number of occurrences of the
    letter `a` in any factor of length `n` of `w`.

    NOTE:

        When `a = 1`, this corresponds to the `F_1` function in the paper of
        Burcsi and al.

    EXAMPLE::

        sage: letter_complexity(Word('01001'), '1', 3)
        1
    """
    return max(num_occurrences(u, letter) for u in word.factor_iterator(n))

def is_k_prefix_normal(word, k):
    r"""
    Returns True if and only if ``word`` is prefix-normal.

    A word `w` is called prefix-normal if for any length `n`, the number of 1's
    in `\\pref_n(w)` is the maximal in comparison with all factors of length
    `n`.

    EXAMPLE::

        sage: is_k_prefix_normal(Word('1101011011'), 0)
        False
        sage: is_k_prefix_normal(Word('1101101011'), 0)
        True
        sage: is_k_prefix_normal(Word([1,1,0,1,0,1,1,0,1,1]), 0)
        False
        sage: is_k_prefix_normal(Word([1,1,0,1,1,0,1,0,1,1]), 0)
        True
        sage: is_k_prefix_normal(Word([1,1,0,1,2]),0)
        False
    """
    alphabet = sorted(word.letters())
    if alphabet == [0,1]:
        one = 1
    elif alphabet == ['0','1']:
        one = '1'
    else:
        return False
    return all(letter_complexity(word, one, len(p)) - num_occurrences(p, one) <= k\
               for p in word.prefixes_iterator())
