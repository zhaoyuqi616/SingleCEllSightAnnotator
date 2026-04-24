from __future__ import annotations
from langchain_openai import ChatOpenAI
from ..config import settings
from ..state import AnnotationState
from ..schemas import AdjudicationOutput
from ..prompts import ADJUDICATION_SYSTEM_PROMPT, ADJUDICATION_USER_TEMPLATE
from ..utils.evidence import format_candidate_scores


def llm_adjudicate(state: AnnotationState) -> AnnotationState:
    if not settings.openai_api_key:
        logs = state.get("logs", [])
        logs.append("OPENAI_API_KEY not set; skipping LLM adjudication and relying on structured scoring only")
        state["logs"] = logs
        return state

    llm = ChatOpenAI(
        model=settings.openai_model,
        api_key=settings.openai_api_key,
        temperature=0,
    )

    structured_llm = llm.with_structured_output(AdjudicationOutput)

    for cluster, result in state["per_cluster_results"].items():
        if result.get("confidence_band") == "high" and not result.get("review_required", False):
            continue

        prompt = ADJUDICATION_USER_TEMPLATE.format(
            cluster_id=cluster,
            species=state.get("species", "human"),
            tissue=state.get("tissue", "not provided"),
            disease_context=state.get("disease_context", "not provided"),
            normalized_markers=", ".join(result.get("normalized_markers", [])),
            candidate_scores=format_candidate_scores(result.get("candidate_scores", [])),
        )

        response = structured_llm.invoke([
            {"role": "system", "content": ADJUDICATION_SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ])

        result["selected_label"] = response.selected_label
        result["confidence_band"] = response.confidence_band
        result["matched_markers"] = response.matched_markers
        result["rationale"] = response.rationale
        result["review_required"] = response.review_required or result.get("review_required", False)
        result["review_notes"] = response.review_notes
        result["alternatives"] = [a.model_dump() for a in response.alternatives]

    logs = state.get("logs", [])
    logs.append("Completed LLM adjudication for ambiguous clusters")
    state["logs"] = logs
    return state
