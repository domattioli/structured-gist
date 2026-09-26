- Migration task
    ▸ Goal
        ↪ move the domain acme-studio.com from the
          old Squarespace site to an already-
          deployed Cloudflare Pages site.
    ▸ Delivery format
        ↪ guide click-by-click; the operator is
          logged into the relevant dashboards
          and can screen-share tabs.
- New site
    ▸ Project
        a. Cloudflare Pages project "acme-studio"
        b. live at https://acme-studio.pages.dev
    ▸ Deploy method
        ↪ direct wrangler uploads, not
          git-connected.
    ▸ Account
        a. personal-account
- Blast-radius limit
    ▸ Shared account
        ↪ the same Cloudflare account also hosts
          the operator's personal site.
        a. project "personal-portfolio"
        b. personal-portfolio.pages.dev
    ▸ Rule
        ↪ do not touch that project or its DNS.
- Old site
    ▸ State
        a. Squarespace
        b. still live at acme-studio.com
    ▸ Retention window
        ↪ it must remain intact as a rollback
          target for about two weeks after
          cutover.
    ▸ Preferred mechanism
        ↪ prefer a DNS-record cutover that is
          revertible in minutes.
    ▸ Forbidden steps
        a. cancel Squarespace subscription
        b. delete the Squarespace site
        c. transfer the registration now
- Registrar
    ▸ Status
        a. unconfirmed
    ▸ Candidates
        a. Squarespace Domains, likely
            ↪ likely because the site was built
              there.
        b. Google Domains legacy
        c. another registrar
    ▸ Resolution
        ↪ step 1 is identifying it together,
          via whois plus what the Squarespace
          or Domains dashboard shows.
- Ordered asks
    I. Identify and snapshot
        a. registrar
        b. current DNS host
        c. current DNS records
            ↪ listed so there is a written
              rollback snapshot before anything
              changes.
    II. Choose the apex + www path
        a. constraint check at Squarespace
            ↪ if DNS stays at Squarespace,
              confirm whether its DNS supports
              what the apex needs, meaning
              CNAME flattening or ALIAS.
        b. fallback: DNS to Cloudflare
            ↪ if not, walk through moving only
              DNS hosting to Cloudflare while
              keeping registration where it is.
        c. state the rollback cost
            ↪ note that this weakens the
              instant-rollback property, and
              give the actual rollback
              procedure and time for whichever
              path is taken.
    III. Lower TTLs first
        ↪ do this before the cutover, if the
          current host allows it.
    IV. Add custom domains
        a. acme-studio.com
        b. www.acme-studio.com
        c. then make the prescribed DNS changes
    V. Verify
        a. apex + www resolve over HTTPS
        b. cert issued
        c. http to https redirect
        d. www/apex canonicalization
        e. /about returns 200
    VI. Close out
        a. rollback steps as a saved note
        b. sitemap reminder for Search Console
- Known open issue
    ▸ Contact form
        ↪ the site's contact-form backend is not
          functional yet and is being fixed
          separately.
    ▸ Launch call
        ↪ completing DNS today is accepted; the
          launch decision belongs to the
          operator.
