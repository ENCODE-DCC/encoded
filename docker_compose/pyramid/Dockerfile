FROM python:3.8.12-buster

ENV PYTHONDONTWRITEBYTECODE 1

ENV PYTHONUNBUFFERED 1

ENV VIRTUAL_ENV=/opt/venv

RUN apt-get update

RUN apt-get install -y make git curl npm

RUN curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash \
  && . ~/.nvm/nvm.sh \
  && nvm install 12.22.7 \
  && nvm use 12.22.7

RUN npm install -g npm@6.14.15

RUN python -m venv $VIRTUAL_ENV

ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN python -m pip install --upgrade pip

WORKDIR /install

COPY package*.json .

COPY node_shims ./node_shims/

RUN npm ci

WORKDIR /encoded

COPY . .

RUN make dockerinstall