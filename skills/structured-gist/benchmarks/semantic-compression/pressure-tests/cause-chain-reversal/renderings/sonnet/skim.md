```text
- Outage onset
    ▸ 14:02 start
    ▸ DB connection errors (payments)
- Pool-exhaustion theory
    I. assumed traffic exhausted pool
    II. raised pool 50→150
    III. errors dropped — seemed confirmed
- Secondary probe
    I. slow order-history query found
    II. connections pinned → pool starved
- Root cause
    ▸ Migration dropped index
    ▸ Missing index (true cause)
- Stopgap limits
    ▸ Symptom reduced only
    ▸ Slow query recurs
- Index fix
    ▸ Index added back
    ▸ Query and pileup fixed
- Postmortem verdict
    ▸ Pool size kept
    ▸ Index was the fix
```
