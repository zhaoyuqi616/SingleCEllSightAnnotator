from cell_annotator.utils.scoring import rank_candidates


def test_rank_candidates():
    marker_db = [
        {
            "cell_type": "T cell",
            "species": "human",
            "positive_markers": ["CD3D", "CD3E", "IL7R"],
            "supporting_markers": [],
            "negative_markers": ["MS4A1"],
        },
        {
            "cell_type": "B cell",
            "species": "human",
            "positive_markers": ["MS4A1", "CD79A"],
            "supporting_markers": [],
            "negative_markers": ["CD3D"],
        },
    ]

    res = rank_candidates(["CD3D", "CD3E", "IL7R"], marker_db)
    assert res[0]["cell_type"] == "T cell"
