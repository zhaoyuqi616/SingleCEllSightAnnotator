from __future__ import annotations
from langgraph.graph import StateGraph, START, END

from .state import AnnotationState
from .nodes.ingest import ingest_input
from .nodes.validate import validate_schema
from .nodes.normalize import normalize_genes
from .nodes.qc import cluster_qc
from .nodes.retrieve import retrieve_structured_candidates
from .nodes.score import score_candidates, ambiguity_router
from .nodes.adjudicate import llm_adjudicate
from .nodes.review import human_review
from .nodes.finalize import finalize_annotation
from .nodes.persist import persist_outputs


def build_graph():
    workflow = StateGraph(AnnotationState)

    workflow.add_node("ingest_input", ingest_input)
    workflow.add_node("validate_schema", validate_schema)
    workflow.add_node("normalize_genes", normalize_genes)
    workflow.add_node("cluster_qc", cluster_qc)
    workflow.add_node("retrieve_structured_candidates", retrieve_structured_candidates)
    workflow.add_node("score_candidates", score_candidates)
    workflow.add_node("llm_adjudicate", llm_adjudicate)
    workflow.add_node("human_review", human_review)
    workflow.add_node("finalize_annotation", finalize_annotation)
    workflow.add_node("persist_outputs", persist_outputs)

    workflow.add_edge(START, "ingest_input")
    workflow.add_edge("ingest_input", "validate_schema")
    workflow.add_edge("validate_schema", "normalize_genes")
    workflow.add_edge("normalize_genes", "cluster_qc")
    workflow.add_edge("cluster_qc", "retrieve_structured_candidates")
    workflow.add_edge("retrieve_structured_candidates", "score_candidates")

    workflow.add_conditional_edges(
        "score_candidates",
        ambiguity_router,
        {
            "llm": "llm_adjudicate",
            "finalize": "finalize_annotation",
        },
    )

    workflow.add_edge("llm_adjudicate", "human_review")
    workflow.add_edge("human_review", "finalize_annotation")
    workflow.add_edge("finalize_annotation", "persist_outputs")
    workflow.add_edge("persist_outputs", END)

    return workflow.compile()
