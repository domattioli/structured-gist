```text
- Timeout rollouts
    ▸ Scope
        a. four services
        b. this week
    ▸ Surface reading
        ↪ On the surface they all read the same: someone bumped
        a timeout value and redeployed; the details are what
        actually matter.
- Service A
    ▸ Change
        a. request timeout decreased
        b. from 30 seconds
        c. to 5 seconds
    ▸ Commit
        a. `abc1234`
    ▸ File
        a. `config/service-a.yaml`
    ▸ Motivation
        ↪ The decrease was intentional: Service A was masking
        slow downstream failures by waiting too long before
        giving up, and the shorter timeout forces faster
        failure detection.
- Service B
    ▸ Change
        a. request timeout increased
        b. from 30 seconds
        c. to 45 seconds
    ▸ Commit
        a. `def5678`
    ▸ File
        a. `config/service-b.yaml`
    ▸ Motivation
        ↪ Service B was timing out on legitimate slow requests
        during nightly batch jobs, so the timeout was raised to
        give those requests room to finish.
- Service C
    ▸ Version
        a. bumped to `2.3.1`
    ▸ File
        a. `config/service-c/timeout.toml`
    ▸ Change
        ↪ Not a raw timeout-seconds change: the timeout unit
        changed from seconds to a duration string, functionally
        keeping the same 30-second effective timeout but
        changing how it is configured.
- Service D
    ▸ Status
        a. rollout aborted
        b. stopped mid-rollout
    ▸ Target version
        a. `2.4.0-rc1`
    ▸ Intent
        ↪ It was meant to change its timeout as well.
    ▸ Trigger
        a. health check failure
    ▸ Current config
        a. previous config, unchanged
- A versus B
    ▸ Confusion risk
        ↪ Both are described as "timeout config changes shipped
        this week."
    ▸ Direction
        a. A cut to a sixth
        b. B nearly doubled
    ▸ Motivation
        a. opposite motivations
    ▸ Commits
        a. `abc1234` versus `def5678`
        b. superficially similar short hashes
```
