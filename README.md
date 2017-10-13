# Fully leafed induced subtrees

This respository contains code for computing the leaf function of a graph. It
was used to compute some values presented in an an article titled *Fully leafed
induced subtrees*, that will be submitted to Discrete Mathematics & Theoretical
Computer Science.

## Background

Given a simple graph `G = (V,E)` and `T` a subset of `V`, we say that `T` is a
*fully leafed induced subtree* of size `i` if the following conditions are
satisfied:

1. `|T| = i` (`T` is of size `i`);
2. The subgraph `G[T]` induced by `T` is a tree;
3. The number of leaves of `G[T]` is maximum, i.e. there is no other induced
   subtree of size `i` having strictly more leaves than `G[T]`.

The *leaf function* of a graph `G` of `n` vertices, denoted by `L_G`, is the
function whose domain is `{0,1,...,n}` and such that `L_G(i)` is the number of
leaves of a fully leafed induced subtree of size `i`.

Since computing the leaf function is NP-hard for general graphs, the program is
expected to run for a long time if the graph has medium or large size. For
instance, it took about 3 days of computation to obtain the function for
the hypercube graph of dimension 6.

## Dependencies

- [Sagemath](http://www.sagemath.org/). One needs to install Sagemath to make
  it work.

## How to use

The main function is `ComputeL(G)`. This function compute the leaf function of
a general graph `G`. Special optimization can be used for particular cases
using the optional parameter `algorihtm`.  The available options are:

- `general`: uses the branch and bound algorithm
- `tree`: uses a O(n^3) dynamic programming algorithm
- `cube`: uses a specialization of the general branch and bound algorihtm for cube graph.

Below are some examples that can be reproduced once Sagemath is started and the
two Python files loaded:

```python
sage: ComputeL(graphs.CompleteGraph(7))[0]
{0: 0, 1: 0, 2: 2, 3: None, 4: None, 5: None, 6: None, 7: None}
sage: ComputeL(graphs.CycleGraph(10))[0]
{0: 0, 1: 0, 2: 2, 3: 2, 4: 2, 5: 2, 6: 2, 7: 2, 8: 2, 9: 2, 10: None}
sage: ComputeL(graphs.WheelGraph(11))[0]
{0: 0, 1: 0, 2: 2, 3: 2, 4: 3, 5: 4, 6: 5, 7: 2, 8: 2, 9: 2, 10: None, 11: None}
sage: ComputeL(graphs.CompleteBipartiteGraph(7,5))[0]
{0: 0, 1: 0, 2: 2, 3: 2, 4: 3, 5: 4, 6: 5, 7: 6, 8: 7, 9: None, 10: None, 11: None, 12: None}
sage: ComputeL(graphs.PetersenGraph())[0]
{0: 0, 1: 0, 2: 2, 3: 2, 4: 3, 5: 3, 6: 4, 7: 3, 8: None, 9: None, 10: None}
sage: ComputeL(graphs.CubeGraph(3), algorihtm = 'cube')[0]
{0: 0, 1: 0, 2: 2, 3: 2, 4: 3, 5: 2, 6: None, 7: None, 8: None}
sage: ComputeL(graphs.BalancedTree(2, 2), algorihtm = 'tree')[0]
{0: 0, 1: 0, 2: 2, 3: 2, 4: 3, 5: 3, 6: 3, 7: 4}
```

License
=======

All files in this repository are subject to the [GPLv3
license](https://www.gnu.org/licenses/gpl-3.0.en.html).
