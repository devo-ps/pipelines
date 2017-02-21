FROM python:2.7

# add our user and group first to make sure their IDs get assigned consistently, regardless of whatever dependencies get added
RUN groupadd -r pipelines && useradd -m -r -g pipelines pipelines

# grab gosu for easy step-down from root
ENV GOSU_VERSION 1.7
RUN set -x \
    && wget -O /usr/local/bin/gosu "https://github.com/tianon/gosu/releases/download/$GOSU_VERSION/gosu-$(dpkg --print-architecture)" \
    && wget -O /usr/local/bin/gosu.asc "https://github.com/tianon/gosu/releases/download/$GOSU_VERSION/gosu-$(dpkg --print-architecture).asc" \
    && export GNUPGHOME="$(mktemp -d)" \
    && gpg --keyserver ha.pool.sks-keyservers.net --recv-keys B42F6819007F00F88E364FD4036A9C25BF357DD4 \
    && gpg --batch --verify /usr/local/bin/gosu.asc /usr/local/bin/gosu \
    && rm -r "$GNUPGHOME" /usr/local/bin/gosu.asc \
    && chmod +x /usr/local/bin/gosu \
    && gosu nobody true

# Install pipelines
RUN pip install pipelines

RUN mkdir /workspace && chown pipelines:pipelines /workspace
VOLUME /workspace
WORKDIR /workspace

ENV ADMIN_USER admin
ENV ADMIN_PASS admin
ENV WORKSPACE /workspace

COPY docker-entrypoint.sh /usr/local/bin/
RUN ln -s /usr/local/bin/docker-entrypoint.sh /entrypoint.sh # backwards compat
ENTRYPOINT ["docker-entrypoint.sh"]

EXPOSE 8888

CMD pipelines server --workspace ${WORKSPACE} --username ${ADMIN_USER} --password ${ADMIN_PASS} --host 0.0.0.0
