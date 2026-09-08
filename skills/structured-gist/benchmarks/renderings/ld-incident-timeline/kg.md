```text
- March 14 incident ▸ Symptom ↪ payment service 502s on checkout, 8 percent then 19 percent, oscillating ▸ Timeline i. first Frankfurt alert 0642 ii. dismissed as network blip iii. incident channel opened 0721 iv. fix deployed 0847 ▸ Impact ↪ about 11,000 failed checkouts over two hours five minutes in the European morning peak
- Diagnosis I. false index-build theory first ↪ the migration was blamed for forty minutes though its index build finished at 23:50 the prior night II. deploy timestamps exposed real cause ↪ a fraud-sidecar deploy at 06:30 capped the connection pool at five because a staging overlay glob matched production; fraud-timeout retries then tripled the load
- Action items I. overlay globs validated against allowlist II. pool size floor alert III. single jittered retry policy IV. check whole request path deploys ↪ the dashboard-access gap that prolonged the false theory was fixed by provisioning the whole rotation
```
