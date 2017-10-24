.PHONY: test

test:
	sage -t README.rst
	sage -t configuration.py
	sage -t flis_graphs.py
	sage -t flis_trees.py
