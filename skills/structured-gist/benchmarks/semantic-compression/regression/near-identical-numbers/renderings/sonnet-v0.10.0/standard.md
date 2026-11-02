```text
- Timeout rollouts
    ▸ Scope
        ↪ Four services got timeout-config rollouts this week,
        and on the surface they all read the same: someone
        bumped a timeout value and redeployed.
        The details are what actually matter.
- Service A
    ▸ Change
        ↪ Request timeout decreased from 30 seconds to 5
        seconds.
    ▸ Commit
        ↪ `abc1234` in `config/service-a.yaml`.
    ▸ Purpose
        ↪ The decrease was intentional: Service A was masking
        slow downstream failures by waiting too long before
        giving up, and the shorter timeout forces faster
        failure detection.
- Service B
    ▸ Change
        ↪ Request timeout increased from 30 seconds to 45
        seconds.
    ▸ Commit
        ↪ `def5678` in `config/service-b.yaml`.
    ▸ Purpose
        ↪ Service B was timing out on legitimate slow requests
        during nightly batch jobs, so the timeout was raised to
        give those requests room to finish.
- Service C
    ▸ Change
        ↪ Not a raw timeout-seconds change: bumped the service
        to version `2.3.1` and touched
        `config/service-c/timeout.toml`.
    ▸ Effect
        ↪ Changed the timeout unit from seconds to a duration
        string, functionally keeping the same 30-second
        effective timeout but changing how it is configured.
- Service D
    ▸ Status
        ↪ Rollout aborted before completion.
    ▸ Target
        ↪ Version `2.4.0-rc1`, meant to change its timeout as
        well.
    ▸ Cause
        ↪ The deploy was stopped mid-rollout after a health
        check failure.
    ▸ State
        ↪ Still running its previous config unchanged.
- A versus B
    ▸ Similarity
        ↪ Both are described as "timeout config changes shipped
        this week", so they are easy to mix up.
    ▸ Difference
        ↪ A cut its timeout to a sixth of its previous value
        while B nearly doubled its own: opposite directions,
        opposite motivations.
    ▸ Commits
        ↪ `abc1234` versus `def5678` look superficially similar
        as short hashes.
```
