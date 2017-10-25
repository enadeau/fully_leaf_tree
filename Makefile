.PHONY: test

test:
	sage -t README.rst
	sage -t flis_configuration.py
	sage -t flis_graphs.py
	sage -t flis_trees.py
	sage -t graphs_util.py
