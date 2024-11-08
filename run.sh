#!/usr/bin/env bash
set -eu

docker_build () {
  local VERSION="$1"
  docker build \
    --tag "slurm-building:0.1-ubuntu$VERSION" \
    --build-arg "BASE_NAME=ubuntu" \
    --build-arg "BASE_TAG=$VERSION" \
    .
}
UBUNTU_VERSION_LIST=("22.04" "24.04")
for UBUNTU_VERSION in "${UBUNTU_VERSION_LIST[@]}"; do
  docker_build "$UBUNTU_VERSION"
done

cd files

get_source () {
  local VERSION="$1"
  wget -O "slurm-$VERSION.tar.bz2" "https://download.schedmd.com/slurm/slurm-$VERSION-latest.tar.bz2" &&
  mkdir -p "slurm-$VERSION" &&
  tar -xa -C "slurm-$VERSION" --strip-components=1 -f "$NAME.tar.bz2"
}
SLURM_VERSION_LIST=("22.05" "23.02" "23.11" "24.05")
for SLURM_VERSION in "${SLURM_VERSION_LIST[@]}"; do
  get_source "$SLURM_VERSION"
done

cd ../

slurm_build () {
  local DIR="$1"
  local UBUNTU_VERSION="$2"
  local SLURM_VERSION="$3"
  docker run \
    --name "slurm-build:0.1-ubuntu$UBUNTU_VERSION" \
    --rm \
    -v "$PWD:/app:rw" \
    --env DIR="slurm-$SLURM_VERSION" \
    slurm-building
}
for UBUNTU_VERSION in "${UBUNTU_VERSION_LIST[@]}"; do
  mkdir "ubuntu$UBUNTU_VERSION"
  ln -s "files/make.sh" "ubuntu$UBUNTU_VERSION/make.sh"
  for SLURM_VERSION in "${SLURM_VERSION_LIST[@]}"; do
    ln -s "files/slurm-$SLURM_VERSION" "ubuntu$UBUNTU_VERSION/slurm-$SLURM_VERSION"
    slurm_build "$PWD/ubuntu$UBUNTU_VERSION/slurm-$SLURM_VERSION" "$UBUNTU_VERSION" "$SLURM_VERSION"
  done
done
