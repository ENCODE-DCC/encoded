FROM node:12-bullseye-slim
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install --no-install-recommends \
        locales build-essential git curl sudo python3-dev python3-venv python3-pip ca-certificates \
        default-jdk libpq-dev postgresql postgresql-client graphviz libmagic-dev ruby-dev ruby-rubygems nginx-light redis python2 \
        libjpeg-dev libtiff-dev libwebp-dev liblcms2-dev \
    && rm -rf /var/lib/apt/lists/* \
    && localedef -i en_US -c -f UTF-8 -A /usr/share/locale/locale.alias en_US.UTF-8 \
    && curl -O https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-5.6.16.deb \
    && dpkg -i elasticsearch-5.6.16.deb \
    && rm elasticsearch-5.6.16.deb \
    && gem install compass \
    && useradd -ms /bin/bash --groups sudo encoded \
    && echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers \
    && mkdir /app \
    && chown encoded /app \
    # Workaround for https://bugs.launchpad.net/ubuntu/+source/nginx/+bug/1899164
    && chown -R encoded /var/log/nginx /var/lib/nginx

WORKDIR /app
USER encoded
ENV LANG en_US.utf8
ENV PATH=/app/venv/bin:/usr/share/elasticsearch/bin:/usr/lib/postgresql/13/bin:${PATH}

COPY --chown=encoded requirements.txt ./
RUN python3 -m venv venv \
    && venv/bin/pip --disable-pip-version-check --no-cache-dir install -r requirements.txt
COPY --chown=encoded package.json package-lock.json ./
COPY --chown=encoded node_shims ./node_shims/
RUN npm ci

