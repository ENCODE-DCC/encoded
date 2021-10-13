# See here for image contents: https://github.com/microsoft/vscode-dev-containers/blob/v0.195.0/containers/python-3/.devcontainer/base.Dockerfile
# [Choice] Python version (use -bullseye variants on local arm64/Apple Silicon): 3, 3.9, 3.8, 3.7, 3.6, 3-bullseye, 3.9-bullseye, 3.8-bullseye, 3.7-bullseye, 3.6-bullseye, 3-buster, 3.9-buster, 3.8-buster, 3.7-buster, 3.6-buster
ARG VARIANT=3.8-bullseye
FROM mcr.microsoft.com/vscode/devcontainers/python:0-${VARIANT}

# [Choice] Node.js version: none, lts/*, 16, 14, 12, 10
ARG NODE_VERSION="12"
RUN if [ "${NODE_VERSION}" != "none" ]; then su vscode -c "umask 0002 && . /usr/local/share/nvm/nvm.sh && nvm install ${NODE_VERSION} 2>&1"; fi

RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install --no-install-recommends default-jdk libpq-dev postgresql postgresql-client graphviz libmagic-dev ruby-dev ruby-rubygems nginx redis python2 \
    && curl -O https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-5.6.16.deb && dpkg -i elasticsearch-5.6.16.deb && rm elasticsearch-5.6.16.deb

RUN gem install compass

# [Optional] If your pip requirements rarely change, uncomment this section to add them to the image.
COPY requirements.txt /tmp/pip-tmp/
RUN su vscode -c "/usr/local/bin/pip --disable-pip-version-check --no-cache-dir install -r /tmp/pip-tmp/requirements.txt" \
    && rm -rf /tmp/pip-tmp
COPY --chown=vscode package.json package-lock.json /app/
COPY --chown=vscode node_shims /app/node_shims
RUN chown vscode /app && su vscode -c "cd /app && npm ci"
ENV PATH=/app/venv/bin:/usr/share/elasticsearch/bin:/usr/lib/postgresql/13/bin:${PATH}
USER vscode
