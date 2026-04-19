// src/extractor.rs
use regex::Regex;
use reqwest::Client;
use scraper::{Html, Selector};
use std::collections::HashMap;
use std::error::Error;
use url::Url;

use crate::ssl_check::check_ssl_issuer;
// use crate::whois::get_domain_age;
use crate::spamhaus::get_data;
use crate::traffic::check_traffic;

pub async fn extract_features(url: &str) -> Result<HashMap<String, f64>, Box<dyn Error>> {
    let mut features = HashMap::new();
    let parsed = Url::parse(url)?;
    let domain = parsed.host_str().unwrap_or("");

    // URL-level features
    features.insert("URLLength".to_string(), url.len() as f64);
    let ip_regex = Regex::new(r"^\d{1,3}(\.\d{1,3}){3}$")?;
    features.insert(
        "isDomainIP".to_string(),
        if ip_regex.is_match(domain) { 1.0 } else { 0.0 },
    );
    features.insert(
        "NoOfSubDomain".to_string(),
        domain.matches('.').count().saturating_sub(1) as f64,
    );
    features.insert(
        "isHTTPS".to_string(),
        if parsed.scheme() == "https" { 1.0 } else { 0.0 },
    );
    features.insert(
        "Prefix_Suffix".to_string(),
        if domain.contains('-') { 1.0 } else { 0.0 },
    );

    // Digit ratio
    let digits = url.chars().filter(|c| c.is_ascii_digit()).count();
    let total_chars = url.len().max(1);
    features.insert(
        "DigitRatioInURL".to_string(),
        digits as f64 / total_chars as f64,
    );

    // HTML content features
    let client = Client::new();
    let response = client.get(url).send().await?;
    let html = response.text().await?;
    let document = Html::parse_document(&html);

    let title_selector = Selector::parse("title").unwrap();
    features.insert(
        "HasTitle".to_string(),
        if document.select(&title_selector).next().is_some() {
            1.0
        } else {
            0.0
        },
    );

    let desc_selector = Selector::parse("meta[name='description']").unwrap();
    features.insert(
        "HasDescription".to_string(),
        if document.select(&desc_selector).next().is_some() {
            1.0
        } else {
            0.0
        },
    );

    // SSL issuer trust
    let ssl_state = check_ssl_issuer(domain).await.unwrap_or_else(|e| {
        eprintln!("SSL check failed for {}: {}", domain, e);
        1.0
    });
    features.insert("SSLfinal_State".to_string(), ssl_state);

    // features.insert("Domain_registration_length".to_string(), age as f64);

    // Web traffic metrics
    let traffic = check_traffic(url).await.unwrap_or(0);
    features.insert("web_traffic".to_string(), traffic as f64);

    // Spamhaus reputation data
    let reputation = get_data(domain).await.unwrap_or_default();
    features.insert(
        "score".to_string(),
        reputation.get("score").copied().unwrap_or(0.0),
    );
    features.insert(
        "malware".to_string(),
        reputation.get("malware").copied().unwrap_or(0.0),
    );
    features.insert(
        "infra".to_string(),
        reputation.get("infra").copied().unwrap_or(0.0),
    );
    features.insert(
        "identity".to_string(),
        reputation.get("identity").copied().unwrap_or(0.0),
    );
    features.insert(
        "Domain_registration_length".to_string(),
        reputation
            .get("Domain_registration_length")
            .copied()
            .unwrap_or(0.0),
    );
    Ok(features)
}
