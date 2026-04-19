// src/ssl_check.rs
use rustls::{RootCertStore, ServerName};
use std::net::ToSocketAddrs;
use std::sync::Arc;
use tokio::net::TcpStream;
use tokio_rustls::{rustls, TlsConnector};

pub async fn check_ssl_issuer(domain: &str) -> Result<f64, Box<dyn std::error::Error>> {
    // 1) Resolve domain:443
    let addr = format!("{domain}:443");
    let socket_addrs = addr.to_socket_addrs()?;
    let first_addr = match socket_addrs.into_iter().next() {
        Some(a) => a,
        None => return Ok(1.0), // Could not resolve => treat as untrusted
    };

    // 2) Connect TCP
    let tcp = TcpStream::connect(first_addr).await?;

    // 3) Build a RootCertStore (currently empty, which will make the handshake untrusted)
    let mut root_store = RootCertStore::empty();
    for cert in rustls_native_certs::load_native_certs()? {
        root_store.add(&rustls::Certificate(cert.0))?;
    }

    // To trust actual certificates, load system roots:
    // for example, using the rustls-native-certs crate

    // 4) Create a minimal ClientConfig
    let config = rustls::ClientConfig::builder()
        .with_safe_default_cipher_suites()
        .with_safe_default_kx_groups()
        .with_safe_default_protocol_versions()?
        .with_root_certificates(root_store)
        .with_no_client_auth();

    let connector = TlsConnector::from(Arc::new(config));

    // 5) Convert domain to a ServerName for TLS
    let server_name = ServerName::try_from(domain)?;

    // 6) Attempt TLS handshake
    let tls_stream = connector.connect(server_name, tcp).await;

    // 7) Return 0.0 if handshake is OK ('trusted'), or 1.0 if it fails ('untrusted')
    match tls_stream {
        Ok(_) => Ok(0.0),
        Err(_) => Ok(1.0),
    }
}
