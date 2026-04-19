// src/main.rs
use actix_cors::Cors;
use actix_web::{web, App, HttpServer}; // now this resolves
mod detector;
mod extractor;
mod routes;
mod spamhaus;
mod ssl_check;
mod traffic;

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    let port = std::env::var("PORT").unwrap_or_else(|_| "8000".to_string());
    let bind_address = format!("0.0.0.0:{}", port);
    // println!("Listening on http://{}", bind_address);

    HttpServer::new(|| {
        App::new()
            .wrap(
                Cors::default()
                    .allow_any_origin()
                    .allowed_methods(vec!["GET", "POST", "OPTIONS"])
                    .allowed_header(actix_web::http::header::CONTENT_TYPE)
                    .allowed_header(actix_web::http::header::ACCEPT)
                    .supports_credentials(),
            )
            .service(web::resource("/health").route(web::get().to(routes::health)))
            .service(web::resource("/receive_url").route(web::post().to(routes::receive_url)))
    })
    .bind(bind_address)?
    .run()
    .await
}
