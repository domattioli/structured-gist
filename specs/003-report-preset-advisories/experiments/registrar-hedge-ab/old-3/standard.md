- Domain migration
    ▸ Goal
        ↪ move deeznutz.com off the old Squarespace site onto
          an already-deployed Cloudflare Pages site.
    ▸ Guidance mode
        ↪ guide click-by-click; the user is logged into the
          relevant dashboards and can screen-share tabs.
- Context
    ▸ New site
        a. Cloudflare Pages project "deeznutz"
        b. live at https://deeznutz.pages.dev
        c. direct wrangler uploads, not git-connected
        d. account name personal-account
    ▸ Shared-account risk
        ↪ the same Cloudflare account also hosts the personal
          site (project "personal-portfolio"); do not touch
          that project or its DNS.
    ▸ Old site
        a. Squarespace, still live at deeznutz.com
        b. intact ~2 weeks as rollback target
        c. prefer a revertible DNS-record cutover
    ▸ Forbidden actions
        a. cancel the Squarespace subscription
        b. delete the Squarespace site
        c. transfer the domain registration now
    ▸ Registrar
        ↪ unconfirmed — likely Squarespace Domains, possibly
          Google Domains legacy or another registrar.
- Requested steps
    I. identify registrar + DNS host
        ↪ list the current DNS records so there is a written
          rollback snapshot before anything changes.
    II. decide apex + www path
        a. check Squarespace DNS apex support
        b. else move DNS hosting to Cloudflare
        c. state rollback procedure and time
    III. lower TTLs first
        ↪ do this if the current DNS host allows it.
    IV. add Pages custom domains
        ↪ in Cloudflare Pages > deeznutz > Custom domains add
          deeznutz.com and www.deeznutz.com, then make the DNS
          changes it prescribes.
    V. verify
        a. apex + www resolve over HTTPS
        b. cert issued
        c. http->https and www/apex canonicalization
        d. /about extensionless returns 200
    VI. close out
        a. exact rollback steps as a saved note
        b. submit sitemap in Google Search Console
- Known open issue
    ▸ Contact form
        ↪ the site's contact form backend is not functional
          yet and is being fixed separately.
    ▸ Acceptance
        ↪ completing DNS today is accepted; the launch
          decision belongs to the user.
