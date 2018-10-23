# -*- coding: utf-8 -*-
 
#################################################################
#
# Web Server Backup and Upload to Google Drive
#
# Author: itfromzero.com
#
#################################################################
import os
from datetime import datetime
import logging, logging.handlers
import time
 
#Logging
def setup_custom_logger(name):
    formatter = logging.Formatter(fmt='%(asctime)s %(levelname)-2s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    handler = logging.handlers.RotatingFileHandler("/home/backup/backup.log", maxBytes=900000, backupCount=15)
    handler.setFormatter(formatter)
    screen_handler = logging.StreamHandler()
    screen_handler.setFormatter(formatter)
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    logger.addHandler(screen_handler)
    return logger
 
 
logger = setup_custom_logger('myapp')
MYSQL_LIST=['db1','db2'] #MYSQL Database
DB_NUM = len(MYSQL_LIST)
WEB_LIST=['a','b','c'] #WEB Folder name
WEB_NUM= len(WEB_LIST)
MYSQL_USER='' #MYSQL user
MYSQL_PW='' #MYSQL Password
GDRIVE_FOLDER='BACKUP_WEB'
 
logger.info('Web Server Backup Script')
 
#Create Backup Folder
logger.info('Create Backup Folder')
cmd = "mkdir -p /home/backup/`date +%Y%m%d`"
os.system(cmd)
 
logger.info('Database Backup')
for i in range(0,DB_NUM):
	cmd = "mysqldump -u "+MYSQL_USER+" -p"+MYSQL_PW+" "+MYSQL_LIST[i]+"  | gzip > /home/backup/`date +%Y%m%d`/"+MYSQL_LIST[i]+"-`date +%Y%m%d-%H-%M-%S`.sql.gz"
	os.system(cmd)
	logger.info('Backup database: %s Complete',MYSQL_LIST[i])
 
logger.info('Web Source Backup')
for j in range(0,WEB_NUM):
	cmd = "zip -r /home/backup/`date +%Y%m%d`/"+WEB_LIST[j]+".zip /home/www/"+WEB_LIST[j]+" -q -x /home/www/"+WEB_LIST[j]+"/wp-content/cache/**\*"
	os.system(cmd)
	logger.info('Backup Web Source: %s Complete',WEB_LIST[j])
 
logger.info('Web Server Config Backup')
cmd = "cp -r /etc/nginx/conf.d/ /home/backup/`date +%Y%m%d`/nginx/"
os.system(cmd)
logger.info('Backup Web Server Config Complete')
 
logger.info('Start Upload To Google Drive')
cmd = 'rclone move /home/backup/`date +%Y%m%d` "upload_google_drive:'+GDRIVE_FOLDER+'/`date +%Y%m%d`" >> /var/log/rclone.log 2>&1'
os.system(cmd)
logger.info('Upload Complete')
 
logger.info('Delete Backup File')
 
cmd = "rm -rf /home/backup/`date +%Y%m%d`"
os.system(cmd)
logger.info('Delete Complete')
 
logger.info("Remove all backups older than 3 days")
cmd = 'rclone -q --min-age 3d delete "upload_google_drive:'+GDRIVE_FOLDER+'"'
os.system(cmd) 
logger.info("Remove all empty folders older than 3 days")
cmd = 'rclone -q --min-age 3d rmdirs "upload_google_drive:'+GDRIVE_FOLDER+'"'
os.system(cmd) 
logger.info("Cleanup Trash")
cmd = 'rclone cleanup "upload_google_drive:"'
os.system(cmd)
logger.info("Finish Backup and Upload to Google Drive")
