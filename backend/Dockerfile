# 1) Builder stage
FROM rust:latest AS builder
WORKDIR /usr/src/app

# 1a) Copy your Cargo manifest
COPY Cargo.toml Cargo.lock ./

# 1b) Copy your source code
COPY src/ ./src/

# 1c) Build your app in release mode
RUN cargo build --release

# 2) Runtime stage: use Bookworm for glibc ≥2.32
FROM debian:bookworm-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    ca-certificates \
    libssl3 \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /usr/src/app/target/release/app /usr/local/bin/app

USER nobody:nogroup
EXPOSE 8000
CMD ["/usr/local/bin/app"]