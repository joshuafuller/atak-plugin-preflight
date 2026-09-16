FROM python:3.12-slim

ARG SEMGREP_VERSION=1.161.0
ARG TRIVY_VERSION=0.69.1
ARG SYFT_VERSION=1.42.0
ARG OSV_VERSION=2.5.1

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates curl unzip openjdk-17-jre-headless \
    && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir "semgrep==${SEMGREP_VERSION}"
RUN curl -fsSL "https://github.com/aquasecurity/trivy/releases/download/v${TRIVY_VERSION}/trivy_${TRIVY_VERSION}_Linux-64bit.tar.gz" \
    | tar -xz -C /usr/local/bin trivy
RUN curl -fsSL "https://github.com/anchore/syft/releases/download/v${SYFT_VERSION}/syft_${SYFT_VERSION}_linux_amd64.tar.gz" \
    | tar -xz -C /usr/local/bin syft
RUN curl -fsSL "https://github.com/google/osv-scanner/releases/download/v${OSV_VERSION}/osv-scanner_linux_amd64" \
    -o /usr/local/bin/osv-scanner && chmod +x /usr/local/bin/osv-scanner

COPY . /opt/atak-plugin-preflight
WORKDIR /workspace
ENTRYPOINT ["python3", "/opt/atak-plugin-preflight/preflight.py"]
