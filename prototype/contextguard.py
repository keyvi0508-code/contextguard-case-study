from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


TOKEN_RE = re.compile(r"[a-z0-9]+")


def load_documents(path: Path) -> list[dict[str, Any]]:
    return json.loads(path.read_text(encoding="utf-8"))


def _tokens(value: str) -> set[str]:
    return set(TOKEN_RE.findall(value.lower()))


def can_view(document: dict[str, Any], user_roles: set[str]) -> bool:
    allowed = set(document["allowed_roles"])
    return "public" in allowed or bool(allowed & user_roles)


def reconstruct_context(
    query: str,
    user_roles: list[str],
    documents: list[dict[str, Any]],
    top_k: int = 3,
) -> dict[str, Any]:
    query_tokens = _tokens(query)
    trusted_roles = {role.lower() for role in user_roles}
    visible_documents = [
        document for document in documents if can_view(document, trusted_roles)
    ]

    ranked: list[tuple[int, str, dict[str, Any]]] = []
    for document in visible_documents:
        searchable = " ".join(
            [document["title"], document["summary"], *document["tags"]]
        )
        score = len(query_tokens & _tokens(searchable))
        if score:
            ranked.append((score, document["updated_at"], document))

    ranked.sort(key=lambda item: (-item[0], item[1], item[2]["id"]))
    selected = [item[2] for item in ranked[:top_k]]

    evidence = [
        {
            "document_id": document["id"],
            "title": document["title"],
            "summary": document["summary"],
            "updated_at": document["updated_at"],
            "citation": f"[{document['id']}] {document['title']}",
        }
        for document in selected
    ]

    return {
        "query": query,
        "roles_used": sorted(trusted_roles),
        "evidence": evidence,
        "evidence_status": "available" if evidence else "insufficient_visible_evidence",
        "decision_authority": "human",
    }


if __name__ == "__main__":
    fixture_path = Path(__file__).parent / "fixtures" / "documents.json"
    packet = reconstruct_context(
        "payment incident timeline",
        ["analyst"],
        load_documents(fixture_path),
    )
    print(json.dumps(packet, indent=2))

