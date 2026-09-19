- Domain migration
    ↪ The task is to migrate deeznutz.com from the old
      Squarespace site to an already-deployed Cloudflare
      Pages site.
    ▸ Domain
        ↪ deeznutz.com
    ▸ Source
        ↪ the old Squarespace site
    ▸ Target
        ↪ the already-deployed Cloudflare Pages site
    ▸ Guidance style
        ↪ The user asks to be guided click-by-click.
        a. logged into the relevant dashboards
        b. can screen-share tabs
- New site
    ▸ Project
        ↪ Cloudflare Pages project named "deeznutz".
    ▸ Address
        ↪ live at https://deeznutz.pages.dev
    ▸ Deploy method
        ↪ Updated by direct wrangler uploads, not
          git-connected.
    ▸ Account
        ↪ The Cloudflare account name is personal-account.
- Protected sibling project
    ↪ Flagged CRITICAL by the user: the same Cloudflare
      account also hosts their personal site.
    ▸ Project name
        ↪ "personal-portfolio"
    ▸ Address
        ↪ personal-portfolio.pages.dev
    ▸ Rule
        ↪ Do not touch that project or its DNS.
- Old Squarespace site
    ▸ Platform
        ↪ Squarespace
    ▸ Status
        ↪ still live at deeznutz.com
    ▸ Role after cutover
        ↪ It must remain intact as a rollback target for
          about two weeks after cutover.
    ▸ Preferred mechanism
        ↪ The user prefers a DNS-record cutover they can
          revert in minutes.
    ▸ Destructive steps to avoid
        ↪ The user asks to avoid destructive steps.
        a. do not cancel the Squarespace subscription
        b. do not delete the Squarespace site
        c. do not transfer the domain registration itself
           right now
- Registrar unconfirmed
    ↪ The registrar is unconfirmed, so identifying it comes
      before anything else.
    ▸ Likely
        ↪ Squarespace Domains, since the site was built
          there.
    ▸ Possible alternatives
        a. Google Domains legacy
        b. another registrar
    ▸ First action
        ↪ Step 1 is identifying the registrar with the
          user.
        a. whois
        b. what the Squarespace or Domains dashboard shows
- Requested steps, in order
    I. identify registrar and DNS host
        ▸ Subject
            ↪ deeznutz.com
        ▸ Deliverable
            ↪ List the current DNS records.
        ▸ Purpose
            ↪ So there is a written rollback snapshot
              before anything is changed.
    II. decide the apex and www path
        ▸ Goal
            ↪ Decide the cleanest path for pointing apex
              and www at the Pages project.
        ▸ Constraint check
            ↪ If the DNS stays at Squarespace, confirm
              whether its DNS supports what the apex needs.
            a. CNAME flattening
            b. ALIAS
        ▸ Fallback path
            ↪ If it does not, walk the user through moving
              just DNS hosting to Cloudflare while keeping
              registration where it is.
            i. add the site as a free zone
            ii. import records
            iii. switch nameservers
        ▸ Caveat
            ↪ Note that the fallback weakens the instant
              rollback property.
        ▸ Required statement
            ↪ Tell the user the actual rollback procedure
              and time for whichever path is taken.
    III. lower TTLs first
        ▸ Timing
            ↪ before the cutover changes
        ▸ Condition
            ↪ Only if the current DNS host allows it.
    IV. add the custom domains
        ▸ Location
            ↪ Cloudflare Pages > deeznutz > Custom domains
        ▸ Domains to add
            a. deeznutz.com
            b. www.deeznutz.com
        ▸ Follow-up
            ↪ Then make the DNS changes that the Custom
              domains flow prescribes.
    V. verify the cutover
        ▸ Checks
            a. apex resolves to the new site over HTTPS
            b. www resolves to the new site over HTTPS
            c. cert issued
            d. http to https redirect works
            e. www and apex canonicalization works
            f. https://deeznutz.com/about returns 200
        ▸ Note on /about
            ↪ That path is extensionless, so it exercises
              the Pages routing behaviour.
    VI. close out
        ▸ Rollback note
            ↪ Give the exact rollback steps as a saved
              note.
        ▸ Reminder
            ↪ Remind the user to submit the sitemap in
              Google Search Console after cutover.
- Known open issue
    ↪ Shared by the user for awareness, not as a blocker.
    ▸ Contact form
        ↪ The site's contact form backend is not functional
          yet.
    ▸ Handling
        ↪ It is being fixed separately.
    ▸ Accepted risk
        ↪ If DNS completes today, that outcome is accepted.
    ▸ Ownership
        ↪ The launch decision is the user's.
