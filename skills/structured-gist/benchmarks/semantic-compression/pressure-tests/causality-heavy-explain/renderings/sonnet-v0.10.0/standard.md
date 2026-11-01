```text
- Webhook receiver
    ▸ Change
        ↪ Moved from synchronous processing to a queue-based
        async model; the reason only makes sense as a chain,
        not as a list of separate facts.
- Failure chain
    I. synchronous handler design
        ↪ On each webhook, the handler called a downstream
        enrichment API directly and held the HTTP request
        open until that call returned.
    II. slow downstream API
        ↪ Already slow under normal conditions, often taking
        several seconds to respond.
    III. sender connection held open
        ↪ Because the handler waited synchronously, the
        sender's HTTP connection stayed open for those same
        several seconds.
    IV. sender timeouts
        ↪ Under any real load, some calls ran long enough to
        exceed the sender's timeout, so a meaningful fraction
        of requests timed out.
    V. sender retries
        ↪ Senders assume a timed-out request failed and, by
        design, retry it; each retry was a new synchronous
        call to the same already-slow endpoint.
    VI. retry feedback loop
        ↪ Retries did not relieve pressure on the downstream
        API, they added to it, which pushed more calls past
        the timeout threshold and produced more retries.
    VII. peak-traffic cascade
        ↪ In ordinary traffic the loop stayed small and went
        unnoticed; at peak it ran hot enough to cascade:
        downstream queue depth grew faster than it could
        drain, latency, timeout rates and retry volume
        climbed, until the receiver spent most of its
        capacity on retried requests instead of new ones.
- Queue fix
    ▸ Trigger
        ↪ The cascade drove the decision to introduce a
        message queue in front of the enrichment step.
    ▸ Mechanism
        ↪ The receiver acknowledges the sender immediately on
        receipt and hands the enrichment work to a worker
        process instead of doing it inline.
    ▸ Decoupling
        ↪ The receiver's response time no longer depends on
        the enrichment API's response time, so the two
        latencies stopped being coupled to each other.
    ▸ Outcome
        ↪ A slow downstream call no longer produces a
        sender-facing timeout, which means no retry; the
        retry-storm failure mode that caused the cascades
        is gone, not just less frequent.
```
