# slurm-building
Build Slurm for Debian or Ubuntu.

## Install prerequisite packages
```sh
sudo apt-get install -y git bzip2
```
Docker is installed separately.

## Single Buildings
### Build Container
```sh
cd "$HOME" &&
git clone --depth 1 https://github.com/hydratlas/slurm-building.git &&
cd slurm-building &&
docker build \
  --tag slurm-building:0.1-ubuntu24.04 \
  --build-arg BASE_NAME=ubuntu \
  --build-arg BASE_TAG=24.04 \
  .
```

### Building Slurm
run in the `slurm-building` directory.
```sh
mkdir -p sources &&
wget -O sources/slurm-24.05.tar.bz2 https://download.schedmd.com/slurm/slurm-24.05-latest.tar.bz2 &&
mkdir -p sources/slurm-24.05 &&
tar -xa -C sources/slurm-24.05 --strip-components=1 -f sources/slurm-24.05.tar.bz2 &&
mkdir -p binarys/ubuntu24.04 &&
docker run \
  --name slurm-building \
  --rm \
  -v "$PWD/binarys/ubuntu24.04:/app/binary:rw" \
  -v "$PWD/sources/slurm-24.05:/app/binary/source:rw" \
  slurm-building:0.1-ubuntu24.04
```
`.deb` files are generated in the `binarys/ubuntu24.04` directory.

### Debugging Containers
```sh
docker run \
  --name slurm-building \
  --rm \
  -v "$PWD/binarys/ubuntu24.04:/app/binary:rw" \
  -v "$PWD/sources/slurm-24.05:/app/binary/source:rw" \
  -it --entrypoint "bash" \
  slurm-building:0.1-ubuntu24.04
```

## Multiple Buildings
```sh
cd "$HOME" &&
git clone --depth 1 https://github.com/hydratlas/slurm-building.git &&
cd slurm-building &&
./batch.py
```

## Install Slurm
After moving to the directory where the `.deb` file is located, install it with the following command.

`N: Download is performed unsandboxed as root as file '<file>' couldn't be accessed by user '_apt'. - The error message `pkgAcquire::Run (13: Permission denied)` is displayed, but can be ignored.
```sh
sudo apt-get install -y "./slurm-smd_24.05.4-1_amd64.deb"
sudo apt-get install -y "./slurm-smd-client_24.05.4-1_amd64.deb"
sudo apt-get install -y "./slurm-smd-slurmd_24.05.4-1_amd64.deb"
sudo apt-get install -y "./slurm-smd-slurmctld_24.05.4-1_amd64.deb"
sudo apt-get install -y "./slurm-smd-slurmdbd_24.05.4-1_amd64.deb"
sudo apt-get install -y "./slurm-smd-sackd_24.05.4-1_amd64.deb"
```
