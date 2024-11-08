ARG BASE_NAME="ubuntu" \
    BASE_TAG="24.04"
FROM ${BASE_NAME}:${BASE_TAG}
WORKDIR /app/binary/source
COPY make.sh /app/make.sh
RUN DEBIAN_FRONTEND=noninteractive apt-get update && apt-get install -y \
      build-essential fakeroot devscripts equivs \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*
ENTRYPOINT ["/bin/bash", "-cx", "/app/make.sh"]
