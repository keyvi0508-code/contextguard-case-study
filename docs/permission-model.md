# Permission model

## Implemented rule

Each document contains an `allowed_roles` list. A document is visible when at least one trusted user role appears in that list. Documents marked `public` are visible to every role.

Permission filtering runs before ranking. This prevents restricted document text and tags from entering the retrieval candidate set.

## Trust boundary

The prototype treats the supplied role set as trusted input. It does not authenticate users or issue roles. In a real system, roles must come from an identity provider or policy service, never from free-text user instructions.

## Tested behaviors

- an analyst can retrieve the public incident timeline but not finance exposure;
- a manager can retrieve both;
- a compliance user can retrieve the regulatory note;
- an analyst receives no evidence for a compliance-only query;
- an unknown role receives no restricted evidence;
- every returned item carries a document ID citation;
- every context packet keeps final decision authority with a human.

## Out of scope

The prototype does not implement field-level redaction, inherited group membership, deny rules, jurisdictional policy, time-bound grants, consent, audit-log persistence, or connector-level authorization.

