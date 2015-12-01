#!/usr/bin/env bash
mysqldump -h 127.0.0.1 --port 3307 -u root -pPassword db_name `echo "SELECT table_name as '' FROM INFORMATION_SCHEMA.TABLES
WHERE table_schema = 'db_name' AND condition_str;" | mysql -h 127.0.0.1 --port 3307 -uroot -pPassword | sed '/Tables_in/d'` > mysql_dump.sql