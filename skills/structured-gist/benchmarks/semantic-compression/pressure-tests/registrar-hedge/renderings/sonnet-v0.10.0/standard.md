```text
- Migration task
    ▸ Goal
        ↪ Migrate acme-studio.com from the old
        Squarespace site to an already-deployed
        Cloudflare Pages site, guided click-by-click,
        with the user logged into the relevant
        dashboards and able to screen-share tabs.
    ▸ New site
        a. Pages project acme-studio
        b. live at acme-studio.pages.dev
        c. wrangler uploads, not git-connected
        d. account personal-account
- Protected site
    ▸ Constraint
        ↪ CRITICAL: the same Cloudflare account also
        hosts the personal site, project "personal-
        portfolio" (personal-portfolio.pages.dev). Do
        not touch that project or its DNS.
- Old site
    ▸ Status
        ↪ Squarespace, still live at acme-studio.com. It
        must remain intact as a rollback target for
        about 2 weeks after cutover.
    ▸ Preferred approach
        ↪ A DNS-record cutover that can be reverted in
        minutes.
    ▸ Forbidden steps
        a. cancel Squarespace subscription
        b. delete Squarespace site
        c. transfer domain registration now
- Registrar
    ▸ Certainty
        ↪ Unconfirmed. Likely Squarespace Domains (site
        was built there), possibly Google Domains legacy
        or another registrar.
    ▸ First step
        ↪ Identify it together using whois and what the
        Squarespace/Domains dashboard shows.
- Requested steps
    I. Identify registrar and DNS host
        ↪ Also list current DNS records, so a written
        rollback snapshot exists before anything
        changes.
    II. Decide apex and www path
        ↪ Choose the cleanest way to point apex and www
        at the Pages project. If DNS stays at
        Squarespace, confirm whether it supports what
        the apex needs (CNAME flattening/ALIAS). If not,
        walk through moving just DNS hosting to
        Cloudflare (add site as a free zone, import
        records, switch nameservers) while keeping
        registration where it is. This weakens the
        instant-rollback property, so state the actual
        rollback procedure and time for whichever path
        is taken.
    III. Lower TTLs
        ↪ Do this first, if the current host allows it.
    IV. Add custom domains
        ↪ In Cloudflare Pages > acme-studio > Custom
        domains, add acme-studio.com and www.acme-
        studio.com, then make the DNS changes it
        prescribes.
    V. Verify
        a. apex and www resolve over HTTPS
        b. certificate issued
        c. http to https redirect works
        d. www/apex canonicalization works
        e. /about (extensionless) returns 200
    VI. Save rollback note
        ↪ Give the exact rollback steps as a saved note,
        and remind the user to submit the sitemap in
        Google Search Console after cutover.
- Known issue
    ▸ Status
        ↪ The contact form backend is not functional yet
        and is being fixed separately. If DNS completes
        today, that is accepted; the launch decision is
        the user's.
```
