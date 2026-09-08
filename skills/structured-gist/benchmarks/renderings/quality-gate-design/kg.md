```text
- Release-integrity gate ▸ Failure conditions a. breaking API change without bump ↪ a major, or 0.x minor, version bump is required b. tag mismatches package version c. missing changelog entry d. upload tool error ▸ Execution ↪ runs in CI on every tagged release and blocks the workflow until all checks pass
```
