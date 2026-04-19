use reqwest::Client;
use serde_json::Value;
use std::collections::HashMap;
use std::error::Error;
use url::Url;

const API_KEY: &str = "2d19db5775msh5e1d78bd4ead909p14a14bjsn35fb153292ce";
const HOST: &str = "similar-web.p.rapidapi.com";

pub async fn check_traffic(input_url: &str) -> Result<u64, Box<dyn Error>> {
    // Extract domain from full URL
    let parsed = Url::parse(input_url)?;
    let domain = parsed.host_str().unwrap_or("").to_string();

    let endpoint = "https://similar-web.p.rapidapi.com/get-analysis";
    let client = Client::new();

    let mut params = HashMap::new();
    params.insert("domain", domain.as_str());

    let res = client
        .get(endpoint)
        .header("X-RapidAPI-Key", API_KEY)
        .header("X-RapidAPI-Host", HOST)
        .query(&params)
        .send()
        .await?;

    let status = res.status();
    let text = res.text().await?;

    if !status.is_success() {
        return Ok(0);
    }

    // Try to parse the JSON body
    let data: Value = serde_json::from_str(&text)?;

    // Use the correct key spelling based on the actual response structure
    let visits_str = data["Engagments"]["Visits"].as_str().unwrap_or("0");
    let visits = visits_str.parse::<f64>().unwrap_or(0.0).round() as u64;

    Ok(visits)
}
