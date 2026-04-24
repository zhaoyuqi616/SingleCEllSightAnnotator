from __future__ import annotations

import os
import tempfile
from pathlib import Path
from typing import Optional

import pandas as pd
import gradio as gr

from cell_annotator.graph import build_graph

try:
    from langchain_openai import ChatOpenAI
except Exception:
    ChatOpenAI = None


APP_TITLE = "SingleCEll Sight Annotator"
APP_DESC = (
    "Upload a marker file or paste a cluster/gene table, run the annotation agent, "
    "review the output table, and optionally ask follow-up questions about the result."
)


def _save_text_input_to_temp(marker_text: str) -> str:
    """
    Save pasted marker text to a temporary file.
    Accepts CSV or TSV-like content with at least columns: cluster, gene
    """
    if not marker_text or not marker_text.strip():
        raise gr.Error("Please upload a marker file or paste a marker table.")

    temp_dir = Path(tempfile.mkdtemp(prefix="cell_annotator_ui_"))
    lines = [line for line in marker_text.strip().splitlines() if line.strip()]
    header = lines[0] if lines else ""
    suffix = ".tsv" if "\t" in header else ".csv"
    temp_path = temp_dir / f"pasted_markers{suffix}"
    temp_path.write_text(marker_text, encoding="utf-8")
    return str(temp_path)


def _resolve_input_path(uploaded_file, pasted_text: str) -> str:
    if uploaded_file is not None:
        # gr.File returns a filepath string in newer gradio, or file object in some configs
        if isinstance(uploaded_file, str):
            return uploaded_file
        if hasattr(uploaded_file, "name"):
            return uploaded_file.name
    return _save_text_input_to_temp(pasted_text)


def run_annotation(
    uploaded_file,
    pasted_text: str,
    species: str,
    tissue: str,
    disease_context: str,
):
    input_path = _resolve_input_path(uploaded_file, pasted_text)

    app = build_graph()
    initial_state = {
        "input_path": input_path,
        "species": species or "human",
        "tissue": tissue or None,
        "disease_context": disease_context or None,
        "logs": [],
    }

    try:
        final_state = app.invoke(initial_state)
    except Exception as e:
        raise gr.Error(f"Annotation run failed: {e}")

    output_path = final_state.get("final_output_path", "")
    if not output_path or not Path(output_path).exists():
        raise gr.Error("Run finished, but no output CSV was created.")

    df = pd.read_csv(output_path)
    logs = "\n".join(final_state.get("logs", []))

    # Provide a human-friendly summary for the UI
    summary_lines = [
        f"Run ID: {final_state.get('run_id', 'NA')}",
        f"Input format: {final_state.get('input_format', 'unknown')}",
        f"Clusters annotated: {len(df)}",
        f"Saved output table: {output_path}",
    ]
    if final_state.get("review_queue"):
        summary_lines.append(
            "Clusters flagged for review: " + ", ".join(final_state["review_queue"])
        )

    return (
        df,
        output_path,
        output_path,
        "\n".join(summary_lines),
        logs,
        df.to_dict(orient="records"),
    )


def _basic_result_answer(question: str, result_df: pd.DataFrame) -> str:
    q = (question or "").strip().lower()
    if result_df.empty:
        return "No result table is loaded yet. Run annotation first."

    if "how many" in q and "review" in q:
        n = int(result_df["review_required"].fillna(False).astype(bool).sum())
        return f"{n} cluster(s) are flagged for review."

    if "low confidence" in q or ("which" in q and "confidence" in q):
        low = result_df[result_df["confidence_band"].astype(str).str.lower() == "low"]
        if low.empty:
            return "No low-confidence clusters were found in the current result table."
        return "Low-confidence clusters: " + ", ".join(low["cluster"].astype(str).tolist())

    if "doublet" in q:
        if "qc_flags" not in result_df.columns:
            return "The result table has no qc_flags column."
        flagged = result_df[
            result_df["qc_flags"].astype(str).str.contains("possible_doublet", case=False, na=False)
        ]
        if flagged.empty:
            return "No clusters were flagged as possible_doublets."
        return "Possible doublet clusters: " + ", ".join(flagged["cluster"].astype(str).tolist())

    top_preview = result_df[[c for c in ["cluster", "predicted_cell_type", "confidence_band"] if c in result_df.columns]].head(10)
    return "I can answer simple questions about the current results. Here is a quick preview:\n\n" + top_preview.to_string(index=False)


def ask_result_question(question: str, result_records: list[dict]) -> str:
    if not result_records:
        return "No result table is available yet. Please run annotation first."

    result_df = pd.DataFrame(result_records)

    api_key = os.getenv("OPENAI_API_KEY", "")
    if api_key and ChatOpenAI is not None and question.strip():
        try:
            llm = ChatOpenAI(model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini"), api_key=api_key, temperature=0)
            context = result_df.to_csv(index=False)
            prompt = (
                "You are helping a scientist interpret a cell annotation result table. "
                "Answer only from the provided table. If the answer is not in the table, say so clearly.\n\n"
                f"Question:\n{question}\n\n"
                f"Result table CSV:\n{context}"
            )
            return llm.invoke(prompt).content
        except Exception as e:
            return f"LLM answer failed, so here is a basic local answer instead.\n\n{_basic_result_answer(question, result_df)}\n\nError: {e}"

    return _basic_result_answer(question, result_df)


with gr.Blocks(title=APP_TITLE) as demo:
    gr.Markdown(f"# {APP_TITLE}\n\n{APP_DESC}")

    result_state = gr.State([])

    with gr.Tab("Run annotation"):
        with gr.Row():
            with gr.Column(scale=1):
                uploaded_file = gr.File(label="Upload marker file (.csv or .tsv)", file_count="single")
                pasted_text = gr.Textbox(
                    label="Or paste marker table",
                    lines=12,
                    placeholder="cluster\tgene\n0\tCD3D\n0\tCD3E\n1\tMS4A1\n1\tCD79A",
                )
                species = gr.Dropdown(["human", "mouse"], value="human", label="Species")
                tissue = gr.Textbox(label="Tissue (optional)", placeholder="PBMC, pancreas, tumor, lung...")
                disease_context = gr.Textbox(label="Disease context (optional)", placeholder="breast cancer, healthy control...")
                run_btn = gr.Button("Run annotation", variant="primary")

            with gr.Column(scale=1):
                summary_box = gr.Textbox(label="Run summary", lines=6)
                output_path_box = gr.Textbox(label="Saved output table location")
                output_file = gr.File(label="Download output CSV")
                logs_box = gr.Textbox(label="Logs", lines=12)

        result_table = gr.Dataframe(label="Annotation output table", interactive=False, wrap=True)

    with gr.Tab("Ask about current results"):
        question_box = gr.Textbox(
            label="Question about the current result table",
            lines=3,
            placeholder="Which clusters are low confidence? Which clusters are flagged for review?",
        )
        ask_btn = gr.Button("Ask")
        answer_box = gr.Textbox(label="Answer", lines=10)

    run_btn.click(
        fn=run_annotation,
        inputs=[uploaded_file, pasted_text, species, tissue, disease_context],
        outputs=[result_table, output_path_box, output_file, summary_box, logs_box, result_state],
    )

    ask_btn.click(
        fn=ask_result_question,
        inputs=[question_box, result_state],
        outputs=[answer_box],
    )


if __name__ == "__main__":
    demo.launch()
