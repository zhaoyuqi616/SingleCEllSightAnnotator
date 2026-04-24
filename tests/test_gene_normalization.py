from cell_annotator.utils.gene_normalization import normalize_gene_symbol


def test_normalize_gene_symbol():
    assert normalize_gene_symbol("FOXP-3") == "FOXP3"
    assert normalize_gene_symbol("PD-L1") == "CD274"
    assert normalize_gene_symbol("cd3d") == "CD3D"
