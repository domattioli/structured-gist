- Migration task
    ▸ Goal
        ↪ migrate the domain deeznutz.com from
          the old Squarespace site to an
          already-deployed Cloudflare Pages
          site.
    ▸ Delivery format
        ↪ guide the operator click-by-click
          rather than acting for them.
        a. operator logged into dashboards
        b. can screen-share tabs
- New site
    ▸ Platform
        a. Cloudflare Pages
        b. project name "deeznutz"
    ▸ Current address
        a. https://deeznutz.pages.dev
            ↪ already live at that address.
    ▸ Deploy method
        ↪ direct wrangler uploads, so the
          project is not git-connected.
    ▸ Cloudflare account
        a. personal-account
- Blast-radius limit
    ▸ Shared account
        ↪ the same Cloudflare account also hosts
          the operator's personal site.
        a. project "personal-portfolio"
        b. personal-portfolio.pages.dev
    ▸ Rule
        ↪ marked CRITICAL in the brief: do not
          touch that project or its DNS.
- Old site
    ▸ Platform
        a. Squarespace
    ▸ State
        a. still live at deeznutz.com
    ▸ Retention window
        ↪ it must remain intact as a rollback
          target for roughly two weeks after
          cutover.
    ▸ Preferred mechanism
        ↪ prefer a DNS-record cutover that the
          operator can revert in minutes.
    ▸ Destructive steps to avoid
        a. cancel the Squarespace subscription
        b. delete the Squarespace site
        c. transfer the domain registration
            ↪ registration transfer is out of
              scope right now, not forever.
- Registrar
    ▸ Status
        a. unconfirmed
    ▸ Candidates
        a. Squarespace Domains
            ↪ the likeliest, because the site
              was built there.
        b. Google Domains legacy
        c. some other registrar
    ▸ Resolution
        ↪ identifying the registrar is step 1
          and is done together with the
          operator.
        a. whois lookup
        b. what the Squarespace or Domains
           dashboard shows
- Ordered asks
    I. Identify and snapshot
        a. registrar for deeznutz.com
        b. current DNS host
        c. current DNS records
            ↪ list them so there is a written
              rollback snapshot in hand before
              anything is changed.
    II. Choose the apex + www path
        ↪ decide the cleanest way to point both
          apex and www at the Pages project.
        a. constraint check, DNS stays put
            ↪ if the DNS stays at Squarespace,
              confirm whether its DNS supports
              what the apex needs.
            i. CNAME flattening
            ii. ALIAS record
        b. fallback, DNS moves to Cloudflare
            ↪ if Squarespace DNS cannot do it,
              walk through moving only the DNS
              hosting to Cloudflare.
            i. add the site as a free zone
            ii. import existing records
            iii. switch nameservers
            ↪ registration stays where it is
              under this path.
        c. rollback cost disclosure
            ↪ note that the nameserver move
              weakens the instant-rollback
              property.
            i. actual rollback procedure
            ii. actual rollback time
            ↪ state both for whichever path is
              taken, not only the fallback.
    III. Lower TTLs first
        ↪ do this ahead of the cutover, if the
          current DNS host allows it.
    IV. Add the custom domains
        ▸ Location
            ↪ Cloudflare Pages > deeznutz >
              Custom domains.
        a. deeznutz.com
        b. www.deeznutz.com
        c. make the DNS changes it prescribes
            ↪ apply them after adding both
              domains.
    V. Verify
        a. apex resolves to the new site
        b. www resolves to the new site
            ↪ both over HTTPS.
        c. certificate issued
        d. http to https redirect works
        e. www/apex canonicalization works
        f. https://deeznutz.com/about
            ↪ the extensionless path must
              return 200.
    VI. Close out
        a. exact rollback steps
            ↪ delivered as a saved note.
        b. sitemap reminder
            ↪ remind the operator to submit the
              sitemap in Google Search Console
              after cutover.
- Known open issue
    ▸ Scope
        ↪ raised for awareness only, not as work
          to do here.
    ▸ Contact form
        ↪ the site's contact-form backend is not
          functional yet and is being fixed
          separately.
    ▸ Acceptance
        ↪ if DNS is completed today, that is
          accepted.
    ▸ Ownership
        ↪ the launch decision belongs to the
          operator.
