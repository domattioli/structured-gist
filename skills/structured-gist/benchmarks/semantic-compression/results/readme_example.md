### registrar-hedge (Before / After)

#### Before (source)

```
Task: migrate the domain acme-studio.com from the old Squarespace site to an
already-deployed Cloudflare Pages site. Guide me click-by-click; I'll be
logged into the relevant dashboards and can screen-share tabs.

Context:
- New site: Cloudflare Pages project "acme-studio", live at
  https://acme-studio.pages.dev (direct wrangler uploads, not git-connected).
  Cloudflare account name: personal-account.
- CRITICAL: the same Cloudflare account also hosts my personal site (project
  "personal-portfolio" / personal-portfolio.pages.dev). Do not touch that project or its DNS.
- Old site: Squarespace, still live at acme-studio.com. It must remain
  intact as a rollback target for ~2 weeks after cutover. Prefer a DNS-record
  cutover I can revert in minutes; avoid destructive steps (do not cancel the
  Squarespace subscription, do not delete the Squarespace site, do not
  transfer the domain registration itself right now).
- Registrar is unconfirmed - likely Squarespace Domains (site was built
  there), possibly Google Domains legacy or another registrar. Step 1 is
  identifying it with me (whois + what the Squarespace/Domains dashboard shows).

What I need from you, in order:
1. Identify registrar + current DNS host for acme-studio.com; list current
   DNS records so we have a written rollback snapshot before changing anything.
2. Decide the cleanest path for pointing apex + www at the Pages project.
   Constraint check: if the DNS stays at Squarespace, confirm whether its DNS
   supports what the apex needs (CNAME flattening/ALIAS); if not, walk me
   through moving just DNS hosting to Cloudflare (add site as a free zone,
   import records, switch nameservers) while keeping registration where it is,
   and note that this weakens the "instant rollback" property - tell me the
   actual rollback procedure and time for whichever path we take.
3. Lower TTLs first if the current host allows it.
4. In Cloudflare Pages > acme-studio > Custom domains: add acme-studio.com
   and www.acme-studio.com, then make the DNS changes it prescribes.
5. Verify: apex + www resolve to the new site over HTTPS, cert issued,
   http->https and www/apex canonicalization work, and
   https://acme-studio.com/about (extensionless) returns 200.
6. Give me the exact rollback steps as a saved note, and remind me to submit
   the sitemap in Google Search Console after cutover.

Known open issue, for your awareness: the site's contact form backend is not
functional yet (being fixed separately). If we complete DNS today, that's
accepted - launch decision is mine.

```

#### After (structured-gist rendering)

```text
- Domain migration
    ▸ Goal
        ↪ move acme-studio.com from the old Squarespace site
        to an already-deployed Cloudflare Pages site
    ▸ Mode
        ↪ guide click-by-click; the user is logged into the
        relevant dashboards and can screen-share tabs
- New site
    ▸ Project
        a. Cloudflare Pages project "acme-studio"
        b. live at https://acme-studio.pages.dev
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
        ↪ Squarespace, still live at acme-studio.com
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

```

**Metrics:**
- Source: 381 words
- Rendering: 272 words
- Compression: 28.6%

**Key structure:**
- The registrar hedge is the concept node `Registrar unconfirmed`, so the uncertainty is stated on the node itself
- Its `▸ Candidates` attribute lists three enumerated children (a./b./c.), each keeping its own qualifier: Squarespace Domains as likely, Google Domains legacy as possibly, and another registrar
- The `▸ First step` explanation keeps how to identify the registrar: from whois and the Squarespace/Domains dashboard, with the user
