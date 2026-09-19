- Domain migration
    ▸ Goal
        ↪ migrate the domain deeznutz.com from the old
          Squarespace site to an already-deployed
          Cloudflare Pages site.
    ▸ Mode
        i. guide me click-by-click
        ii. I will be logged into the dashboards
        iii. I can screen-share tabs
- New site
    ▸ Project
        a. Cloudflare Pages project "deeznutz"
        b. live at https://deeznutz.pages.dev
    ▸ Deploy
        a. direct wrangler uploads
        b. not git-connected
    ▸ Account
        a. personal-account
- Do-not-touch
    ↪ CRITICAL: the same Cloudflare account also hosts my
      personal site, so that project and its DNS must be
      left alone.
    ▸ Project
        a. personal-portfolio
        b. personal-portfolio.pages.dev
    ▸ Scope
        a. do not touch that project
        b. do not touch its DNS
- Old site
    ▸ State
        a. Squarespace
        b. still live at deeznutz.com
    ▸ Role
        ↪ it must remain intact as a rollback target for
          ~2 weeks after cutover.
    ▸ Preference
        ↪ prefer a DNS-record cutover I can revert in
          minutes, and avoid destructive steps.
    ▸ Excluded now
        a. do not cancel the Squarespace subscription
        b. do not delete the Squarespace site
        c. do not transfer the domain registration itself
           right now
- Registrar
    ▸ Certainty
        ↪ unconfirmed - likely Squarespace Domains since
          the site was built there, possibly Google
          Domains legacy or another registrar.
    ▸ Resolution
        ↪ step 1 is identifying it with me.
        a. whois
        b. what the Squarespace/Domains dashboard shows
- Ordered asks
    I. identify registrar + current DNS host
        ↪ for deeznutz.com, and list the current DNS
          records so we have a written rollback snapshot
          before changing anything.
    II. decide the cleanest path for apex + www
        ↪ the target is pointing apex and www at the
          Pages project.
        ▸ Constraint check
            ↪ if the DNS stays at Squarespace, confirm
              whether its DNS supports what the apex
              needs (CNAME flattening/ALIAS).
        ▸ Fallback
            ↪ if not, walk me through moving just DNS
              hosting to Cloudflare while keeping
              registration where it is.
            i. add site as a free zone
            ii. import records
            iii. switch nameservers
        ▸ Caveat
            ↪ note that this weakens the "instant
              rollback" property.
        ▸ Required output
            ↪ tell me the actual rollback procedure and
              time for whichever path we take.
    III. lower TTLs first
        ↪ do this if the current host allows it.
    IV. add the custom domains
        ↪ in Cloudflare Pages > deeznutz > Custom
          domains, then make the DNS changes it
          prescribes.
        a. deeznutz.com
        b. www.deeznutz.com
    V. verify the cutover
        a. apex + www resolve to the new site over HTTPS
        b. cert issued
        c. http->https works
        d. www/apex canonicalization works
        e. https://deeznutz.com/about (extensionless)
           returns 200
    VI. close out
        a. give me the exact rollback steps as a saved
           note
        b. remind me to submit the sitemap in Google
           Search Console after cutover
- Known open issue
    ↪ stated for your awareness, not as a blocker.
    ▸ Contact form
        ↪ the site's contact form backend is not
          functional yet, being fixed separately.
    ▸ Decision
        ↪ if we complete DNS today, that is accepted -
          the launch decision is mine.
