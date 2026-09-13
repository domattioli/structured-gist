- Domain migration: mindmatterbh.com Squarespace → Cloudflare Pages
    ▸ Current state
        a. old site: Squarespace at mindmatterbh.com (live)
        b. new site: Cloudflare Pages (mindmatter-bh.pages.dev)
        c. same CF account hosts personal site (do not touch)
    ▸ Registrar for mindmatterbh.com
        ↪ unconfirmed — must identify in Step 1
        a. Squarespace Domains (site built there, most likely)
        b. Google Domains legacy (possible)
        c. Another registrar (possible)
    ▸ Step 1: Identify registrar + DNS host
        ↪ check registrar via whois + Squarespace/Domains
          dashboard
        a. list all current DNS records (written snapshot)
        b. snapshot saved for rollback reference
    ▸ Step 2: Choose DNS hosting path
        ↪ constraint: if Squarespace hosts DNS, must
          support CNAME flattening/ALIAS for apex
        I. Path A: keep DNS at Squarespace
            ↪ only if it supports ALIAS/CNAME flattening
        II. Path B: move DNS to Cloudflare
            a. add site as free zone
            b. import existing records
            c. switch nameservers
            ↪ tradeoff: instant rollback becomes
              documented-procedure rollback
    ▸ Preference
        ↪ record-level cutover (revertible in minutes);
          avoid destructive steps
        a. do NOT cancel Squarespace subscription
        b. do NOT delete Squarespace site
        c. do NOT transfer domain registration yet
    ▸ Step 3: Reduce TTLs
        ↪ before cutover, lower TTLs if possible on
          current DNS host
    ▸ Step 4: Add custom domains in Cloudflare
        ↪ Cloudflare Pages UI > mindmatter-bh > Custom
          domains
        a. add mindmatterbh.com
        b. add www.mindmatterbh.com
        c. apply prescribed DNS changes
    ▸ Step 5: Verify cutover
        a. apex + www resolve to new site over HTTPS
        b. cert issued correctly
        c. http → https redirect works
        d. www ↔ apex canonicalization correct
        e. extensionless paths return 200 (e.g.,
           /about)
    ▸ Step 6: Documentation + notification
        a. save exact rollback steps (procedure + timing)
        b. remind user to submit sitemap to Google Search
           Console
    ▸ Rollback requirement
        ↪ old site must remain intact ~2 weeks post-cutover
        a. enables fast revert if needed
        b. DNS revert fastest on path A, slower on path B
    ▸ Open issue
        ↪ contact form backend not functional (separate
          fix in progress)
        a. user accepts this risk
        b. launch decision belongs to user
        c. does not block DNS migration
