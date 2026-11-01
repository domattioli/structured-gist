```text
- Timeout rollouts
    ▸ Context
        ↪ Four services shipped timeout-config rollouts this
        week. They look alike, but the details differ.
- Service A
    ▸ Change
        ↪ Request timeout decreased from 30 seconds to 5
        seconds.
    ▸ Commit
        ↪ Shipped at commit `abc1234` in `config/service-a.yaml`.
    ▸ Reason
        ↪ Intentional. Service A was masking slow downstream
        failures by waiting too long before giving up, and the
        shorter timeout forces faster failure detection.
- Service B
    ▸ Change
        ↪ Request timeout increased from 30 seconds to 45
        seconds.
    ▸ Commit
        ↪ Shipped at commit `def5678` in `config/service-b.yaml`.
    ▸ Reason
        ↪ It was timing out on legitimate slow requests during
        nightly batch jobs, so the timeout was raised to give
        those requests room to finish.
- Service C
    ▸ Version
        ↪ Bumped to version `2.3.1`.
    ▸ Change
        ↪ Touched `config/service-c/timeout.toml`, changing the
        timeout unit from seconds to a duration string. Not a
        raw timeout-seconds change.
    ▸ Effective timeout
        ↪ Functionally the same 30-second effective timeout,
        but how it is configured changed.
- Service D
    ▸ Status
        ↪ Aborted before completion, stopped mid-rollout after
        a health check failure.
    ▸ Target
        ↪ Targeted version `2.4.0-rc1` and was meant to change
        its timeout as well.
    ▸ Current config
        ↪ Still running its previous config unchanged.
- A versus B
    ▸ Mix-up risk
        ↪ Both are described as "timeout config changes
        shipped this week," so they are easy to mix up.
    ▸ Difference
        ↪ A cut its timeout to a sixth of its previous value,
        while B nearly doubled its own. Opposite directions and
        opposite motivations.
    ▸ Commits
        ↪ `abc1234` versus `def5678` look superficially similar
        as short hashes.
```
