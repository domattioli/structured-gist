```text
- Cache migration
    ▸ Writes
        i. Quorum writes
            ↪ Each write waits for two replicas.
        ii. Source
            ↪ The source says:
              ````
              First the team froze writes.
              Then it copied each shard.
              Last it reopened writes.
              ````
```
