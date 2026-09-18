# Example — `structured-gist` report preset (v0.5.0b1)

Source (synthetic): on-call support notes about a recurring timeout
incident. The report preset packages each independently-supported
finding as its own top concept — no shared Intro/Background root —
and omits any optional branch (Question, Method, Observed, Inferred,
Next) the source does not support, so the two findings below end up
with different branch sets.

<!--
source: Support notes recorded that timeout errors may spike during cache warm-up, correlated with a rising request rate; engineers suspect cold cache entries explain the spike; on-call resolved recurring alerts by pre-warming the cache before peak traffic, though restarts alone did not reduce alert volume in prior incidents.
hedge: may
claim-key: spike during cache warm-up
relation: correlated with
endpoint-a: timeout errors
endpoint-b: request rate
supported-branches: Observed, Inferred, Next, Question
-->

```text
- Timeouts may spike
    ▸ Observed
        ↪ timeout errors may spike during cache warm-up,
        correlated with a rising request rate
    ▸ Inferred
        ↪ engineers suspect cold cache entries explain the spike
    ▸ Next
        ↪ pre-warm cache before peak traffic
- Restarts don't help
    ▸ Question
        ↪ does restarting reduce alert volume?
    ▸ Observed
        ↪ restarts did not reduce alert count in prior incidents
```

Two peer findings, not one packaging root. The first heading keeps
the source's hedge (`may`) rather than promoting a hedged claim to
an unhedged heading, and its Observed leaf keeps the source's
association wording (`correlated with`) instead of upgrading it to a
causal arrow. Its Inferred leaf reflects an inference the source
itself states (engineers' suspicion), not a manufactured one. The
second finding is unhedged in the source, has no Method or Next
branch, and none is invented.
