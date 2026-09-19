```text
- Domain migration
    ▸ Goal
        ↪ Move deeznutz.com off the old Squarespace site and
        onto the already-deployed Cloudflare Pages site.
    ▸ Guidance style
        ↪ Click-by-click, with the user logged into the
        dashboards and able to screen-share tabs.
- Constraints
    a. old Squarespace site stays live ~2 weeks
    b. personal-portfolio project untouched
    c. revertible DNS cutover, no destructive steps
    d. registrar unconfirmed
- Requested sequence
    I. identify registrar and DNS host
    II. choose apex and www path
    III. lower TTLs first
    IV. add custom domains in Pages
    V. verify resolution, cert, canonicalization
    VI. save rollback note, sitemap reminder
- Known open issue
    ↪ The contact form backend is not functional yet and is
    being fixed separately; the launch decision is the
    user's.
```
