```text
- Domain migration
    ▸ Task
        ↪ Migrate the domain deeznutz.com from the old
        Squarespace site to an already-deployed Cloudflare
        Pages site.
    ▸ Guidance style
        ↪ Guide the user click-by-click.
        a. user logged into relevant dashboards
        b. user can screen-share tabs
- Context
    ▸ New site
        ↪ The destination is already deployed and reachable
        on its Pages subdomain.
        a. Cloudflare Pages project `deeznutz`
        b. live at `https://deeznutz.pages.dev`
        c. deployed by direct wrangler uploads
        d. not git-connected
        e. account name `personal-account`
    ▸ Critical exclusion
        ↪ The same Cloudflare account also hosts the
        personal site, and it is out of scope.
        a. project `personal-portfolio`
        b. `personal-portfolio.pages.dev`
        c. do not touch the project
        d. do not touch its DNS
    ▸ Old site
        ↪ Squarespace, still live at deeznutz.com.
        a. must remain intact as rollback target
        b. rollback window ~2 weeks after cutover
        c. prefer a revertible DNS-record cutover
    ▸ Forbidden actions
        a. do not cancel the Squarespace subscription
        b. do not delete the Squarespace site
        c. do not transfer domain registration now
    ▸ Registrar
        ↪ Unconfirmed at the outset, so identifying it
        with the user is step 1.
        a. likely Squarespace Domains
        b. possibly Google Domains legacy
        c. possibly another registrar
        d. identify via whois
        e. identify via the Squarespace dashboard
- Requested sequence
    I. Identify registrar and DNS host
        ↪ Establish who holds registration and who serves
        DNS for deeznutz.com.
        a. list current DNS records
        b. keep them as a written rollback snapshot
        c. do this before changing anything
    II. Decide the cleanest apex and www path
        ↪ Pick how apex and www point at the Pages project,
        then run the constraint check below.
        a. if DNS stays at Squarespace
            i. confirm apex support
            ii. CNAME flattening or ALIAS
        b. if Squarespace DNS cannot do it
            i. add the site as a free Cloudflare zone
            ii. import records
            iii. switch nameservers
            iv. keep registration where it is
        c. note the weakened rollback property
        d. state rollback procedure and time per path
    III. Lower TTLs first
        ↪ Do this if the current DNS host allows it.
    IV. Add custom domains in Pages
        ↪ In Cloudflare Pages > deeznutz > Custom domains.
        a. add deeznutz.com
        b. add www.deeznutz.com
        c. make the DNS changes it prescribes
    V. Verify
        a. apex resolves to the new site over HTTPS
        b. www resolves to the new site over HTTPS
        c. cert issued
        d. http to https works
        e. www and apex canonicalization works
        f. `https://deeznutz.com/about` returns 200
            ↪ The extensionless path is the case being
            checked here.
    VI. Close out
        a. exact rollback steps as a saved note
        b. remind to submit the sitemap
            ↪ In Google Search Console, after cutover.
- Known open issue
    ▸ What
        ↪ The site's contact form backend is not functional
        yet and is being fixed separately.
    ▸ Status
        ↪ Shared for awareness only.
    ▸ Decision
        ↪ Completing DNS today is accepted, and the launch
        decision belongs to the user.
```
