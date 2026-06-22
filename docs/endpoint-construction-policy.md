# Endpoint construction policy

This note fixes the policy for edge endpoint construction before adding more constructor syntax.

## Decision

Keep the current default behavior: `add edge` endpoints must already name existing nodes. Endpoints may come from literal IDs or from variables that were bound by earlier `match` or `add node` statements, but the plain `add edge` form must not silently create endpoint nodes.

```cgppl
rule main => {
  match node $source label "Root";
  add node $target label "Generated";
  add edge $edge from $source to $target label "new";
}
```

A missing endpoint is a construction precondition failure. The runtime already reports that as a rule-local `GraphMatchFailed`, so it can participate in `try { ... } or { ... }` fallback.

## Rationale

Implicit endpoint creation in the default edge constructor would hide typos and weak matches. For example, `add edge $e from "soruce" to $target;` should fail loudly instead of creating a node with the misspelled ID.

Explicit endpoints also keep graph rewrite programs easier to audit: node creation is visible at `add node`, and edge creation is visible at `add edge`. This matches the current deterministic binding model for construction target variables.

## Reserved future form

Endpoint auto-creation may still be useful, but it should be opt-in at the endpoint site. The reserved syntax is:

```cgppl
add edge $edge from add $source to add $target label "new";
```

Proposed future semantics:

- Without `add`, endpoints remain strict graph references and must already exist.
- With `add` before an endpoint variable, an unbound variable creates a fresh node ID using the existing deterministic construction-ID rule, then binds the variable.
- With `add` before a literal endpoint, the runtime ensures a node with that literal ID exists; if absent, it creates it.
- With `add` before an already-bound variable, the runtime uses the binding and still requires that the bound node exists.
- Auto-created endpoint nodes start with no labels or attributes. Programs that need annotations should use explicit `add node` statements instead.

## Next implementation step

Add parser tests and an AST shape for opt-in endpoint specs without changing runtime behavior yet. A small first slice is enough:

```python
@dataclass(frozen=True, slots=True)
class EndpointRef:
    ref: GraphRef
    auto_create: bool = False
```

Then update `AddEdgeStmt.source_id` and `AddEdgeStmt.target_id` to use `EndpointRef` while preserving compatibility for existing literal and variable endpoint syntax.
