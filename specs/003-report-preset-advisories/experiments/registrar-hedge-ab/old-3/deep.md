- Domain migration
    ▸ Goal
        ↪ migrate the domain deeznutz.com from the old
          Squarespace site to an already-deployed Cloudflare
          Pages site.
    ▸ Guidance mode
        ↪ guide the user click-by-click; they are logged into
          the relevant dashboards and can screen-share tabs.
- New site
    ▸ Project
        a. Cloudflare Pages project "deeznutz"
        b. live at https://deeznutz.pages.dev
    ▸ Deploy method
        ↪ direct wrangler uploads, not git-connected.
    ▸ Account
        ↪ Cloudflare account name personal-account.
- Shared-account constraint
    ▸ Severity
        ↪ flagged CRITICAL in the brief.
    ▸ Neighbour project
        a. project "personal-portfolio"
        b. personal-portfolio.pages.dev
        c. the user's personal site
    ▸ Rule
        ↪ do not touch that project or its DNS.
- Old site
    ▸ Platform
        ↪ Squarespace, still live at deeznutz.com.
    ▸ Retention
        ↪ it must remain intact as a rollback target for about
          two weeks after cutover.
    ▸ Preferred mechanism
        ↪ prefer a DNS-record cutover that can be reverted in
          minutes; avoid destructive steps.
    ▸ Forbidden actions
        a. cancel the Squarespace subscription
        b. delete the Squarespace site
        c. transfer the domain registration right now
- Registrar
    ▸ Status
        ↪ unconfirmed.
    ▸ Candidates
        a. Squarespace Domains, most likely
        b. Google Domains legacy
        c. another registrar
    ▸ Basis
        ↪ the site was built on Squarespace.
    ▸ First move
        ↪ step 1 is identifying the registrar together, using
          whois plus what the Squarespace or Domains dashboard
          shows.
- Requested steps
    ↪ six items, to be delivered in this order.
    I. identify registrar + DNS host
        a. registrar for deeznutz.com
        b. current DNS host
        c. list current DNS records
        ↪ the record list is the written rollback snapshot,
          taken before anything is changed.
    II. decide apex + www path
        ↪ pick the cleanest way to point apex and www at the
          Pages project.
        a. constraint check at Squarespace
            ↪ if DNS stays at Squarespace, confirm whether its
              DNS supports what the apex needs, meaning CNAME
              flattening or ALIAS.
        b. fallback: move DNS to Cloudflare
            i. add the site as a free zone
            ii. import records
            iii. switch nameservers
            ↪ move DNS hosting only, keeping the domain
              registration where it is.
        c. rollback caveat
            ↪ note that the nameserver move weakens the
              instant-rollback property, and state the actual
              rollback procedure and time for whichever path
              is taken.
    III. lower TTLs first
        ↪ do this before the cutover, if the current DNS host
          allows it.
    IV. add Pages custom domains
        a. deeznutz.com
        b. www.deeznutz.com
        ↪ add them under Cloudflare Pages > deeznutz > Custom
          domains, then make the DNS changes it prescribes.
    V. verify
        a. apex + www resolve to the new site over HTTPS
        b. cert issued
        c. http->https redirect works
        d. www/apex canonicalization works
        e. https://deeznutz.com/about returns 200
            ↪ the extensionless path is the specific case to
              check.
    VI. close out
        a. exact rollback steps as a saved note
        b. reminder to submit the sitemap
            ↪ in Google Search Console, after cutover.
- Known open issue
    ▸ Contact form
        ↪ the site's contact form backend is not functional
          yet and is being fixed separately.
    ▸ Acceptance
        ↪ completing DNS today is accepted even so.
    ▸ Ownership
        ↪ the launch decision is the user's.
