```text
- Timeout-config rollouts
    ↪ four services shipped timeout-config changes this
    week; on the surface all read the same, as
    "bumped a value, redeployed" — the details differ
    A. Service A
        ▸ Timeout 30 seconds → 5 seconds
        ▸ Commit `abc1234`
        ▸ File `config/service-a.yaml`
        ↪ intentional: Service A was masking slow
        downstream failures by waiting too long, so the
        shorter timeout forces faster failure detection
    B. Service B
        ▸ Timeout 30 seconds → 45 seconds
        ▸ Commit `def5678`
        ▸ File `config/service-b.yaml`
        ↪ opposite fix: Service B was timing out on
        legitimate slow requests during nightly batch
        jobs, so the timeout was raised to give those
        requests room to finish
    C. Service C
        ▸ Not a raw seconds change
        ▸ Version → 2.3.1
        ▸ File `config/service-c/timeout.toml`
        ↪ changed the timeout unit from seconds to a
        duration string; functionally keeps the same
        30-second effective timeout, just changes how
        it's configured
    D. Service D
        ▸ Status aborted
        ▸ Target version 2.4.0-rc1
        ▸ Meant to change timeout too
        ↪ deploy was stopped mid-rollout after a health
        check failure; Service D is still running its
        previous config, unchanged

- A/B confusion risk
    ↪ both are described as "timeout config changes
    shipped this week," which invites conflating them
    ▸ Opposite directions
        ↪ A cut its timeout to a sixth of its previous
        value (30 seconds → 5 seconds); B nearly doubled
        its own (30 seconds → 45 seconds) — opposite
        directions, opposite motivations
    ▸ Different commits
        ↪ `abc1234` (A) versus `def5678` (B) — different
        commits that look superficially similar as short
        hashes
```
