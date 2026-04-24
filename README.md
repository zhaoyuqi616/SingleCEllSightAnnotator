# 🧬 SingleCellSightAnnotator

**AI-Assisted Single-Cell RNA-seq Cell Type Annotation Agent**

SingleCellSightAnnotator is an AI-powered bioinformatics tool that converts **cluster-level marker genes** into **interpretable cell-type annotations** using reference databases, scoring algorithms, and explainable outputs.

---

## 🚀 Overview

Single-cell RNA-seq workflows often produce cluster-specific marker genes but require manual interpretation to assign biological meaning. This tool automates that process by providing:

* 🔍 Marker-to-reference matching
* 📊 Quantitative confidence scoring
* 🧾 Evidence gene reporting
* 🤖 Optional AI-based reasoning
* 📁 Exportable annotation tables

---

## 🧠 Key Features

* ✅ Automated cell-type annotation from marker genes
* ✅ Supports Seurat / Scanpy outputs (e.g., FindAllMarkers)
* ✅ Reference database integration (PanglaoDB, curated markers)
* ✅ Transparent scoring and evidence tracking
* ✅ User-friendly interface (Gradio)
* ✅ API-ready (FastAPI-compatible design)
* ✅ Reproducible and modular pipeline

---

## 🏗️ Architecture

```text
Input (marker genes)
        ↓
Preprocessing (gene normalization)
        ↓
Reference Database Matching
        ↓
Scoring Engine
        ↓
Reasoning Layer (optional LLM)
        ↓
Output Table + UI/API
```

---

## 📥 Installation

### 1. Clone the repository

```bash
git clone https://github.com/zhaoyuqi616/SingleCEllSightAnnotator.git
cd SingleCEllSightAnnotator
```

### 2. Install dependencies

```bash
# Create environment
python3.10 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
# Install the package
pip install -r requirements.txt
pip install gradio
pip install pytest
pip install -e .

# Create .env
cp .env.example .env
# At minimum, if you want LLM adjudication:
# OPENAI_API_KEY=your_key_here
# OPENAI_MODEL=gpt-4.1-mini
# CURATED_MARKER_DB=data/knowledge/curated_markers_v1.json
# OUTPUT_DIR=outputs
# 

```

---

## ▶️ Usage

### Run the application

```bash
python app.py
```

If using Gradio, a local UI will launch in your browser.

---

## 📊 Example Input

| cluster | gene  |
| ------- | ----- |
| 0       | EPCAM |
| 0       | KRT18 |
| 1       | CD3D  |
| 1       | CD3E  |

---

## 📈 Example Output

| cluster | predicted_cell_type | evidence_genes | confidence | score |
| ------- | ------------------- | -------------- | ---------- | ----- |
| 0       | epithelial cell     | EPCAM, KRT18   | High       | 0.91  |
| 1       | T cell              | CD3D, CD3E     | High       | 0.87  |

---

## 🔬 Methodology

### 1. Marker Matching

* Computes overlap between query markers and reference markers

### 2. Scoring

* Overlap-based scoring (ratio, weighted markers)
* Optional advanced scoring (TF-IDF / enrichment-based)

### 3. Evidence Extraction

* Reports matched genes supporting prediction

### 4. Optional AI Reasoning

* Generates biological explanations for predictions

---

## 🧩 Project Structure

```text
SingleCellSightAnnotator/
├── README.md
├── app.py
├── requirements.txt
├── src/
│   ├── preprocessing.py
│   ├── matcher.py
│   ├── scorer.py
│   ├── reference_db.py
│   └── utils.py
├── data/
├── tests/
├── results/
└── .github/
```

---

## 🔧 API Design (Optional)

```bash
POST /annotate
```

### Example Input

```json
{
  "markers": {
    "0": ["EPCAM", "KRT18"],
    "1": ["CD3D", "CD3E"]
  }
}
```

### Example Output

```json
{
  "annotations": [
    {
      "cluster": "0",
      "cell_type": "epithelial cell",
      "confidence": "High"
    }
  ]
}
```

---

## 🧠 Why This Matters

* Eliminates manual annotation bottlenecks
* Improves reproducibility across studies
* Provides interpretable, evidence-based outputs
* Bridges computational analysis and biological insight

---

## ⚠️ Limitations

* Dependent on reference database quality
* May not detect novel cell types
* Sensitive to marker gene quality

---

## 🚀 Future Work

* Multi-omics integration
* Spatial transcriptomics support
* RAG-based literature validation
* Isoform-level annotation (long-read RNA-seq)
* Multi-agent architecture (LangGraph)

---

## 📌 Tech Stack

* Python
* Pandas / NumPy
* Gradio (UI)
* FastAPI (optional API layer)
* Bioinformatics marker databases

---

## 📄 License

MIT License

---

## 👤 Author

**Yuqi Zhao**
Computational Biologist | AI in Translational Science

---

## ⭐ Acknowledgments

* PanglaoDB
* CellMarker database
* Single-cell analysis community

---

## 💡 Citation (Optional)

If you use this tool in your research, please consider citing:

```text
SingleCellSightAnnotator: AI-assisted cell-type annotation framework for scRNA-seq data.
```
