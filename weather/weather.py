
# 导包
from argparse import ArgumentParser

from typing import *
import json
import re
import pandas as pd
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup
import requests
plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号 

cityID = pd.read_csv('./cityID.csv')

def getCityID(cityID):
    def getID(city):
        return cityID[cityID['城市'] == city].values[0][1]
    return getID

getID = getCityID(cityID)

areaType = 2

queryURL = 'https://tianqi.2345.com/Pc/GetHistory?'

headers = {
   'User-Agent': r'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36'
}

class WeatherApi:
    def __init__(self, cityID, startDay: Tuple[str, str, str], endDay: Tuple[str, str, str], areaType = 2):
        self.cityID = cityID
        self.Year = startDay[0]
        self.Month = startDay[1]
        self.Day = startDay[2]

        self.endYear = endDay[0]
        self.endMonth = endDay[1]
        self.endDay = endDay[2]
        
        self.areaType = areaType

        self.prefix = queryURL
    def parse(self):
        queryParam = {
            'areaInfo%5BareaId%5D': self.cityID,
            'areaInfo%5BareaType%5D': self.areaType,
            'date%5Byear%5D': self.Year,
            'date%5Bmonth%5D': self.Month
        }
        queryStr = self.prefix

        length = len(queryParam)
        for i, (key, value) in enumerate(queryParam.items()):
            queryStr += key + '=' + str(value)
            queryStr += '&' if i != length - 1 else ''
        return queryStr
    
    def __call__(self):
        # 没次call一次就返回一个新url
        # 由于url只需要年月数据，这里自增天
        
        isLeapYear = False

        if self.Year % 4 == 0 and self.Year % 100 != 0 or self.Year % 400 == 0:
            isLeapYear = True

        if self.Year <= self.endYear:
            if self.Month <= self.endMonth:
                if self.Day <= self.endDay:
                    self.Day += 1
                    if self.Month == 2:
                        if isLeapYear:
                            if self.Day > 28:
                                self.Day = 1
                                self.Month += 1
                        else:
                            if self.Day > 29:
                                self.Day = 1
                                self.Month += 1

                    return self.parse()
                else:
                    self.Day = 1
                    self.Month += 1
                    if self.Month > 12:
                        self.Month = 1
                        self.Year += 1
                    return self.parse()
            else:
                self.Month = 1
                self.Year += 1
                return self.parse()

def jsonData(ans):
    return json.loads(ans)['data']


ulPattern = re.compile(r'<ul class="history-msg">(.*)</ul>', re.S)


avgHighTemperature = re.compile('<li>平均高温：<em class="orange-txt">(-{0,1}\d{1,4})°</em>', re.S)
avgLowTemperature = re.compile(';平均低温：<em class="blue-txt">(-{0,1}\d{1,4})°</em>', re.S)
abnormalHighTemperature = re.compile('<li>极端高温：<em class="orange-txt">(-{0,1}\d{1,4})°</em>', re.S)
abnormalLowTemperature = re.compile('<li>极端低温：<em class="blue-txt">(-{0,1}\d{1,4})°</em><b>', re.S)
avgAirQualityCoefficient = re.compile('<li>平均空气质量指数：<em class="blod-txt">(-{0,1}\d{1,4})</em>', re.S)
bestAirQualityCoefficient = re.compile('<li>空气最好：<em class="green-txt">(\d{1,4}) {0,1}[\u4e00-\u9fa5]{0,10}</em>', re.S)
lowAirQualityCoefficient = re.compile('<li>空气最差：<em class="yellow-txt">(\d{1,4}) {0,1}[\u4e00-\u9fa5]{0,10}</em>', re.S)


avgData = [avgHighTemperature, avgLowTemperature, abnormalHighTemperature, 
abnormalLowTemperature, avgAirQualityCoefficient, bestAirQualityCoefficient, 
lowAirQualityCoefficient]

tablePattern = re.compile(r'<table class="history-table" width="100%">(.*)</table>', re.S)
trPattern = re.compile(r'<tr>(.*)</tr>', re.S)
tdPattern = re.compile(r'<td>(.*)</td>', re.S)


# 获取月平均数据

def getMonthAvgData(data, parseRePattern):
    monthAvgData = []
    for pattern in parseRePattern:
        monthAvgData.extend(pattern.findall(data))
    return list(map(lambda x: int(x), monthAvgData))

