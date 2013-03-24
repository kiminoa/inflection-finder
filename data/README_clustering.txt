Open Refine Clustering Algorithms

Nearest Neighbor

    Levenshtein
    --> r=1,2 b=6 ok results, slightly better for radius=2.0

(*) PPM
    --> r=1 b=5 best results among Open Refine's clustering algorithms for the 20 line sample
    --> r=1 b=4 better results for a clustering of the complete lexicon
	- correctly identified 

Key Collision

    ngram-fingerprint (ngram=2)
    --> good for identifying potential syllabic metathesis; not good for discovering inflection candidates

    double-metaphone
    --> clusters are way too broad

Python Module Clustering Algorithms

    import cluster; HierarchicalClustering
    --> lambda x,y: len(str(x) & str(y)) - algorithm is probably naïve? Definitely not doing the trick.
