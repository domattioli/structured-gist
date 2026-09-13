Task: migrate the domain mindmatterbh.com from the old Squarespace site to an
already-deployed Cloudflare Pages site. Guide me click-by-click; I'll be
logged into the relevant dashboards and can screen-share tabs.

Context:
- New site: Cloudflare Pages project "mindmatter-bh", live at
  https://mindmatter-bh.pages.dev (direct wrangler uploads, not git-connected).
  Cloudflare account name: [account name redacted].
- CRITICAL: the same Cloudflare account also hosts my personal site (project
  [name redacted] / [redacted]). Do not touch that project or its DNS.
- Old site: Squarespace, still live at mindmatterbh.com. It must remain
  intact as a rollback target for ~2 weeks after cutover. Prefer a DNS-record
  cutover I can revert in minutes; avoid destructive steps (do not cancel the
  Squarespace subscription, do not delete the Squarespace site, do not
  transfer the domain registration itself right now).
- Registrar is unconfirmed - likely Squarespace Domains (site was built
  there), possibly Google Domains legacy or another registrar. Step 1 is
  identifying it with me (whois + what the Squarespace/Domains dashboard shows).

What I need from you, in order:
1. Identify registrar + current DNS host for mindmatterbh.com; list current
   DNS records so we have a written rollback snapshot before changing anything.
2. Decide the cleanest path for pointing apex + www at the Pages project.
   Constraint check: if the DNS stays at Squarespace, confirm whether its DNS
   supports what the apex needs (CNAME flattening/ALIAS); if not, walk me
   through moving just DNS hosting to Cloudflare (add site as a free zone,
   import records, switch nameservers) while keeping registration where it is,
   and note that this weakens the "instant rollback" property - tell me the
   actual rollback procedure and time for whichever path we take.
3. Lower TTLs first if the current host allows it.
4. In Cloudflare Pages > mindmatter-bh > Custom domains: add mindmatterbh.com
   and www.mindmatterbh.com, then make the DNS changes it prescribes.
5. Verify: apex + www resolve to the new site over HTTPS, cert issued,
   http->https and www/apex canonicalization work, and
   https://mindmatterbh.com/about (extensionless) returns 200.
6. Give me the exact rollback steps as a saved note, and remind me to submit
   the sitemap in Google Search Console after cutover.

Known open issue, for your awareness: the site's contact form backend is not
functional yet (being fixed separately). If we complete DNS today, that's
accepted - launch decision is mine.
