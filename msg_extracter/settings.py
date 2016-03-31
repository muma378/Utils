# -*- coding: utf-8 -*-
import os

PARTITION_NUM = 10

MASTER_URL = "spark://Yang.local:7077"
APP_NAME = "HUAWEI_MSG_CLASSIFIER"
DATABASE_NAME = "msg_classifier.db"


RABBITMQ_USERNAME = "guest"
RABBITMQ_PASSWORD = "guest"
RABBITMQ_HOST = "localhost"

RABBITMQ_CONN_CONF = {
    "host": "localhost",
    "username": "guest",
    "password": "guest",
}

RABBITMQ_SPARK = {
    "exchange": "spark-exchange",
    "queue": "spark-queue",
    "consumer-tag": "spark-consumer",
    "routing-key": "msg-filter",
}

SOURCE_FILE_TEMPLATE = "out_{index}.txt"
ROOT_DIRECTORY = "/Users/imac/Desktop/huawei/"  # TODO:
DATA_DIRECTORY = os.path.join(ROOT_DIRECTORY, u"源数据")
SAVE_DIRECTORY = os.path.join(ROOT_DIRECTORY, u"待处理数据")
TEMP_DIRECTORY = os.path.join(ROOT_DIRECTORY, u"临时文件")
LOG_DIRECTORY = os.path.join(ROOT_DIRECTORY, u"日志")

SYNTAX_RULES = {
	u'地点': ('ns', ),	# classified as location if the sentence had tag 'ns'
	u'日程': ('[tm]', ),	
	u'地点日程': ('ns', 'v'),
	u'导航打车': ('v', 'ns'),
	u'待办': ('[tm]', 'v'),
}

XLSX_HEADERS = {
    u'地点': [['A1:A2',u"语料",80],
            ['B1:B2',u"所有具体地点", 25],
            ['C1:C2',u"所有具体最长地点", 25],
            ['D1:D2',u"所有细化地点", 25],
            ['E1:E2',u"细化地点类型", 25],
            ['F1:F2',u"标注疑惑备注", 25],
        ],
    u'日程': [['A1:A2',u"语料",80],
            ['B1:B2',u"所属方",8],
            ['C1:C2',u"事件",15],
            ['D1:D2',u"开始时间原文",15],
            ['E1:E2',u"结束时间原文",15],
            ['F1:F2',u"参与者",10],
            ['G1:G2',u"发送方接收方名",10],
            ['H1:H2',u"事件发生的地点",20],
            ['I1:I2',u"所有具体地点",20],
            ['J1:J2',u"所有具体地点最长地点",20],
            ['K1:K2',u"所有细化地点",20],
            ['L1:L2',u"细化地点类型",20],
            ['M1:M2',u"标注疑惑备注",20],
        ],
    u'地点日程': [['A1:A2',u"语料",80],
            ['B1:B2',u"所属方",7],
            ['C1:C2',u"事件",16],
            ['D1:D2',u"触发事件的地点",25],
            ['E1:E2',u"状态(到达或离开状态)",24],
            ['F1:F2',u"参与者",20],
            ['G1:G2'u"发送方接收方名",20],
            ['H1:H2',u'事件发生地点',20],
            ['I1:I2',u'所有具体地点',20],
            ['J1:J2',u"所有具体地点最长地点",20],
            ['K1:K2',u'所有细化地点',20],   
            ['L1:L2',u'细化地点类型',20],
            ['M1:M2',u'标注疑惑备注',20],
        ],
    u'导航打车': [['A1:A2',u"语料",80],
            ['B1:B2',u"所属方",7],
            ['C1:C2',u'有意图要去的地点',20],
            ['D1:D2',u'有意图要去的时间',20],
            ['E1:E2',u'所有具体地点',20],   
            ['F1:F2',u'所有细化地点',20],
            ['G1:G2',u'细化地点类型',20],
            ['H1:H2',u'标注疑惑备注',25],
        ],
    u'待办': [['A1:A2',u"语料",80],
            ['B1:B2',u"所属方",7],
            ['C1:C2',u"待办事件",16],
            ['D1:D2',u"参与人",20],
            ['E1:F1',u'事件发生地点',40],
            ['E2:E2',u'地点',15],
            ['F2:F2',u'地点里包含的具体地点列表',25],   
            ['G1:H1',u'其他地地点',40],
            ['G2:G2',u'地点',15], 
            ['H2:H2',u'地点里包含的具体地点列表',25],
        ],
}