from argparse import ArgumentParser
from datetime import date, datetime
import pandas as pd
import json
import re
from typing import Tuple

# 网络请求
import requests
import time
from urllib.parse import urlencode

import warnings
warnings.filterwarnings("ignore")

url = "https://data.stats.gov.cn/easyquery.htm"

stringParams = {
    "m": "QueryData",
    "dbcode": "fsnd",
    "rowcode": "zb",
    "colcode": "sj",
    "wds": "[{\"wdcode\":\"reg\",\"valuecode\":\"430000\"}]", 
    "dfwds": "[{\"wdcode\":\"zb\",\"valuecode\":\"A0202\"},{\"wdcode\":\"sj\",\"valuecode\":\"LAST50\"}]",
    # wds 和 dfwds 是爬取过程中相当重要的两个参数
    "k1": int(time.time()),
    "h": 1,
}

provinceData = pd.read_csv('./province.csv')

def getReg(province):
    reg = provinceData[provinceData['province'] == province].values[0][1]
    return reg



def parseData(data):
    totalData = {}
    for i, el in enumerate(data):
        currDataCode = el['code'].split('.')
        zbName = currDataCode[1]
        if zbName not in totalData:
            totalData[zbName] = {}
        totalData[zbName][currDataCode[-1]] = el['data']['data']
    return totalData


def parseJsonData(data):
    data = json.loads(data)
    data = data['returndata']['datanodes']
    return parseData(data)


def query(reg, zb, sj, dbcode):
    stringParams['dbcode'] = dbcode
    if reg != None:
        reg = str(getReg(reg))
        stringParams['wds'] = "[{\"wdcode\":\"reg\",\"valuecode\":\"" + reg + "\"}]"
    else:
        stringParams['wds'] = "[]"
    stringParams['dfwds'] = "[{\"wdcode\":\"zb\",\"valuecode\":\"" + zb + "\"},{\"wdcode\":\"sj\",\"valuecode\":\"" + sj + "\"}]"
    reqUrl = url + "?" +  urlencode(stringParams)
    text = requests.get(reqUrl, verify=False).text
    return parseJsonData(text)


parser = ArgumentParser()


zbExplain = '''
打开国家统计局官网(https://data.stats.gov.cn/easyquery.htm)
在左边的列选择你要查询的数据，往下点，直到找到你需要的指标，
依据点击路线，可以如此命名 Axxyyzz
其中A为默认头部，xx表示第一层索引（从1开始，如1为01, 超过10之后开始以字母为序如10 换成 0A, 11换成0B）
，yy为第二层，zz为第三层，以此类推
'''

sjExplain = '''
时间查询支持4中模式：
1. LASTxx： 最近xx行数据
2. 2005-2021： 查询2005年到2021年的数据,以年为单位
3. 2010A-2022B: 查询2010年第一季度到2022年第二季度的数据，以季度为单位
4. 201001-202112: 查询2010年1月到2021年12月的数据，以月为单位
'''

parser.add_argument('--zb', type=str, help=zbExplain)
parser.add_argument('--reg', type=str, default=None, help='指定地区, 比方说: 湖北省, 北京市')
parser.add_argument('--sj', type=str, help=sjExplain)
parser.add_argument('--dbcode', type=str, help='指定数据源, 比方说: 全国年度(hgnd)，全国季度(hgjd)，全国月度(hgyd), 分省年度(fsnd), 分省季度(fsjd), 分省月度(fsyd)')
parser.add_argument('--output', type=str, default='./data.csv', help='输出文件路径')

zb = parser.parse_args().zb
reg = parser.parse_args().reg
sj = parser.parse_args().sj

dbcode = parser.parse_args().dbcode

data = pd.DataFrame()

if (re.match(r'^LAST\d+$', sj)):
    # print('这里', sj)
    data = pd.DataFrame(query(reg, zb, sj, dbcode))
    sj = sj
elif (re.match(r'^\d{4}-\d{4}$', sj)):
    now = int(datetime.now().strftime('%Y'))
    [start, end] = sj.split('-')
    start = int(start)
    end = int(end)
    sj = 'LAST' + str(now - start)
    # print(sj)
    data = pd.DataFrame(query(reg, zb, sj, dbcode))[now - end - 1:]
elif (re.match(r'^\d{4}.{1}-\d{4}.{1}$', sj)):
    [startStr, endStr] = sj.split('-')
    start = int(startStr[:4]) 
    end = int(endStr[:4]) 

    startSeason = startStr[4:]
    endSeason = endStr[4:]

    now = int(datetime.now().strftime('%Y')) 
    
    # 确定当前季度
    month = int(datetime.now().strftime('%m')) // 3
    if month >= 1 and month <= 3:
        month = 'A'
    elif month >= 4 and month <= 6:
        month = 'B'
    elif month >= 7 and month <= 9:
        month = 'C'
    elif month >= 10 and month <= 12:
        month = 'D'

    def exchange(s):
        if s == 'A':
            return 1
        elif s == 'B':
            return 2
        elif s == 'C':
            return 3
        elif s == 'D':
            return 4

    def getDist(start:Tuple[int, int], end:Tuple[int, int]):
        # 2007A - 2017C = 10 * 4 + A - 1 - 4 + C
        return (end[0] - start[0] + 1) * 4 + start[1] - 1 - 4 + end[1]
    
    sj = 'LAST' + str(getDist((start, exchange(startSeason)), (now, exchange(month))))
    # print(sj, now, month)

    dbcode = dbcode.replace('nd', 'jd')
    # sj = 'LAST' + str(now - start)
    data = pd.DataFrame(query(reg, zb, sj, dbcode))[getDist((end, exchange(endSeason)), (now, exchange(month))) - 1:]


elif (re.match(r'^\d{6}-\d{6}$', sj)):
    [startTime, endTime] = sj.split('-')
    start = int(startTime[:4])
    startMonth = int(startTime[4:])
    end = int(endTime[:4])
    endMonth = int(endTime[4:])
    now = int(datetime.now().strftime('%Y'))
    nowMonth = int(datetime.now().strftime('%m'))
    

    # 20070x - 20170y = 10 * 12 - x + y - 12
    def getMonth(start: Tuple[int, int], end: Tuple[int, int]):
        return (end[0] - start[0] + 1) * 12 - start[1] + end[1] - 12 - 1
    
    sj = 'LAST' + str(getMonth((start, startMonth), (now, nowMonth)))
    dbcode = dbcode[:2] + 'yd'
    data = pd.DataFrame(query(reg, zb, sj, dbcode))[getMonth((end, endMonth), (now, nowMonth)) - 1:]


data.to_csv(parser.parse_args().output)
