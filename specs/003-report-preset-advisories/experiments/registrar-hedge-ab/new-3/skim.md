- Domain migration
    ↪ move deeznutz.com from the old Squarespace site to
      an already-deployed Cloudflare Pages site, guided
      click-by-click while I share the dashboards.
    ▸ New site
    ▸ Old site
    ▸ Registrar
- Do-not-touch
    ↪ the same Cloudflare account hosts my personal site,
      project personal-portfolio; do not touch that
      project or its DNS.
- Ordered asks
    I. identify registrar + DNS host, snapshot records
    II. decide cleanest apex + www path
    III. lower TTLs first if the host allows
    IV. add custom domains in Pages, make DNS changes
    V. verify resolution, cert, canonicalization
    VI. save rollback steps, sitemap reminder
- Known open issue
    ↪ the contact form backend is not functional yet and
      is being fixed separately; completing DNS today is
      accepted, the launch decision is mine.
