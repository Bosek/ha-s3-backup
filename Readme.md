**Required ENV variables:**  

`AWS_ACCESS_KEY`  
`AWS_ACCESS_SECRET`  
`S3_BUCKET_NAME`  
`S3_REGION`  
`S3_PATH_PREFIX` is the path inside S3 bucket  
`HA_URL` is HomeAssistant URL without /api  
`HA_TOKEN`  
`LOCAL_BACKUPS_PATH` is path to local folder with backups(`homeassistant/backups`)  
`CRON_SCHEDULE` [generate here](https://crontab.guru/)  
`HA_BACKUP_DATETIME_ENTITY` is a HomeAssistant entity(`input_datetime`) that will get updated with actual date and time when the backup is done  
  