#!/usr/bin/env python3
import json
import subprocess
import urllib.request
import pathlib
import tarfile

def main():
  # JSONファイルを読み込み
  with open('batch.json', 'r') as file:
    data = json.load(file)
  environments = data['environments']
  slurm_versions = data['slurm_versions']

  # Dockerイメージをビルド
  docker_image_version = '0.1'
  for env in environments:
    docker_image_name = docker_image_building(env['name'], env['tag'], docker_image_version)
    env['docker_image_name'] = docker_image_name

  # Slurmのソースコードをダウンロード・展開
  for ver in slurm_versions:
    download_file_path = download_source(ver['version'], ver['url'])
    extract_source(download_file_path, ver['version'])

  # Slurmをビルド
  for env in environments:
    base_name = env['name']
    base_tag = env['tag']
    docker_image_name = env['docker_image_name']

    # 各環境用のディレクトリーを作成
    environment_dir = pathlib.Path(f"{base_name}{base_tag}").resolve()
    environment_dir.mkdir(parents=True, exist_ok=True)
    for ver in slurm_versions:
      slurm_version = ver['version']

      # 各環境用のディレクトリーから、make.shへのシンボリックリンクを作成
      link_path = pathlib.Path(f"{base_name}{base_tag}/make.sh")
      target_path = pathlib.Path(f"files/make.sh")
      link_path.symlink_to(target_path)

      # 各環境用のディレクトリーから、ソースコードへのシンボリックリンクを作成
      link_path = pathlib.Path(f"{base_name}{base_tag}/slurm-{slurm_version}")
      target_path = pathlib.Path(f"files/slurm-{slurm_version}")
      link_path.symlink_to(target_path)

      # ビルド
      slurm_building(docker_image_name, environment_dir, f"slurm-{slurm_version}")

def docker_image_building(base_name: str, base_tag: str, image_version: str):
  image_name = f"slurm-building:{image_version}-{base_name}{base_tag}"
  try:
    command = ["docker", "build", \
      "--tag", image_name, \
      "--build-arg", f"BASE_NAME={base_name}", \
      "--build-arg", f"BASE_TAG={base_tag}", \
      "."]
    result = subprocess.run(command, check=True, capture_output=True, text=True)
  except subprocess.CalledProcessError as e:
    print("Failed to build Docker image.")
    print("Error:", e.stderr)
    raise
  print(f"Docker image built successfully to {image_name}")
  return image_name

def download_source(slurm_version: str, slurm_url: str):
  download_file_path = pathlib.Path(f"files/slurm-{slurm_version}.tar.bz2").resolve()
  try:
    data = urllib.request.urlopen(slurm_url).read()
    with download_file_path.open("wb") as f:
        f.write(data)
  except urllib.error.HTTPError as e:
      print(f"HTTP error occurred: {e.code} - {e.reason}")
      raise
  except urllib.error.URLError as e:
      print(f"URL error occurred: {e.reason}")
      raise
  except Exception as e:
      print(f"An error occurred: {e}")
      raise
  print(f"File downloaded successfully and saved to {download_file_path.name}")
  return download_file_path

def extract_source(archive_file_path: pathlib.PurePath, slurm_version: str):
  extract_dir_path = archive_file_path.joinpath(pathlib.Path(f"../slurm-{slurm_version}")).resolve()
  extract_dir_path.mkdir(parents=True, exist_ok=True)
  with tarfile.open(archive_file_path, "r:bz2") as tar:
    # 各メンバーを1階層スキップして展開
    for member in tar.getmembers():
      # 最初のディレクトリ階層を削除する
      member_path = pathlib.Path(*pathlib.Path(member.name).parts[1:])
      
      # 削除したパスで、展開先パスを再設定
      member.name = str(member_path)
      
      # ディレクトリに展開
      tar.extract(member, path=extract_dir_path)
  print(f"Extracted {archive_file_path.name} to {extract_dir_path.name} with 1 component stripped.")

def slurm_building(docker_image_name: str, bind_directory: pathlib.PurePath, source_directory: str):
  try:
    result = subprocess.run(
      ["docker", "run", \
        "--rm", \
        "-v", f"{bind_directory}:/app:rw", \
        "--env", f"DIR=\"{source_directory}\"", \
        docker_image_name],
      check=True,
      capture_output=True,
      text=True
      )
  except subprocess.CalledProcessError as e:
    print("Failed to build Slurm.")
    print("Error:", e.stderr)
    raise

if __name__ == "__main__":
  main()
