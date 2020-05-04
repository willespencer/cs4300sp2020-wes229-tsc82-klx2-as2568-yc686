from inv_idx import *
from idf import *
import math
import numpy as np


def compute_idf(inv_idx, n_docs, min_df=10, max_df_ratio=0.95):
    """ Compute term IDF values from the inverted index.
    Words that are too frequent or too infrequent get pruned.

    Hint: Make sure to use log base 2.

    Arguments
    =========

    inv_idx: an inverted index as above

    n_docs: int,
        The number of documents.

    min_df: int,
        Minimum number of documents a term must occur in.
        Less frequent words get ignored. 
        Documents that appear min_df number of times should be included.

    max_df_ratio: float,
        Maximum ratio of documents a term can occur in.
        More frequent words get ignored.

    Returns
    =======

    idf: dict
        For each term, the dict contains the idf value.

    """

    # YOUR CODE HERE
    idf = {}
    for word, lst in inv_idx.items():
        if min_df <= len(lst) and len(lst) <= (max_df_ratio * n_docs):
            idf[word] = math.log2(n_docs / (1 + len(lst)))
    return idf

def compute_doc_norms(index, idf, n_docs):
    """ Precompute the euclidean norm of each document.

    Arguments
    =========

    index: the inverted index as above

    idf: dict,
        Precomputed idf values for the terms.

    n_docs: int,
        The total number of documents.

    Returns
    =======

    norms: np.array, size: n_docs
        norms[i] = the norm of document i.
    """
    summation = np.zeros(n_docs)
    for key, lst in index.items():
        for (doc_id, count) in lst:
            try:
                summation[doc_id] += (count*idf[key])**2
            except KeyError:
                pass
    norm_lst = np.array(list(map(lambda x: math.sqrt(x), list(summation))))
    return norm_lst

def main():
    global inv_idx

    idf = compute_idf(inv_idx, 6598, min_df=10, max_df_ratio=0.15)
    inv_idx = {key: val for key, val in inv_idx.items() if key in idf} 
    doc_norms = compute_doc_norms(inv_idx, idf, 6598)

    f = open("inv_idx_new.py", "w")
    f.write("inv_idx = " + repr(inv_idx) + "\n")
    f.close()      

    g = open("idf_new.py", "w")
    g.write("idf = " + repr(idf) + "\n")
    g.close()

    h = open("doc_norms_new.py", "w")
    h.write("import numpy as np\n")
    h.write("doc_norms = np.array([")
    for i in range(len(doc_norms)):
        h.write(repr(doc_norms[i]))
        if i != len(doc_norms) - 1:
            h.write(",\n")
    h.write("])")
    h.close()



    # np.savetxt("doc_norms_new.py", doc_norms, fmt = "%f", delimiter=", ", newline=",", header="doc_norms = [", footer="]")
    # h = open("doc_norms_new.py", "w")
    # h.write(np.array_str(doc_norms, max_line_width=20))
    # h.close()

# main()

