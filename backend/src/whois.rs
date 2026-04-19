// src/whois.rs
use chrono::{DateTime, Utc};
use regex::Regex;
use std::error::Error as StdError;            // <-- alias so we can extend it
use whois_rust::{WhoIs, WhoIsLookupOptions};

type BoxError = Box<dyn StdError + Send + Sync + 'static>;

pub async fn get_domain_age(domain: &str) -> Result<u64, BoxError> {
    // strip “www.”
    let clean_domain = domain.trim_start_matches("www.").to_string();

    // 1) Perform the blocking WHOIS lookup on a thread pool
    let raw: String = tokio::task::spawn_blocking(move || -> Result<_, BoxError> {
        // Use IANA as a fallback registrar
        let whois = WhoIs::from_host("whois.iana.org")?;
        let opts = WhoIsLookupOptions::from_string(clean_domain)?;
        let resp = whois.lookup(opts)?;
        Ok(resp)
    })
    .await?
    .map_err(|e| e as BoxError)?;  // unwrap the inner Result

    println!("WHOIS raw response:\n{}", raw);

    // 2) Try keyword‑based parsing (case‑insensitive)
    let keywords = [
        "creation date",
        "created on",
        "domain create date",
        "registered on",
    ];
    for line in raw.lines() {
        let lower = line.to_lowercase();
        if keywords.iter().any(|&kw| lower.contains(kw)) {
            if let Some(idx) = line.find(':') {
                let candidate = line[idx + 1..].trim();
                if let Ok(dt) = DateTime::parse_from_rfc3339(candidate)
                    .or_else(|_| DateTime::parse_from_str(candidate, "%Y-%m-%dT%H:%M:%SZ"))
                    .or_else(|_| DateTime::parse_from_str(candidate, "%Y-%m-%d %H:%M:%S"))
                    .or_else(|_| DateTime::parse_from_str(candidate, "%Y-%m-%d"))
                {
                    let days = Utc::now()
                        .signed_duration_since(dt.with_timezone(&Utc))
                        .num_days() as u64;
                    return Ok(days);
                }
            }
        }
    }

    // 3) Fallback: grab the first “YYYY‑MM‑DD” date anywhere
    let date_re = Regex::new(r"(?m)(?P<d>\d{4}-\d{2}-\d{2})(?:[T ]\d{2}:\d{2}:\d{2}Z?)?")?;
    if let Some(caps) = date_re.captures(&raw) {
        let ds = &caps["d"];
        if let Ok(dt) = DateTime::parse_from_str(ds, "%Y-%m-%d") {
            let days = Utc::now()
                .signed_duration_since(dt.with_timezone(&Utc))
                .num_days() as u64;
            return Ok(days);
        }
    }

    // Nothing matched → return 0
    Ok(0)
}
