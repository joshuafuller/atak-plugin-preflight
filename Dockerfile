FROM python:3.12-slim

ARG SEMGREP_VERSION=1.161.0
ARG TRIVY_VERSION=0.74.0
ARG TRIVY_SHA256=2ae6fe3ee734b7fdf11335663e18c75ea12dccc76062f09f164a3b0f8be4371a
ARG OSV_VERSION=2.5.1
ARG OSV_SHA256=f9f25499a2c8cc367b3af45df2ea7eeca7fbccceab9c35079968f4b3652194be

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir "semgrep==${SEMGREP_VERSION}"
RUN curl -fsSL "https://github.com/aquasecurity/trivy/releases/download/v${TRIVY_VERSION}/trivy_${TRIVY_VERSION}_Linux-64bit.tar.gz" \
    -o /tmp/trivy.tar.gz \
    && echo "${TRIVY_SHA256}  /tmp/trivy.tar.gz" | sha256sum -c - \
    && tar -xzf /tmp/trivy.tar.gz -C /usr/local/bin trivy \
    && rm /tmp/trivy.tar.gz
RUN curl -fsSL "https://github.com/google/osv-scanner/releases/download/v${OSV_VERSION}/osv-scanner_linux_amd64" \
    -o /usr/local/bin/osv-scanner \
    && echo "${OSV_SHA256}  /usr/local/bin/osv-scanner" | sha256sum -c - \
    && chmod +x /usr/local/bin/osv-scanner

COPY . /opt/atak-plugin-preflight
WORKDIR /workspace
ENTRYPOINT ["python3", "/opt/atak-plugin-preflight/preflight.py"]
