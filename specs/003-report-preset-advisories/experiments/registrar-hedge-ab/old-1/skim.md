- Migration task
    ▸ Goal
        ↪ move deeznutz.com off the old Squarespace
          site and onto the already-deployed
          Cloudflare Pages site.
    ▸ Format
        ↪ guide click-by-click; the operator is
          logged into the dashboards and can
          screen-share tabs.
- New site
    ▸ Project
        a. Cloudflare Pages "deeznutz"
        b. live at deeznutz.pages.dev
    ▸ Deploy method
        ↪ direct wrangler uploads, not
          git-connected.
    ▸ Account
        a. personal-account
- Do not touch
    ▸ Same account
        a. project "personal-portfolio"
        b. personal-portfolio.pages.dev
        c. its DNS
- Old site
    ▸ State
        a. Squarespace, still live
    ▸ Retention
        ↪ must stay intact as a rollback target
          for about two weeks after cutover.
    ▸ Forbidden steps
        a. cancel Squarespace subscription
        b. delete the Squarespace site
        c. transfer domain registration now
- Registrar
    ▸ Status
        a. unconfirmed
    ▸ Candidates
        a. Squarespace Domains, likely
        b. Google Domains legacy
        c. another registrar
- Ordered asks
    I. identify registrar + DNS host, snapshot
       records
    II. decide apex + www path to Pages
    III. lower TTLs first if allowed
    IV. add custom domains in Pages
    V. verify resolution, cert, redirects
    VI. save rollback note + sitemap reminder
- Known open issue
    ▸ Contact form
        ↪ the backend is not functional yet and
          is being fixed separately.
    ▸ Launch call
        ↪ finishing DNS today is accepted; the
          launch decision is the operator's.
