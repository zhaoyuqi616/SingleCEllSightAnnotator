# 🧬 Single CEll Sight Annotator (SCESA)
**AI Copilot for Single-Cell Cell-Type Annotation**

---

## 🚀 Overview

**SingleCEllSight Annotator** is an AI-powered, evidence-guided annotation engine for **single-cell RNA-seq (scRNA-seq)** cluster labeling.

It combines:
- curated biological knowledge (marker databases)
- deterministic scoring (interpretable rules)
- LLM-assisted reasoning (for ambiguous cases)
- human-in-the-loop review signals

to generate **transparent, reproducible, and confidence-aware cell-type annotations**.

---

## ✨ Key Features

- 🔬 **Marker-based annotation engine**
- 🧠 **Hybrid AI architecture**
- 📊 **Confidence-aware predictions**
- ⚠️ **Biological QC detection**
- 🧾 **Explainable outputs**
- 👨‍⚕️ **Human-in-the-loop ready**
- 🖥️ **Interactive UI (Gradio)**
- 📦 **Reproducible outputs**

---

## 🏗️ Architecture

Ingest → Validate → Normalize → QC → Retrieve → Score → Adjudicate → Finalize → Persist

---

## 📂 Project Structure

cell_type_annotation_agent/
├── app_gradio.py
├── data/
├── src/cell_annotator/
├── tests/
├── pyproject.toml
└── README.md

---

## ⚙️ Installation

```bash
git clone https://github.com/yourusername/CellSight-Annotator.git
cd CellSight-Annotator

python3.10 -m venv .venv
source .venv/bin/activate

pip install -e .[dev]
pip install gradio
```

---

## ▶️ Usage

### CLI

```bash
python -m cell_annotator.main \
  --input data/examples/marker_list_simple.tsv \
  --species human \
  --tissue PBMC
```

### Web UI

```bash
python app_gradio.py
```

Open http://127.0.0.1:7860

---

## 📥 Input Format

cluster	gene
0	CD3D
0	CD3E
1	MS4A1
1	CD79A

---

## 📤 Output Example

| Cluster | Cell Type | Confidence | QC | Top Markers |
|--------|----------|------------|----|------------|
| 0 | CD8 T cell | High | – | CD3D, CD8A |
| 1 | B cell | High | – | MS4A1, CD79A |

---

## 🧪 Testing

```bash
pytest -q
```

---

## 🧠 Knowledge Base

- PanglaoDB
- curated markers
- domain knowledge

---

## ⚠️ Limitations

- Marker DB still evolving
- Confidence not fully calibrated
- Limited ontology integration

---

## 🔮 Roadmap

- Expand marker DB
- Improve scoring
- Add ontology support
- Production deployment

---

## 🧑‍💻 Tech Stack

Python, Pandas, Gradio, OpenAI API, pytest

---

## 👤 Author

Yuqi Zhao  
https://github.com/zhaoyuqi616
