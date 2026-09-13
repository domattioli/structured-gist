- Domain migration
    ▸ Scope
        ↪ move mindmatterbh.com from Squarespace to
          Cloudflare Pages; Squarespace stays as rollback
          for ~2 weeks
    ▸ Registrar for mindmatterbh.com
        ↪ unconfirmed — likely Squarespace Domains,
          possibly Google Domains legacy, or another
          registrar
        a. Squarespace Domains
        b. Google Domains legacy
        c. Another registrar
    ▸ Step 1
        ↪ identify which registrar + current DNS host,
          snapshot all current DNS records before any changes
    ▸ DNS hosting decision
        I. if Squarespace hosts DNS: confirm it supports
           CNAME flattening/ALIAS for apex
        II. if not: move DNS to Cloudflare (free zone,
            import records, switch nameservers)
    ▸ Tradeoff
        ↪ DNS move weakens instant-rollback property;
          requires documented procedure instead
    ▸ Preference
        ↪ record-level cutover that reverts in minutes;
          no destructive steps (keep Squarespace site + subscription intact,
          do not transfer domain registration yet)
    ▸ Steps
        I. lower TTLs
        II. add custom domains (apex + www) in Cloudflare
            Pages UI
        III. apply DNS changes it prescribes
        IV. verify HTTPS, certs, canonicalization,
            extensionless paths
        V. save exact rollback procedure
        VI. submit sitemap to Google Search Console
    ▸ Open issue
        ↪ contact form backend is broken (being fixed
          separately) but user accepts the risk and will
          proceed
