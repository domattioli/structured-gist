```text
- Timeout-config rollouts
    ↪ four services changed timeouts this week; similar
    on the surface, but details differ
    A. Service A
        ▸ Timeout 30 seconds → 5 seconds, commit `abc1234`
        ↪ was masking slow downstream failures; shorter
        timeout forces faster failure detection
    B. Service B
        ▸ Timeout 30 seconds → 45 seconds, commit `def5678`
        ↪ was timing out legitimate slow requests during
        nightly batch jobs; raised for headroom
    C. Service C
        ▸ Version 2.3.1, seconds → duration string
        ↪ functionally the same 30-second effective
        timeout, just reconfigured
    D. Service D
        ▸ Aborted, target version 2.4.0-rc1
        ↪ stopped mid-rollout after a health check
        failure; still running previous config

- A/B confusion risk
    ↪ both read as "timeout config changed this week"
    ▸ Opposite directions
        ↪ A cut to a sixth of its value (30 seconds → 5
        seconds); B nearly doubled its own (30 seconds →
        45 seconds)
    ▸ Different commits
        ↪ `abc1234` versus `def5678` — similarly short,
        easy to mix up
```
