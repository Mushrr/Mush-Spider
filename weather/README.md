#### 食用方法

```python
usage: weather.py [-h] [-c CITY] [-s START] [-e END] [-o OUTPUT]

optional arguments:
  -h, --help            show this help message and exit
  -c CITY, --city CITY  city name
  -s START, --start START
                        start date, like 2017-01-18
  -e END, --end END     end date, like 2017-01-18
  -o OUTPUT, --output OUTPUT
                        output file, like=weather.csv
```

#### 例: 武汉2021-1-1 ~ 2021-10-1 之间所有的天气数据

```python
python weather.py -c 武汉 -s 2021-1-1 -e 2021-10-1 -o 武汉天气数据_日.csv
```

#### 结果

![image-20220502203904057](https://github.com/HuangXingjie2002/Mush-Spider/blob/main/weather/README.assets/image-20220502203904057.png)

#### 解释

`cityID.csv`存储的各个城市的ID，这个ID需要被爬虫使用。
