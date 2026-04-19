// src/detector.rs
use std::collections::HashMap;

pub fn rule_based_phishing_detector(features: &HashMap<String, f64>) -> String {
    let mut suspicion_score = 0.0;
    println!("Features hashmap: {:?}", features);

    if *features.get("Domain_registration_length").unwrap_or(&0.0) < 366.0 {
        suspicion_score += 2.0;
    }
    if *features.get("isDomainIP").unwrap_or(&0.0) == 1.0 {
        suspicion_score += 2.0;
    }
    if *features.get("NoOfSubDomain").unwrap_or(&0.0) >= 3.0 {
        suspicion_score += 1.0;
    }
    if *features.get("URLLength").unwrap_or(&0.0) > 75.0 {
        suspicion_score += 1.0;
    }
    if *features.get("DigitRatioInURL").unwrap_or(&0.0) > 0.3 {
        suspicion_score += 1.0;
    }
    if *features.get("Prefix_Suffix").unwrap_or(&0.0) == 1.0 {
        suspicion_score += 1.0;
    }
    if *features.get("SSLfinal_State").unwrap_or(&1.0) == 1.0 {
        suspicion_score += 2.0;
    }
    if *features.get("isHTTPS").unwrap_or(&0.0) == 0.0 {
        suspicion_score += 1.0;
    }
    if *features.get("HasTitle").unwrap_or(&1.0) == 0.0 {
        suspicion_score += 1.0;
    }
    if *features.get("HasDescription").unwrap_or(&1.0) == 0.0 {
        suspicion_score += 1.0;
    }
    if *features.get("score").unwrap_or(&0.0) <= 0.0 {
        suspicion_score += 2.0;
    }
    if *features.get("malware").unwrap_or(&0.0) == 1.0 {
        suspicion_score += 3.0;
    }
    if *features.get("infra").unwrap_or(&0.0) == 1.0 {
        suspicion_score += 2.0;
    }
    if *features.get("identity").unwrap_or(&0.0) < 0.0 {
        suspicion_score += 2.0;
    }

    let traffic = *features.get("web_traffic").unwrap_or(&0.0);
    if traffic < 10000.0 {
        suspicion_score += 2.0;
    } else if traffic < 100000.0 {
        suspicion_score += 1.0;
    }

    println!("{}", suspicion_score);

    if suspicion_score >= 4.0 {
        "phishing".to_string()
    } else {
        "legitimate".to_string()
    }
}
