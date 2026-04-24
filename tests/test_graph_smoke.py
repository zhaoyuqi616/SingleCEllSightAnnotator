from cell_annotator.graph import build_graph


def test_graph_builds():
    app = build_graph()
    assert app is not None
