# Positive require runtime diagnostics wiring

Positive `require` statements now have direct runtime wiring for the same structured diagnostic style already used by matchers and negative requirements.

Covered runtime paths:

- `require node ...`
- `require edge ...`
- `require node ... label ...`
- `require edge ... label ...`
- `require node ... attr ...`
- `require edge ... attr ...`

The previous import-time adapter has been folded into `src/cgppl/runtime.py`, so package initialization no longer mutates runtime dispatch. Positive-require failures now call the `format_required_*_failure` helpers directly from the canonical runtime statement dispatcher.
