import glob
import os
import time
from os import getenv
from pathlib import Path
import boto3
from homeassistant_api import Client
from botocore.config import Config
from progress_percentage import ProgressPercentage

def sanitize_dir_path(path):
    return path + ("/" if not path.endswith("/") else "")

def get_s3_client():
    if ((AWS_ACCESS_KEY := getenv("AWS_ACCESS_KEY")) is None):
        raise EnvironmentError("No AWS_ACCESS_KEY env variable")
    if ((AWS_ACCESS_SECRET := getenv("AWS_ACCESS_SECRET")) is None):
        raise EnvironmentError("No AWS_ACCESS_SECRET env variable")
    if ((S3_REGION := getenv("S3_REGION")) is None):
        raise EnvironmentError("No S3_REGION env variable")

    config = Config(region_name=S3_REGION)
    
    boto = None
    try:
        boto = boto3.client("s3", aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_ACCESS_SECRET, config=config)
        print("Connected to AWS")
    except:
        print("Connection to AWS failed")
        quit()
    return boto

def get_ha_client():
    if ((HA_URL := getenv("HA_URL")) is None):
        raise EnvironmentError("No HA_URL env variable")
    HA_URL = HA_URL + ("api" if HA_URL.endswith("/") else "/api")
    if ((HA_TOKEN := getenv("HA_TOKEN")) is None):
        raise EnvironmentError("No HA_TOKEN env variable")

    ha = None
    try:
        ha = Client(HA_URL, HA_TOKEN)
        assert ha.check_api_running()
        print(f"Connected to HA API at {HA_URL}")
    except:
        print(f"Connection to HA API at {HA_URL} failed")
        quit()
    return ha

def create_backup(backup_dir, ha_client):
    if (not ha_client.check_api_running()):
        print("HA API is not running, cannot create backup")
        quit()
    
    pre_backup_files = glob.glob(backup_dir + "*.tar")
    #Do backup here
    print("Triggering new backup in HA")
    #ha_client.trigger_service("backup", "create")
    post_backup_files = glob.glob(backup_dir + "*.tar")

    backup_files = []
    for backup_file in post_backup_files:
        if backup_file in pre_backup_files:
            continue
        backup_files.append(backup_file)
    if (len(backup_files) == 0):
        print("Backup creation was triggered but no backup file was found")
        quit()
    return backup_files

def get_filename(path: Path | str) -> str:
    if isinstance(path, (Path)):
        return f"{path.stem}{path.suffix}"
    else:
        return path.replace("\\", "/").split("/")[-1]

def rename_upload_remove_backup(s3_client, filename):
    if ((S3_BUCKET_NAME := getenv("S3_BUCKET_NAME")) is None):
        raise EnvironmentError("No S3_BUCKET_NAME env variable")
    if ((S3_PATH_PREFIX := getenv("S3_PATH_PREFIX")) is None):
        S3_PATH_PREFIX = ""
    else:
        S3_PATH_PREFIX = sanitize_dir_path(S3_PATH_PREFIX)

    file_path = Path(filename)
    timestr = time.strftime("%Y%m%d-%H%M%S")

    print(f"Found backup {get_filename(file_path)}, renaming")
    file_path = file_path.rename(file_path.with_stem(timestr))
    print(f"New name is {get_filename(file_path)}")

    print("Uploading:")
    s3_path = os.path.join(S3_PATH_PREFIX, get_filename(file_path))
    s3_client.upload_file(file_path.resolve(), S3_BUCKET_NAME, s3_path)
    print("")
    print(f"Removing backup from local disk")
    os.remove(file_path.resolve())

def run():
    print("Starting backup process")
    if ((LOCAL_BACKUPS_PATH := getenv("LOCAL_BACKUPS_PATH")) is None):
        raise EnvironmentError("No LOCAL_BACKUPS_PATH env variable")
    LOCAL_BACKUPS_PATH = sanitize_dir_path(LOCAL_BACKUPS_PATH)
    if(not os.path.exists(LOCAL_BACKUPS_PATH)):
            print(f"{LOCAL_BACKUPS_PATH} does not exist")
            quit()
    
    s3 = get_s3_client()
    ha = get_ha_client()
    files = create_backup(LOCAL_BACKUPS_PATH, ha)
    
    for backup_file in files:
        rename_upload_remove_backup(s3, backup_file)
    
    print("Backup process done")

run()
