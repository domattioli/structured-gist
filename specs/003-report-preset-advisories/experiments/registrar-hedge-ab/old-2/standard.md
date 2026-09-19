```text
- Domain migration
    ▸ Goal
        ↪ Migrate the domain deeznutz.com from the old
        Squarespace site to an already-deployed Cloudflare
        Pages site.
    ▸ Guidance style
        ↪ Click-by-click guidance, with the user logged into
        the relevant dashboards and able to screen-share
        tabs.
- Context
    ▸ New site
        a. Cloudflare Pages project `deeznutz`
        b. live at `https://deeznutz.pages.dev`
        c. direct wrangler uploads, not git-connected
        d. account `personal-account`
    ▸ Do not touch
        ↪ The same Cloudflare account hosts the personal site
        (project `personal-portfolio`), and neither that
        project nor its DNS may be touched.
    ▸ Old site
        a. Squarespace, still live at deeznutz.com
        b. rollback target for ~2 weeks after cutover
        c. prefer a revertible DNS-record cutover
        d. no cancel, delete, or domain transfer
    ▸ Registrar
        ↪ Unconfirmed — likely Squarespace Domains, possibly
        Google Domains legacy or another registrar, so
        identifying it with the user is step 1.
- Requested sequence
    I. Identify registrar and DNS host
        ↪ List the current DNS records so there is a written
        rollback snapshot before anything changes.
    II. Choose the apex and www path
        ↪ If DNS stays at Squarespace, confirm whether its
        DNS supports what the apex needs.
        a. CNAME flattening or ALIAS check
        b. otherwise move DNS hosting to Cloudflare
        c. keep registration where it is
        d. state real rollback procedure and time
    III. Lower TTLs first
        ↪ Only if the current DNS host allows it.
    IV. Add custom domains in Pages
        a. deeznutz.com
        b. www.deeznutz.com
        c. make the DNS changes it prescribes
    V. Verify
        a. apex and www resolve over HTTPS
        b. cert issued
        c. http to https redirect
        d. www and apex canonicalization
        e. `/about` returns 200
    VI. Close out
        a. exact rollback steps as a saved note
        b. submit sitemap in Google Search Console
- Known open issue
    ↪ The site's contact form backend is not functional yet
    and is being fixed separately; completing DNS today is
    accepted, and the launch decision is the user's.
```
