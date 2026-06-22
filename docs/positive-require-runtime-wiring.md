# Positive require runtime diagnostics wiring

Positive `require` statements now have runtime wiring for the same structured diagnostic style already used by matchers and negative requirements.

Covered runtime paths:

- `require node ...`
- `require edge ...`
- `require node ... label ...`
- `require edge ... label ...`
- `require node ... attr ...`
- `require edge ... attr ...`

The current implementation uses a narrow runtime adapter installed during package initialization. This keeps the feature slice small while preserving the existing runtime surface. A future cleanup should fold the adapter directly into `src/cgppl/runtime.py` and remove the import-time patch module.
