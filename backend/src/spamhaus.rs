// src/spamhaus.rs
use reqwest::Client;
use serde_json::Value;
use std::collections::HashMap;
use std::error::Error;

const SPAMHAUS_ENDPOINT: &str =
    "https://www.spamhaus.org/api/v1/sia-proxy/api/intel/v2/byobject/domain";

pub async fn get_data(search: &str) -> Result<HashMap<String, f64>, Box<dyn Error>> {
    // Extract effective second-level domain (e.g., "example.com")
    let domain_parts: Vec<&str> = search.split('.').collect();
    let root = if domain_parts.len() >= 2 {
        format!(
            "{}.{}",
            domain_parts[domain_parts.len() - 2],
            domain_parts[domain_parts.len() - 1]
        )
    } else {
        search.to_string()
    };

    let url = format!("{}/{}/overview", SPAMHAUS_ENDPOINT, root);
    let client = Client::new();

    let res = client
        .get(&url)
        .header("User-Agent", "Actix-Web Client")
        .send()
        .await?;

    if !res.status().is_success() {
        // If the response is not successful, return an empty hashmap.
        return Ok(HashMap::new());
    }

    let data: Value = res.json().await?;

    let mut spamhaus = HashMap::new();

    // Extract score: try as f64; if that fails, try as str and parse.
    let score_value = if let Some(num) = data["score"].as_f64() {
        num
    } else if let Some(s) = data["score"].as_str() {
        s.parse::<f64>().unwrap_or(0.0)
    } else {
        0.0
    };
    spamhaus.insert("score".to_string(), score_value);

    // Extract each dimension as a f64
    if let Some(dimensions) = data.get("dimensions") {
        for key in ["human", "identity", "infra", "malware", "smtp"] {
            let value = if let Some(num) = dimensions.get(key).and_then(|v| v.as_f64()) {
                num
            } else if let Some(s) = dimensions.get(key).and_then(|v| v.as_str()) {
                s.parse::<f64>().unwrap_or(0.0)
            } else {
                0.0
            };
            spamhaus.insert(key.to_string(), value);
        }
    }

    if let Some(whois) = data.get("whois") {
        let created_ts = whois.get("created").and_then(|v| v.as_i64()).unwrap_or(0);
        let expires_ts = whois.get("expires").and_then(|v| v.as_i64()).unwrap_or(0);
        if expires_ts > created_ts {
            let days = (expires_ts - created_ts) as f64 / 86400.0;
            spamhaus.insert("Domain_registration_length".to_string(), days);
        }
    }
    println!("Spamhaus values: {:?}", spamhaus);

    Ok(spamhaus)
}
