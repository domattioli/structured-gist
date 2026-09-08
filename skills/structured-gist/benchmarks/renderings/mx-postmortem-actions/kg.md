```text
- May 3 outage ▸ Scope ↪ 47 minutes, search feature only ▸ Root cause ↪ invalidation queue consumer deployed with concurrency one; overflow silently dropped oldest messages; stale cache read as authoritative ▸ Response grades a. detection fast, nine minutes b. communication clean, fifteen-minute updates c. diagnosis slow, half hour ↪ dropped messages left no trace; the index was searched before queue metrics
- Action items I. queue overflow pages, never drops II. concurrency required in manifest ↪ a lint rule rejects implicit defaults; platform team, end of month III. runbook starts at queue depth IV. quarterly game-day rehearses this ↪ the replay mitigation worked but cost twelve minutes reading its documentation
```
