- Domain migration
    ▸ Domain
        ↪ deeznutz.com
    ▸ From
        ↪ the old Squarespace site, still live
    ▸ To
        ↪ an already-deployed Cloudflare Pages site
    ▸ Guidance style
        ↪ Guide click-by-click while the user, logged into
          the dashboards, screen-shares tabs.
- New site
    ▸ Project
        ↪ Cloudflare Pages project "deeznutz"
    ▸ Address
        ↪ https://deeznutz.pages.dev
    ▸ Deploys
        ↪ direct wrangler uploads, not git-connected
    ▸ Account
        ↪ personal-account
- Protected sibling
    ▸ Project
        ↪ personal-portfolio, the user's personal site
    ▸ Rule
        ↪ Do not touch that project or its DNS.
- Old site preserved
    ▸ Role
        ↪ rollback target for about two weeks
    ▸ Preferred cutover
        ↪ a DNS-record change revertible in minutes
    ▸ Forbidden now
        a. cancel Squarespace subscription
        b. delete Squarespace site
        c. transfer domain registration
- Registrar unconfirmed
    ▸ Likely
        ↪ Squarespace Domains, since the site was built there
    ▸ Possible
        a. Google Domains legacy
        b. another registrar
- Requested steps
    I. identify registrar and DNS host
    II. choose the apex and www path
    III. lower TTLs first
    IV. add the custom domains in Pages
    V. verify resolution, cert, canonicalization
    VI. save rollback note, submit sitemap
- Known open issue
    ▸ Contact form
        ↪ The backend is not functional yet and is being
          fixed separately.
    ▸ Launch call
        ↪ Finishing DNS today is accepted; the launch
          decision is the user's.
