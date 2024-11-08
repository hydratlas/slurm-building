ARG BASE_NAME="ubuntu" \
    BASE_TAG="24.04"
ENV DIR source
FROM ${BASE_NAME}:${BASE_TAG}
WORKDIR /app
RUN DEBIAN_FRONTEND=noninteractive apt-get update && apt-get install -y \
      build-essential fakeroot devscripts equivs \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*
ENTRYPOINT ["/bin/bash", "-cx", "/app/make.sh \"${DIR}\""]
