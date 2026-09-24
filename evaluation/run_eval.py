from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from prototype.contextguard import load_documents, reconstruct_context


def main() -> int:
    documents = load_documents(ROOT / "prototype" / "fixtures" / "documents.json")
    cases = json.loads((ROOT / "evaluation" / "cases.json").read_text(encoding="utf-8"))

    rows = []
    for case in cases:
        packet = reconstruct_context(case["query"], case["roles"], documents)
        actual_ids = [item["document_id"] for item in packet["evidence"]]
        citations_ok = all(item["citation"].startswith("[DOC-") for item in packet["evidence"])
        passed = (
            actual_ids == case["expected_document_ids"]
            and not (set(actual_ids) & set(case["must_not_include"]))
            and citations_ok
            and packet["decision_authority"] == "human"
        )
        rows.append(
            {
                "case_id": case["id"],
                "roles": case["roles"],
                "query": case["query"],
                "expected_document_ids": case["expected_document_ids"],
                "actual_document_ids": actual_ids,
                "blocked_document_ids": case["must_not_include"],
                "evidence_status": packet["evidence_status"],
                "citations_present": citations_ok,
                "decision_authority": packet["decision_authority"],
                "passed": passed,
            }
        )

    result = {
        "run_date": "2026-09-24",
        "prototype_version": "public-v1",
        "method": "deterministic local prototype; no LLM or external service",
        "case_count": len(rows),
        "passed": sum(row["passed"] for row in rows),
        "failed": sum(not row["passed"] for row in rows),
        "cases": rows,
    }
    output = ROOT / "evaluation" / "results" / "latest.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(f"{result['passed']}/{result['case_count']} cases passed")
    return 0 if result["failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())

