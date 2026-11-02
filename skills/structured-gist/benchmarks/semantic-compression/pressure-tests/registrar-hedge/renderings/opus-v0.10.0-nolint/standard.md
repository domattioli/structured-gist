```text
- Domain migration
    ▸ Goal
        ↪ move acme-studio.com from the old Squarespace site to
        the already-deployed Cloudflare Pages site, guided
        click-by-click
    ▸ New site
        a. project "acme-studio"
        b. https://acme-studio.pages.dev
        c. direct wrangler uploads
            ↪ not git-connected
        d. account personal-account
    ▸ Old site
        ↪ Squarespace, still live at acme-studio.com; it must
        remain intact as a rollback target for ~2 weeks after
        cutover
    ▸ Registrar
        ↪ unconfirmed - likely Squarespace Domains (site was
        built there), possibly Google Domains legacy or another
        registrar
- Constraints
    A. personal-portfolio untouched
        ↪ the same Cloudflare account hosts the personal site
        (project "personal-portfolio" /
        personal-portfolio.pages.dev); do not touch that project
        or its DNS
    B. revertible DNS cutover
        ↪ prefer a DNS-record cutover that can be reverted in
        minutes
    C. no destructive steps
        a. keep Squarespace subscription
        b. keep Squarespace site
        c. no registration transfer now
- Steps
    I. Identify registrar, DNS host
        ↪ use whois and what the Squarespace/Domains dashboard
        shows; list current DNS records as a written rollback
        snapshot before changing anything
    II. Choose apex + www path
        a. DNS stays at Squarespace
            ↪ confirm whether its DNS supports what the apex
            needs (CNAME flattening/ALIAS)
        b. DNS hosting moves to Cloudflare
            ↪ if not supported: add the site as a free zone,
            import records, switch nameservers, keeping
            registration where it is
        c. rollback procedure and time
            ↪ moving DNS weakens the "instant rollback"
            property; state the actual rollback procedure and
            time for whichever path is taken
    III. Lower TTLs first
        ↪ if the current host allows it
    IV. Add Pages custom domains
        ↪ in Cloudflare Pages > acme-studio > Custom domains,
        add acme-studio.com and www.acme-studio.com, then make
        the DNS changes it prescribes
    V. Verify
        a. apex + www over HTTPS
        b. cert issued
        c. http->https works
        d. www/apex canonicalization works
        e. /about returns 200
            ↪ https://acme-studio.com/about (extensionless)
    VI. Save rollback note
        ↪ give the exact rollback steps as a saved note, and a
        reminder to submit the sitemap in Google Search Console
        after cutover
- Open issue
    ▸ Contact form
        ↪ the backend is not functional yet and is being fixed
        separately; completing DNS today is accepted, and the
        launch decision is the user's
```
