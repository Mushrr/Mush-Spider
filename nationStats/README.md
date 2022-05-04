#### 国家统计局数据爬虫

##### 食用方法

```python
usage: nationStatisticdata.py [-h] [--zb ZB] [--reg REG] [--sj SJ] [--dbcode DBCODE] [--output OUTPUT]

optional arguments:
  -h, --help       show this help message and exit
  --zb ZB          打开国家统计局官网(https://data.stats.gov.cn/easyquery.htm) 在左边的列选择你要查询的数据，往下点，直 到找到你需要的指标， 依据点击路线，可以如此命名
                   Axxyyzz 其中A为默认头部，xx表示第一层索引（从1开始，如1为01, 超过10之后开始以字母为序如10 换成 0A, 11换成0B） ，yy为第二层，zz为第三层，以此类推
  --reg REG        指定地区, 比方说: 湖北省, 北京市
  --sj SJ          时间查询支持4中模式： 1. LASTxx： 最近xx行数据 2. 2005-2021： 查询2005年到2021年的数据,以年为单位 3. 2010A-2022B:
                   查询2010年第一季度到2022年第二季度的数据，以季度为单位 4. 201001-202112: 查询2010年1月到2021年12月的 数据，以月为单位
  --dbcode DBCODE  指定数据源, 比方说: 全国年度(hgnd)，全国季度(hgjd)，全国月度(hgyd), 分省年度(fsnd), 分省季度(fsjd),  分省月度(fsyd)
  --output OUTPUT  输出文件路径
```

```python
python nationStatisticdata.py --zb A1401 --reg 湖北省 --sj LAST100 --dbcode fsyd --output 湖北省房地产开发情况.csv
```

![爬取到的数据](https://github.com/HuangXingjie2002/Mush-Spider/blob/main/nationStats/README.assets/image-20220504212303917.png)

![国家统计局公布的数据](https://github.com/HuangXingjie2002/Mush-Spider/blob/main/nationStats/README.assets/image-20220504212337165.png)



###### `zb`（指标如何确定）？

1. 打开国家统计局官网的[查询数据页面](https://data.stats.gov.cn/easyquery.htm), 选择你要查询的类型

![image-20220504212607970](https://github.com/HuangXingjie2002/Mush-Spider/blob/main/nationStats/README.assets/image-20220504212607970.png)

2. 点击确认之后，可以在左侧观察得到非常多的类别（**我这里选择分省年度数据**）

![image-20220504212731358](https://github.com/HuangXingjie2002/Mush-Spider/blob/main/nationStats/README.assets/image-20220504212731358.png)

3. 确认一个指标，我这里选择人口下的人口出生率、死亡率和自然增长率

![image-20220504212914819](https://github.com/HuangXingjie2002/Mush-Spider/blob/main/nationStats/README.assets/image-20220504212914819.png)

国家统计局官网按照如上层级关系命名指标。即`AXXYYZZ`其中第一层XX可以突破10，第二三层不可以突破10，如果超过10 就需要按字母序来重新编写即， `A131011` 应该改成  `A130A0B`

在这个例子中数据`人口出生率、死亡率和自然增长率`为`A0302`，如果您还是觉得不保险，可以在打开`F12`，直接查看请求。

![image-20220504213216914](https://github.com/HuangXingjie2002/Mush-Spider/blob/main/nationStats/README.assets/image-20220504213216914.png)

所以没错。

4. 执行`python`，抓取数据。

```python
python nationStatisticdata.py --zb A0302 --reg 湖北省 --sj LAST100 --dbcode fsnd --output 湖北省人口出生死亡自然增长.csv
```

![image-20220504213559350](https://github.com/HuangXingjie2002/Mush-Spider/blob/main/nationStats/README.assets/image-20220504213559350.png)

![image-20220504213528507](https://github.com/HuangXingjie2002/Mush-Spider/blob/main/nationStats/README.assets/image-20220504213528507.png)

