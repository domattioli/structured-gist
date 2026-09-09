```text
- Synchronous design
    I. connection held open
    II. sender timeouts
    III. automatic retry
    IV. retry adds load
- Feedback loop
    A. ordinary traffic
    B. peak traffic
- Queue-based redesign
    I. acknowledge immediately
    II. hand off to worker
- Retry storm eliminated
    I. no timeout
    II. no retry
    III. failure mode gone
```
