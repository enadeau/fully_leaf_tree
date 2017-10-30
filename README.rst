Fully leafed induced subtrees
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This respository contains code for computing the leaf function of a graph. The
main algorithms used are described and analyzed in an article titled *Fully
leafed induced subtrees* (https://arxiv.org/abs/1709.09808). It was also used
to compute the leaf function of classical graphs.

Background
==========

Given a simple graph `G = (V,E)` and `T` a subset of `V`, we say that `T` is a
*fully leafed induced subtree* of size `i` if the following conditions are
satisfied:

1. `|T| = i` (`T` is of size `i`);
2. The subgraph `G[T]` induced by `T` is a tree;
3. The number of leaves of `G[T]` is maximum, i.e. there is no other induced
   subtree of size `i` having strictly more leaves than `G[T]`.

The *leaf function* of a graph `G` of `n` vertices, denoted by `L_G`, is the
function whose domain is `\{0,1,...,n\}` and such that `L_G(i)` is the number
of leaves of a fully leafed induced subtree of size `i`.

Since computing the leaf function is NP-hard for general graphs, the program is
expected to run for a long time if the graph has medium or large size. For
instance, it took about 3 days of computation to obtain the function for the
hypercube graph of dimension 6.

Dependencies
============

Currently, one must have `Sagemath <http://www.sagemath.org>`__ installed to
run the program. It is mostly used to have quick access to classical graphs. In
the future, we intend intend to remove the dependency and port the program to C
or C++.

How to use
==========

The main class is ``FLISSolver(G)``. This class compute the leaf function
of a general graph ``G``. Special optimization can be used for particular cases
using the optional parameter ``algorithm``. The available options are:

- ``'general'``: The branch and bound algorithm for general graphs;
- ``'tree'``: A polynomial time algorithm based on dynamic programming;
- ``'cube'``: A specialized branch and bound algorithm exploiting the
  symmetries of the hypercubes.

This class can also compute examples of fully leafed tree with
``FLISSolver(G).fully_leafed_subtrees(i)`` for subtrees of size ``i``.

Below are some examples that can be reproduced once Sagemath is started and the
three Python files loaded::

    sage: load('flis_graphs.py')
    sage: FLISSolver(graphs.CompleteGraph(7)).leaf_map()
    {0: 0, 1: 0, 2: 2, 3: None, 4: None, 5: None, 6: None, 7: None}
    sage: FLISSolver(graphs.CycleGraph(10)).leaf_map()
    {0: 0, 1: 0, 2: 2, 3: 2, 4: 2, 5: 2, 6: 2, 7: 2, 8: 2, 9: 2, 10: None}
    sage: FLISSolver(graphs.WheelGraph(11)).leaf_map()
    {0: 0, 1: 0, 2: 2, 3: 2, 4: 3, 5: 4, 6: 5, 7: 2, 8: 2, 9: 2, 10: None, 11: None}
    sage: FLISSolver(graphs.CompleteBipartiteGraph(7,5)).leaf_map()
    {0: 0, 1: 0, 2: 2, 3: 2, 4: 3, 5: 4, 6: 5, 7: 6, 8: 7, 9: None, 10: None, 11: None, 12: None}
    sage: FLISSolver(graphs.PetersenGraph()).leaf_map()
    {0: 0, 1: 0, 2: 2, 3: 2, 4: 3, 5: 3, 6: 4, 7: 3, 8: None, 9: None, 10: None}
    sage: FLISSolver(graphs.CubeGraph(3), algorithm='cube').leaf_map()
    {0: 0, 1: 0, 2: 2, 3: 2, 4: 3, 5: 2, 6: None, 7: None, 8: None}
    sage: FLISSolver(graphs.BalancedTree(2, 2), algorithm='tree').leaf_map()
    {0: 0, 1: 0, 2: 2, 3: 2, 4: 3, 5: 3, 6: 3, 7: 4}

Below are additional examples with pictures. A ternary tree::

    sage: load('flis_graphs.py')
    sage: B = graphs.BalancedTree(3, 2)
    sage: S = FLISSolver(B, algorithm='tree')
    sage: G = graphics_array([plot_subgraph(B, S.fully_leafed_subtrees(i)[0]) for i in range(14)], 2, 7)
    sage: G.show(figsize=[14,4])

.. image:: images/flis-balanced-tree.png

And the Petersen graph::

    sage: load('flis_graphs.py')
    sage: P = graphs.PetersenGraph()
    sage: S = FLISSolver(P, algorithm='general')
    sage: G = graphics_array([plot_subgraph(P, S.fully_leafed_subtrees(i)[0]) for i in range(8)], 2, 4)
    sage: G.show(figsize=[14,7])

.. image:: images/flis-petersen.png

License
=======

All files in this repository are subject to the `GPLv3 license
<https://www.gnu.org/licenses/gpl-3.0.en.html>`__.
