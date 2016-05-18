#!/usr/bin/python
# -*- coding: utf-8 -*-
# defined by developers, basically settings are for the system
# rarely needed to be modified

import logging
import logging.config

azure_settings = {
	"account": "crowdfile", #容器名
	"key": "LPKAQIkvntlpsZm+EBTB2JfjILpObuRfYzwhmBk31/ILoafSLzwkJaBQDhwcW4rpXks7UGi3+e2+1eCHHCn+SQ==", #容器对应的key值
	"blob_host_base": ".blob.core.chinacloudapi.cn", #blob服务器
	"queue_host_base": ".queue.core.chinacloudapi.cn", #queue服务器
	"queue_name": "auto-cut-queue-%s",
}

mongo_settings = {
	"host": "127.0.0.1",
	"port": "27017",
}

sqlserver_settings = {
	"host": "crowd-db.chinacloudapp.cn",
	"port": "1433",
	"user": "crowd-user",
	"password": "zaixian2013",
	"database": "CrowdDB",
	"charset": "UTF-8",
	"reconnect_cnt": 3,	# limited times to reconnect
	"reconnect_interval": 100,
}

#sqlserver_ip = "113.31.17.46"
#sqlserver_port = "1433"
#sqlserver_user = "sa"
#sqlserver_password = "zaixian2013"
#sqlserver_database = "CrowdDB"
#sqlserver_charset = "UTF-8"

logging.config.fileConfig('logging.conf')
logger = logging.getLogger('root')

from local_settings import *