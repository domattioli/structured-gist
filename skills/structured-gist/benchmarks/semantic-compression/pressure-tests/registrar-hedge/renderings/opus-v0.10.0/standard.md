```text
- Domain migration
    ▸ Goal
        ↪ move acme-studio.com from the old Squarespace site to
        an already-deployed Cloudflare Pages site
    ▸ Guidance style
        ↪ click-by-click; user is logged into the dashboards and
        can screen-share tabs
- New site
    ▸ Pages project
        a. name "acme-studio"
        b. https://acme-studio.pages.dev
        c. direct wrangler uploads
        d. not git-connected
    ▸ Account
        a. personal-account
    ▸ Constraint
        ↪ CRITICAL: the same account hosts project
        "personal-portfolio" / personal-portfolio.pages.dev; do
        not touch that project or its DNS
- Old site
    ▸ Status
        a. Squarespace, live at acme-studio.com
    ▸ Rollback role
        ↪ must remain intact as a rollback target for ~2 weeks
        after cutover
    ▸ Preferences
        a. DNS-record cutover
        b. revertible in minutes
    ▸ Forbidden steps
        a. cancel Squarespace subscription
        b. delete Squarespace site
        c. transfer domain registration now
- Registrar
    ▸ Certainty
        ↪ unconfirmed - likely Squarespace Domains (site was
        built there), possibly Google Domains legacy or another
        registrar
    ▸ Identification
        a. whois
        b. Squarespace/Domains dashboard
- Requested steps
    I. Snapshot current state
        ↪ identify registrar and current DNS host; list current
        DNS records as a written rollback snapshot before
        changing anything
    II. Choose apex + www path
        i. check Squarespace apex support
            ↪ confirm whether its DNS supports CNAME
            flattening/ALIAS for the apex
        ii. else move DNS hosting
            a. add free Cloudflare zone
            b. import records
            c. switch nameservers
            d. keep registration in place
        iii. state rollback procedure, time
            ↪ moving DNS hosting weakens the "instant rollback"
            property
    III. Lower TTLs first
        ↪ only if the current host allows it
    IV. Add custom domains
        i. acme-studio.com
        ii. www.acme-studio.com
        iii. apply prescribed DNS changes
    V. Verify
        i. apex, www resolve over HTTPS
        ii. cert issued
        iii. http->https works
        iv. www/apex canonicalization works
        v. /about returns 200
    VI. Deliver rollback note
        ↪ exact rollback steps as a saved note, plus a reminder
        to submit the sitemap in Google Search Console after
        cutover
- Open issue
    ▸ Contact form
        ↪ backend not functional yet, being fixed separately;
        completing DNS today is accepted, and the launch
        decision is the user's
```
