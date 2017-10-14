.PHONY: test

test:
	sage -t graph_border.py
	sage -t induced_maximal_tree.py
	sage -t flis_trees.py
