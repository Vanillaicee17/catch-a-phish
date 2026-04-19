// src/routes.rs
use crate::detector::rule_based_phishing_detector;
use crate::extractor::extract_features;
use actix_web::{web, HttpResponse, Responder};
use serde::{Deserialize, Serialize};

#[derive(Deserialize)]
pub struct UrlRequest {
    pub url: String,
}

#[derive(Serialize)]
pub struct UrlResponse {
    pub result: String,
}

#[derive(Serialize)]
pub struct HealthResponse {
    pub status: &'static str,
}

pub async fn health() -> impl Responder {
    HttpResponse::Ok().json(HealthResponse { status: "ok" })
}

pub async fn receive_url(req: web::Json<UrlRequest>) -> impl Responder {
    let url = req.url.clone();
    let features = match extract_features(&url).await {
        Ok(features) => features,
        Err(e) => {
            return HttpResponse::InternalServerError().json(UrlResponse {
                result: format!("error: {}", e),
            })
        }
    };
    let result = rule_based_phishing_detector(&features);
    HttpResponse::Ok().json(UrlResponse { result })
}
