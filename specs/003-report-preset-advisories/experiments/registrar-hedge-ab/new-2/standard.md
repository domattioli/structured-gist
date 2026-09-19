- Domain migration
    ▸ Domain
        ↪ deeznutz.com
    ▸ From
        ↪ the old Squarespace site
    ▸ To
        ↪ an already-deployed Cloudflare Pages site
    ▸ Guidance style
        ↪ Guide the user click-by-click; they are logged
          into the relevant dashboards and can screen-share
          tabs.
- New site
    ▸ Project
        ↪ Cloudflare Pages project "deeznutz"
    ▸ Address
        ↪ live at https://deeznutz.pages.dev
    ▸ Deploy method
        ↪ direct wrangler uploads, not git-connected
    ▸ Account
        ↪ Cloudflare account name personal-account
- Protected sibling project
    ▸ Project
        ↪ "personal-portfolio", at personal-portfolio.pages.dev
    ▸ Shared surface
        ↪ It sits in the same Cloudflare account as the
          "deeznutz" project.
    ▸ Rule
        ↪ Marked CRITICAL: do not touch that project or
          its DNS.
- Old Squarespace site
    ▸ Status
        ↪ still live at deeznutz.com
    ▸ Role after cutover
        ↪ It must remain intact as a rollback target for
          about two weeks.
    ▸ Preferred cutover
        ↪ a DNS-record cutover the user can revert in
          minutes
    ▸ Destructive steps to avoid
        a. cancel the Squarespace subscription
        b. delete the Squarespace site
        c. transfer the domain registration now
- Registrar unconfirmed
    ▸ Likely
        ↪ Squarespace Domains, because the site was built
          there.
    ▸ Possible alternatives
        a. Google Domains legacy
        b. another registrar
    ▸ Resolution
        ↪ Step 1 is identifying it with the user, using
          whois plus what the Squarespace or Domains
          dashboard shows.
- Requested steps, in order
    I. identify registrar and DNS host
        ▸ Deliverable
            ↪ List the current DNS records so there is a
              written rollback snapshot before anything
              changes.
    II. decide the apex and www path
        ▸ Goal
            ↪ Pick the cleanest way to point apex and www
              at the Pages project.
        ▸ Constraint check
            ↪ If DNS stays at Squarespace, confirm whether
              its DNS supports what the apex needs, meaning
              CNAME flattening or ALIAS.
        ▸ Fallback
            ↪ If not, walk through moving DNS hosting only
              to Cloudflare while registration stays put.
        ▸ Caveat
            ↪ Note that this weakens the instant-rollback
              property, and state the actual rollback
              procedure and time for whichever path is
              taken.
    III. lower TTLs first
        ▸ Condition
            ↪ Only if the current DNS host allows it.
    IV. add the custom domains
        ▸ Location
            ↪ Cloudflare Pages > deeznutz > Custom domains
        ▸ Domains
            a. deeznutz.com
            b. www.deeznutz.com
        ▸ Follow-up
            ↪ Then make the DNS changes it prescribes.
    V. verify the cutover
        ▸ Checks
            a. apex and www resolve over HTTPS
            b. cert issued
            c. http to https redirect
            d. www and apex canonicalization
            e. /about extensionless returns 200
    VI. close out
        ▸ Rollback note
            ↪ Give the exact rollback steps as a saved note.
        ▸ Reminder
            ↪ Remind the user to submit the sitemap in
              Google Search Console after cutover.
- Known open issue
    ▸ Contact form
        ↪ The site's contact form backend is not functional
          yet and is being fixed separately.
    ▸ Accepted risk
        ↪ If DNS completes today, that is accepted.
    ▸ Ownership
        ↪ The launch decision belongs to the user.
