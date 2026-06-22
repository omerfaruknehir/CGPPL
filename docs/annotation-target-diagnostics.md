# Annotation target diagnostics

This slice extends the runtime diagnostic helper layer to label and attribute mutation target misses.

Target diagnostic shapes:

```text
missing set target for node "missing" with attr "kind" in rule main
missing set target for edge $e with label "selected" in rule main
missing unset target for node "missing" with attr "kind" in rule main
missing unset target for edge $e with label "selected" in rule main
```

Implemented in this slice:

- formatter helpers for `set node/edge ... attr`
- formatter helpers for `set node/edge ... label`
- formatter helpers for `unset node/edge ... attr`
- formatter helpers for `unset node/edge ... label`
- unit coverage for all helper variants
- `xfail` runtime regression coverage documenting the pending runtime wiring

Runtime wiring is intentionally left for the next incremental slice. The current runtime still emits legacy direct strings for annotation target misses until the statement handlers are wired to these helpers.
