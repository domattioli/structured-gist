- Domain migration
    ▸ Goal
        ↪ migrate deeznutz.com from the old Squarespace
          site to an already-deployed Cloudflare Pages
          site.
    ▸ Mode
        ↪ guide me click-by-click; I am logged into the
          relevant dashboards and can screen-share tabs.
- New site
    ▸ Project
        a. Cloudflare Pages "deeznutz"
        b. https://deeznutz.pages.dev
    ▸ Deploy
        a. direct wrangler uploads
        b. not git-connected
    ▸ Account
        a. personal-account
- Do-not-touch
    ↪ CRITICAL: the same Cloudflare account also hosts
      my personal site, so that project and its DNS stay
      untouched.
    ▸ Project
        a. personal-portfolio
        b. personal-portfolio.pages.dev
- Old site
    ▸ State
        a. Squarespace
        b. still live at deeznutz.com
    ▸ Role
        ↪ it must remain intact as a rollback target for
          ~2 weeks after cutover.
    ▸ Preference
        ↪ prefer a DNS-record cutover I can revert in
          minutes, avoiding destructive steps.
    ▸ Excluded now
        a. cancel Squarespace subscription
        b. delete the Squarespace site
        c. transfer the domain registration
- Registrar
    ▸ Certainty
        ↪ unconfirmed - likely Squarespace Domains since
          the site was built there, possibly Google
          Domains legacy or another registrar.
    ▸ Resolution
        ↪ step 1 is identifying it with me, via whois and
          what the Squarespace/Domains dashboard shows.
- Ordered asks
    I. identify registrar + current DNS host
        ↪ list current DNS records so we have a written
          rollback snapshot before changing anything.
    II. decide cleanest apex + www path
        ↪ if DNS stays at Squarespace, confirm whether
          its DNS supports what the apex needs.
    III. lower TTLs first if the current host allows it
    IV. add custom domains in Pages
        ↪ in Cloudflare Pages > deeznutz > Custom
          domains, add deeznutz.com and www.deeznutz.com,
          then make the DNS changes it prescribes.
    V. verify the cutover
        a. apex + www resolve over HTTPS
        b. cert issued
        c. http->https and www/apex canonicalization
        d. /about extensionless returns 200
    VI. close out
        a. exact rollback steps as a saved note
        b. remind me to submit the sitemap
- Known open issue
    ▸ Contact form
        ↪ the site's contact form backend is not
          functional yet and is being fixed separately.
    ▸ Decision
        ↪ if we complete DNS today that is accepted - the
          launch decision is mine.
