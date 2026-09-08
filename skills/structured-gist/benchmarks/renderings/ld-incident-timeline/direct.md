```text
- March 14 incident ▸ Symptom ↪ payment service 502s on checkout, 8% then 19%, oscillating ▸ Timeline i. 06:42 first alert, Frankfurt synthetic ii. dismissed as network blip iii. 07:21 incident channel opened iv. 08:47 fix deployed ▸ Impact ↪ ~11,000 failed checkouts over 2h05m, European morning peak
- Diagnosis I. false theory first ↪ index-build migration blamed ~40 min; build had finished 23:50 prior night II. real cause found via deploy timestamps ↪ fraud sidecar deploy 06:30 capped pool at five connections a. staging overlay hit production ↪ glob pattern broader than author knew b. retries amplified load ↪ fraud timeouts retried, tripling volume
- Action items I. overlay globs validated against allowlist II. pool size floor alert III. retry policy: single jittered retry IV. check deploy log for whole request path ▸ Access note ↪ migration dashboard login missing for most responders; provisioned next week
```
