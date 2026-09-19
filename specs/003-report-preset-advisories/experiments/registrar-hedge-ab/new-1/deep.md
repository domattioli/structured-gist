- Domain migration
    ▸ Goal
        ↪ migrate the domain deeznutz.com from the old
        Squarespace site to an already-deployed Cloudflare
        Pages site
    ▸ Guidance mode
        ↪ guide the user click-by-click
    ▸ User posture
        a. logged into the relevant dashboards
        b. can screen-share tabs
- New site
    ▸ Project
        ↪ Cloudflare Pages project "deeznutz"
    ▸ Live URL
        ↪ https://deeznutz.pages.dev
    ▸ Deploy method
        ↪ direct wrangler uploads, not git-connected
    ▸ Account
        ↪ the Cloudflare account name is personal-account
- Protected project
    ▸ Severity
        ↪ the user flags this constraint as CRITICAL
    ▸ Identity
        a. project "personal-portfolio"
        b. personal-portfolio.pages.dev
    ▸ Relation
        ↪ the same Cloudflare account also hosts the user's
        personal site
    ▸ Rule
        ↪ do not touch that project or its DNS
- Old site
    ▸ State
        ↪ Squarespace, still live at deeznutz.com
    ▸ Retention
        ↪ it must remain intact as a rollback target for
        about two weeks after cutover
    ▸ Preferred method
        ↪ prefer a DNS-record cutover the user can revert
        in minutes
    ▸ Destructive steps to avoid
        a. cancelling the Squarespace subscription
        b. deleting the Squarespace site
        c. transferring the domain registration now
- Registrar unconfirmed
    ▸ Candidates
        a. Squarespace Domains, likely
        b. Google Domains legacy, possibly
        c. another registrar
    ▸ Reason for the guess
        ↪ the site was built at Squarespace
    ▸ Resolution
        ↪ step 1 is identifying the registrar together with
        the user
    ▸ Evidence sources
        a. whois
        b. what the Squarespace/Domains dashboard shows
- Requested steps
    I. identify registrar + DNS host
        ▸ Targets
            a. registrar for deeznutz.com
            b. current DNS host
        ▸ Deliverable
            ↪ list the current DNS records so there is a
            written rollback snapshot before anything
            changes
    II. decide the apex and www path
        ▸ Objective
            ↪ pick the cleanest path for pointing the apex
            and www at the Pages project
        ▸ Constraint check
            ↪ if DNS stays at Squarespace, confirm whether
            its DNS supports what the apex needs
        ▸ Apex requirement
            ↪ CNAME flattening or ALIAS
        ▸ Fallback path
            i. add the site as a free Cloudflare zone
            ii. import the records
            iii. switch the nameservers
        ▸ Fallback scope
            ↪ move only DNS hosting to Cloudflare while
            keeping registration where it is
        ▸ Caveat
            ↪ note that the fallback weakens the instant
            rollback property
        ▸ Required answer
            ↪ state the actual rollback procedure and time
            for whichever path is taken
    III. lower TTLs first
        ↪ do this only if the current host allows it
    IV. add the custom domains in Pages
        ▸ Location
            ↪ Cloudflare Pages > deeznutz > Custom domains
        ▸ Domains
            a. deeznutz.com
            b. www.deeznutz.com
        ▸ Follow-up
            ↪ then make the DNS changes it prescribes
    V. verify the cutover
        a. apex and www resolve to the new site over HTTPS
        b. cert issued
        c. http to https redirect works
        d. www and apex canonicalization works
        e. https://deeznutz.com/about returns 200
        ↪ the /about check is the extensionless case
    VI. close-out items
        a. exact rollback steps as a saved note
        b. reminder to submit the sitemap
        ↪ the sitemap goes to Google Search Console after
        cutover
- Known open issue
    ▸ Status
        ↪ raised for awareness, not as a blocker
    ▸ Contact form
        ↪ the site's contact form backend is not functional
        yet and is being fixed separately
    ▸ Accepted outcome
        ↪ if DNS completes today that is accepted
    ▸ Ownership
        ↪ the launch decision is the user's
