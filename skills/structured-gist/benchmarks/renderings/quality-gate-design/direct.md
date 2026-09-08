```text
- Release-integrity gate ▸ Failure conditions a. breaking public-API change, no bump ↪ requires major, or 0.x minor, version bump b. tag mismatches package version c. missing changelog entry d. upload tool error ▸ Execution ↪ runs in CI on every tagged release; blocks release workflow until all checks pass
```