def getMonthData(data, tablePattern, from2To: Union[None, Tuple[int, int]] = None):
    html = BeautifulSoup(re.findall(tablePattern, data)[0], 'html.parser')
    
    # 表头
    th = html.find_all('th')
    th = list(map(lambda x: x.text, th))
    
    # 表数据

    content = []
    for i, tr in enumerate(html.find_all('tr')):
        if i == 0:
            continue
        # print(from2To)
        if from2To is not None:
            if i >= from2To[0] and i <= from2To[1]:
                content.append(list(map(lambda x: x.text, tr.find_all('td'))))
            else:
                continue
        else:
            content.append(list(map(lambda x: x.text, tr.find_all('td'))))

    return th, content

def getWeatherData(cityID, start: Tuple[int, int, int], end: Tuple[int, int, int]):
    # 分两个阶段
    # [2017, 1, 18] -> [2022, 3, 30]
    # 爬取 2017年1月数据, 从18号往后爬取
    # 建立循环从2月开始往后，一个月一爬
    # 爬取2022 年3月数据，从1号往后爬取
    start = list(start)
    end = list(end)
    print('正在爬取，请稍等 ...')

    data = []
    # head
    weatherapi = WeatherApi(getID(cityID), start, end)
    headUrl = weatherapi.parse()
    # print(headUrl)
    getData = requests.get(headUrl, headers=headers).text # 获取文本信息

    if start[1] == end[1]:
        header, content = getMonthData(jsonData(getData), tablePattern, (start[2], end[2])) 
    else:
        header, content = getMonthData(jsonData(getData), tablePattern, (start[2], 31)) # 从这一天往月末取
    data.extend(content) # 添加进来

    start[1] += 1
    
    # 循环爬取
    startMonth = [start[0], start[1], 0]
    endMonth = [end[0], end[1], 32]

    while (startMonth[1] < endMonth[1] or startMonth[0] < endMonth[0]):
        # print(startMonth, endMonth)
        if startMonth[1] > 12:
            startMonth[1] = 1
            startMonth[0] += 1
        weatherapi = WeatherApi(getID(cityID), startMonth, endMonth)
        headUrl = weatherapi.parse()
        # print(headUrl)
        getData = requests.get(headUrl, headers=headers).text
        header, content = getMonthData(jsonData(getData), tablePattern, (1, 31))
        data.extend(content)
        startMonth[1] += 1
    
    # 表尾
    # print(startMonth, endMonth)
    if (startMonth[1] <= endMonth[1]):
        weatherapi = WeatherApi(getID(cityID), end, end)
        headUrl = weatherapi.parse()
        getData = requests.get(headUrl, headers=headers).text
        header, content = getMonthData(jsonData(getData), tablePattern, (1, end[2]))
        data.extend(content)

    print('爬取完成, 正在转换 ...')
    return header, data

def getDataFrame(data, header):
    dataframe = pd.DataFrame(data, columns=header)   
    dataframe.iloc[:, 0] = pd.to_datetime(dataframe.iloc[:, 0].map(lambda x: x.split(' ')[0]), format='%Y-%m-%d')
    dataframe.iloc[:, 1] = dataframe.iloc[:, 1].map(lambda x : int(x[:-1]))
    dataframe.iloc[:, 2] = dataframe.iloc[:, 2].map(lambda x : int(x[:-1]))
    dataframe.iloc[:, -1] = dataframe.iloc[:, -1].map(lambda x : int(x.split(' ')[0]))
    print('转换完成')
    return dataframe


############################################# 解析参数 ######################################
parser = ArgumentParser()

parser.add_argument('-c', '--city', type=str, help='city name')
parser.add_argument('-s', '--start', type=str, help='start date, like 2017-01-18')
parser.add_argument('-e', '--end', type=str, help='end date, like 2017-01-18')
parser.add_argument('-o', '--output', type=str, help='output file, like=weather.csv')

args = parser.parse_args()

cityName = args.city
startDate = list(map(lambda x: int(x), args.start.split('-')))
endDate = list(map(lambda x: int(x), args.end.split('-')))
outputFile = args.output


header, data = getWeatherData(cityName, startDate, endDate)

dataframe = getDataFrame(data, header)

dataframe.to_csv(outputFile, index=False)
print(f'存储完毕, 文件名为{outputFile}')


