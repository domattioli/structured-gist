```text
- Evaluation scenario A. three-week staging replay ↪ 70 percent reads, 25 percent writes, 5 percent bulk exports
- Candidates A. incumbent open source ↪ reads and writes clean; cannot model long-polling bulk exports; the external-driver workaround is the duct tape to retire B. commercial service ↪ best reporting with automatic run comparison; blocked because recorded traffic must upload to the vendor cloud and scrubbing cannot meet policy C. newer open source ↪ expresses the full scenario natively and self-hosted; the distributed runner lost coordination twice and the project has two maintainers D. eliminated week one ↪ licensing flipped to per-seat mid-evaluation, costing more than the observability budget
- Recommendation I. adopt C for regression gate ↪ the scheduled gate tolerates a flaky rerun II. keep A for ad-hoc testing III. revisit B next year ↪ a self-hosted replay runner would dissolve the governance blocker
```
