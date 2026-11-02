```text
- Migration task
    ▸ Goal
        ↪ Migrate acme-studio.com from the old Squarespace site
        to an already-deployed Cloudflare Pages site. Guide the
        user click-by-click; they will be logged into the
        relevant dashboards and can screen-share tabs.
    ▸ New site
        a. Pages project acme-studio
        b. Live at acme-studio.pages.dev
        c. Deployed by wrangler upload
            ↪ Direct uploads, not git-connected.
        d. Account personal-account
- Constraints
    ▸ Protected project
        ↪ CRITICAL: the same Cloudflare account also hosts the
        personal site, project personal-portfolio at
        personal-portfolio.pages.dev. Do not touch that project
        or its DNS.
    ▸ Old site
        a. Squarespace, live at acme-studio.com
        b. Rollback target
            ↪ It must remain intact for about 2 weeks after
            cutover.
    ▸ Cutover preference
        ↪ Prefer a DNS-record cutover the user can revert in
        minutes; avoid destructive steps.
    ▸ Avoided steps
        a. Cancel Squarespace subscription
        b. Delete Squarespace site
        c. Transfer domain registration now
    ▸ Registrar
        ↪ Unconfirmed. Likely Squarespace Domains, since the
        site was built there; possibly Google Domains legacy
        or another registrar.
- Requested steps
    I. Identify registrar and DNS host
        ↪ Use whois and what the Squarespace or Domains
        dashboard shows. List current DNS records as a written
        rollback snapshot before changing anything.
    II. Choose apex and www path
        ↪ If DNS stays at Squarespace, confirm whether it
        supports what the apex needs: CNAME flattening or
        ALIAS.
        ↪ If not, move just DNS hosting to Cloudflare: add the
        site as a free zone, import records, switch
        nameservers, and keep registration where it is. This
        weakens the instant-rollback property, so give the
        actual rollback procedure and time for the chosen path.
    III. Lower TTLs first
        ↪ Only if the current host allows it.
    IV. Add custom domains
        ↪ In Cloudflare Pages > acme-studio > Custom domains,
        add acme-studio.com and www.acme-studio.com, then make
        the DNS changes it prescribes.
    V. Verify cutover
        a. Apex and www resolve over HTTPS
        b. Certificate issued
        c. http to https redirect works
        d. www and apex canonicalization works
        e. Extensionless /about returns 200
            ↪ The URL is https://acme-studio.com/about.
    VI. Save rollback note
        ↪ Give the exact rollback steps as a saved note, and
        remind the user to submit the sitemap in Google Search
        Console after cutover.
- Known issue
    ▸ Contact form backend
        ↪ Not functional yet; being fixed separately.
    ▸ Launch decision
        ↪ If DNS is completed today, that is accepted. The
        launch decision belongs to the user.
```
