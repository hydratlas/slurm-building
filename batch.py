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
  sources_dir_path = pathlib.Path("sources")
  sources_dir_path.mkdir(parents=True, exist_ok=True) # sourcesディレクトリーを作成
  for ver in slurm_versions:
    # ダウンロード
    download_file_path = sources_dir_path.joinpath(pathlib.Path(f"slurm-{ver['version']}.tar.bz2"))
    download(ver['url'], download_file_path)

    # 展開
    extract_dir_path = sources_dir_path.joinpath(pathlib.Path(f"slurm-{ver['version']}"))
    extract_dir_path.mkdir(parents=True, exist_ok=True)
    extract(download_file_path, extract_dir_path)

    ver['dir_path'] = extract_dir_path

  # Slurmをビルド
  binarys_dir_path = pathlib.Path("binarys")
  binarys_dir_path.mkdir(parents=True, exist_ok=True) # binaryディレクトリーを作成
  for env in environments:
    base_name = env['name']
    base_tag = env['tag']
    docker_image_name = env['docker_image_name']

    environment_dir_path = binarys_dir_path.joinpath(pathlib.Path(f"{base_name}{base_tag}"))
    environment_dir_path.mkdir(parents=True, exist_ok=True) # 各環境用のディレクトリーを作成
    for ver in slurm_versions:
      source_dir_path = ver['dir_path']
      slurm_building(docker_image_name, source_dir_path, environment_dir_path)

def docker_image_building(base_name: str, base_tag: str, image_version: str):
  image_name = f"slurm-building:{image_version}-{base_name}{base_tag}"
  if (check_docker_image_exists(image_name)):
    return image_name
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
  print(f"Docker image build successfully to {image_name}")
  return image_name

def check_docker_image_exists(image_name):
  try:
    # Dockerイメージの確認コマンド
    command = ["docker", "image", "inspect", image_name]
    
    # subprocess.runでコマンドを実行
    result = subprocess.run(command, check=True, capture_output=True, text=True)
    
    # イメージが存在する場合
    return True
  
  except subprocess.CalledProcessError:
    # イメージが存在しない場合
    return False

def download(url: str, download_file_path: pathlib.PurePath):
  try:
    data = urllib.request.urlopen(url).read()
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

def extract(archive_file_path: pathlib.PurePath, extract_dir_path: pathlib.PurePath):
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

def slurm_building(docker_image_name: str, source_dir_path: pathlib.PurePath, binary_dir_path: pathlib.PurePath):
  try:
    command = ["docker", "run", \
        "--rm", \
        "-v", f"{binary_dir_path.resolve()}:/app/binary:rw", \
        "-v", f"{source_dir_path.resolve()}:/app/binary/source:rw", \
        docker_image_name]
    result = subprocess.run(command, check=True, capture_output=True, text=True)
  except subprocess.CalledProcessError as e:
    print("Failed to build Slurm.")
    print("Error:", e.stderr)
    raise
  print(f"Slurm build successfully to {source_dir_path.name} {binary_dir_path.name}")

if __name__ == "__main__":
  main()
