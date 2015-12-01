#!/usr/bin/env bash
mysql -h 127.0.0.1 --port 3306 -u root -pPassword db_name < mysql_dump.sql