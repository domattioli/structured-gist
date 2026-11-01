```text
- Timeout rollouts
    ▸ Scope
        a. four services
        b. this week
    ▸ Surface reading
        ↪ on the surface they all read the same: someone bumped
        a timeout value and redeployed; the details are what
        actually matter
- Service A
    ▸ Change
        a. request timeout decreased
        b. 30 seconds to 5 seconds
    ▸ Location
        a. commit `abc1234`
        b. `config/service-a.yaml`
    ▸ Purpose
        ↪ the decrease was intentional — Service A was masking
        slow downstream failures by waiting too long before
        giving up, and the shorter timeout forces faster
        failure detection
- Service B
    ▸ Change
        a. request timeout increased
        b. 30 seconds to 45 seconds
    ▸ Location
        a. commit `def5678`
        b. `config/service-b.yaml`
    ▸ Purpose
        ↪ Service B was timing out on legitimate slow requests
        during nightly batch jobs, so the timeout was raised to
        give those requests room to finish
- Service C
    ▸ Change
        a. version bump to `2.3.1`
        b. `config/service-c/timeout.toml`
    ▸ Effect
        ↪ not a raw timeout-seconds change: the timeout unit
        changed from seconds to a duration string, functionally
        keeping the same 30-second effective timeout but
        changing how it's configured
- Service D
    ▸ Status
        a. rollout aborted
        b. target version `2.4.0-rc1`
    ▸ Cause
        ↪ it was meant to change its timeout as well, but the
        deploy was stopped mid-rollout after a health check
        failure; Service D still runs its previous config
        unchanged
- A versus B
    ▸ Confusion risk
        ↪ both are described as "timeout config changes shipped
        this week," but A cut its timeout to a sixth of its
        previous value while B nearly doubled its own
    ▸ Differences
        a. opposite directions
        b. opposite motivations
        c. different commits
            ↪ `abc1234` versus `def5678` look superficially
            similar as short hashes
```
