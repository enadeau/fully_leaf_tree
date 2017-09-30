# Fully leafed induced subtrees

This respository contains code used to compute the leaf function of graph.
The program included was used in an article titled *Fully leafed induced subtrees*,
submitted to Discrete Mathematics & Theoretical Computer Science.

Notice that it took about 3 days of computation
to obtain the function for hypercube graphs of dimension 6.

## Dependencies

- [Sagemath](http://www.sagemath.org/). One needs to install Sagemath to
  make it work.

## How to use

The two main functions are `ComputeL(G)` and `CubeGraphLeafFunction(d)`.
The first one compute the leaf function for a general graph&nbsp;*G* and similarly the second 
compute the leaf function but in an optimized way for hypercube graph of dimension&nbsp;*d*. `CubeGraphLeafFunction(d)` also returns examples of
induced subtrees that reached the maximal number of leaves.

Once Sagemath is started and the two python files loaded, we can compute the following examples:

```python
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
sage: (L, E) = CubeGraphLeafFunction(3) #L is the leaf function and E the dictionnary of examples
sage: L
{0: 0, 1: 0, 2: 2, 3: 2, 4: 3, 5: 2, 6: 0, 7: 0, 8: 0}
```

License
=======

All files in this repository are subject to the [GPLv3 license](https://www.gnu.org/licenses/gpl-3.0.en.html).
