Four services got timeout-config rollouts this week, and on the surface they all read the same: someone bumped a timeout value and redeployed. The details are what actually matter here.

Service A's request timeout was decreased from 30 seconds to 5 seconds, shipped at commit `abc1234` in `config/service-a.yaml`. The decrease was intentional — Service A was masking slow downstream failures by waiting too long before giving up, and the shorter timeout forces faster failure detection.

Service B's request timeout went the opposite direction: it was increased from 30 seconds to 45 seconds, shipped at commit `def5678` in `config/service-b.yaml`. This was a response to a different problem — Service B was timing out on legitimate slow requests during nightly batch jobs, so the timeout was raised to give those requests room to finish.

Service C's rollout wasn't a raw timeout-seconds change at all; it bumped the service to version `2.3.1` and touched `config/service-c/timeout.toml`, which changed the timeout unit from seconds to a duration string, functionally keeping the same 30-second effective timeout but changing how it's configured.

Service D's rollout was aborted before completion. It was targeting version `2.4.0-rc1` and was meant to change its timeout as well, but the deploy was stopped mid-rollout after a health check failure, and Service D is still running its previous config unchanged.

It is easy to mix up Service A and Service B here because both are described as "timeout config changes shipped this week," but A cut its timeout to a sixth of its previous value while B nearly doubled its own — opposite directions, opposite motivations, and different commits (`abc1234` versus `def5678`) that look superficially similar as short hashes.
