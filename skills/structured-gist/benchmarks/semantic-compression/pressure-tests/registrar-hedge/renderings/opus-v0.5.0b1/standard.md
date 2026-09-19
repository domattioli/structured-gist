- Domain migration
    ▸ Goal
        ↪ move deeznutz.com from the old Squarespace site
        to an already-deployed Cloudflare Pages site
    ▸ Mode
        ↪ guide click-by-click; the user is logged into the
        relevant dashboards and can screen-share tabs
- New site
    ▸ Project
        a. Cloudflare Pages project "deeznutz"
        b. live at https://deeznutz.pages.dev
    ▸ Deploy method
        ↪ direct wrangler uploads, not git-connected
    ▸ Account
        ↪ the Cloudflare account name is personal-account
- Protected project
    ▸ Severity
        ↪ the user marks this one CRITICAL
    ▸ Identity
        a. project "personal-portfolio"
        b. personal-portfolio.pages.dev
    ▸ Rule
        ↪ the same account hosts it, so do not touch that
        project or its DNS
- Old site
    ▸ State
        ↪ Squarespace, still live at deeznutz.com
    ▸ Retention
        ↪ it must remain intact as a rollback target for
        about two weeks after cutover
    ▸ Preference
        ↪ prefer a DNS-record cutover revertible in minutes
    ▸ Avoid
        a. cancelling the Squarespace subscription
        b. deleting the Squarespace site
        c. transferring the registration right now
- Registrar unconfirmed
    ▸ Candidates
        a. Squarespace Domains, likely
        b. Google Domains legacy, possibly
        c. another registrar
    ▸ First step
        ↪ identify it with the user, from whois and what
        the Squarespace/Domains dashboard shows
- Requested steps
    I. identify registrar + current DNS host
    II. decide the apex and www path
    III. lower TTLs first
    IV. add the custom domains in Pages
    V. verify the new site end to end
    VI. rollback note + sitemap reminder
- Known open issue
    ▸ Contact form
        ↪ the site's contact form backend is not functional
        yet and is being fixed separately
    ▸ Accepted
        ↪ completing DNS today is accepted; the launch
        decision is the user's
