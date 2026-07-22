# Contributing

Contributions must remain hardware-safe and reproducible.

1. Keep all real robot execution opt-in; new commands must default to preview or dry-run mode.
2. Do not commit datasets, weights, raw videos, private logs, machine-specific paths, device serials, accounts, endpoints, or credentials.
3. Add hardware-free tests for state transitions and safety behavior.
4. Run `make test` and `make validate` before opening a pull request.
5. Document which behavior belongs to an upstream project and which code is implemented here.

