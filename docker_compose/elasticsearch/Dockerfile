FROM webhippie/elasticsearch:5.6-arm64v8

RUN rm /usr/share/elasticsearch/plugins

RUN mkdir /usr/share/elasticsearch/plugins

RUN mkdir /usr/share/elasticsearch/config

RUN mkdir /usr/share/elasticsearch/scripts

RUN chown -R elastico:elastico /usr/share/elasticsearch

ENTRYPOINT []

CMD ["su-exec", "elastico", "/usr/share/elasticsearch/bin/elasticsearch"]