from __future__ import annotations
import argparse
from .graph import build_graph


def main():
    parser = argparse.ArgumentParser(description="Cell type annotation agent")
    parser.add_argument("--input", required=True, help="Path to marker input file")
    parser.add_argument("--species", default="human")
    parser.add_argument("--tissue", default=None)
    parser.add_argument("--disease-context", default=None)
    args = parser.parse_args()

    app = build_graph()

    initial_state = {
        "input_path": args.input,
        "species": args.species,
        "tissue": args.tissue,
        "disease_context": args.disease_context,
        "logs": [],
    }

    final_state = app.invoke(initial_state)

    print("\n=== Run complete ===")
    print(f"Output file: {final_state.get('final_output_path')}")
    print("\nLogs:")
    for line in final_state.get("logs", []):
        print("-", line)


if __name__ == "__main__":
    main()
