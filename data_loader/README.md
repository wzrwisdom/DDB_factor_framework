
数据导入模块下的文件结构以及对应文件的功能简介：
```
│ ├── data_loader
│ │ ├── loader_library
│ │ │ └── CSVDataModule.dos  提供解析路径，导入csv文件到DDB库表，提交导入job等函数
│ │ │ └── ExtractFeatureModule.dos  整合特征提取，创建库表结构，以及提交导入job等函数
│ │ ├── data_load_template
│ │ │ └── loadTrade.dos  指定csv存放的路径，按照日期范围进行导入逐笔成交数据
│ │ │ └── loadEntrust.dos  指定csv存放的路径，按照日期范围进行导入逐笔委托数据
│ │ │ └── loadSnapshot.dos  指定csv存放的路径，按照日期范围进行导入原始3s快照数据
│ │ │ └── createOneMinuteKLineChart.dos  将导入的原始快照数据聚合生成1min的K线数据
│ │ │ └── createFiveMinuteKLineChart.dos  将导入的原始快照数据聚合生成5min的K线数据
======= 特征提取
│ │ │ └── createSnapCrossSec.dos  指定滚动时间窗口的大小，根据原始快照信息统计出新的特征
│ │ │ └── createTradeCrossSec.dos  指定滚动时间窗口的大小，根据逐笔成交统计出新的特征，其中需要结合逐笔委托判断资金规模
│ │ │ └── createEntrustCrossSec.dos  指定滚动时间窗口的大小，根据逐笔委托统计出新的特征
│ │ │ └── createCancelOrderCrossSec.dos  指定滚动时间窗口的大小，结合逐笔委托和逐笔成交中的撤单数据统计出新的特征
```

## 特征提取
利用导入到DDB的原始快照，逐笔成交以及逐笔委托数据，我们按照一定的滚动时间窗口进行特征提取。以000014标的为例，按照6s的频率提取特殊，其输出保存在./output/CROSS_SECTION_6SEC路径下。

关于**createSnapCrossSec.dos**运行的配置如下：
| 参数名称      | 类型  | 取值 | 描述 |
| :------------ | :------------- | :------------- | :------------------- |
| dbName| String  | dfs://CROSS_SECTION_6sec | 输出库名 |
| tbName | String | snap_info | 输出表名 |
| startDate | Date | 2023-04-20 | 处理数据的起始日期 |
| endDate | Date | 2023-04-20 | 处理数据的截止日期 |
| window_size | String | 6s | 滚动时间窗口大小 |
| threadNum | Int | 1 | 线程数目 |
| snapDbName | String | dfs://LEVEL2_Snapshot_ArrayVector | 输入的快照库名 |
| snapTbName | String | SnapRaw | 输入的快照表名 |
| initDb | Boolean | false | 是否覆盖输出库 |
| initTb | Boolean | false | 是否覆盖输出表 |


关于**createTradeCrossSec.dos**运行的配置如下：
| 参数名称      | 类型  | 取值 | 描述 |
| :------------ | :------------- | :------------- | :------------------- |
| dbName| String  | dfs://CROSS_SECTION_6sec | 输出库名 |
| tbName | String | trade_info | 输出表名 |
| startDate | Date | 2023-04-20 | 处理数据的起始日期 |
| endDate | Date | 2023-04-20 | 处理数据的截止日期 |
| window_size | String | 6s | 滚动时间窗口大小 |
| threadNum | Int | 1 | 线程数目 |
| fromDbNameStr | String | {'entrust': 'dfs://LEVEL2_Tick', 'trade': 'dfs://LEVEL2_Tick'} | 输入委托和成交的库名 |
| fromTbNameStr | String | {'entrust': 'OrderRaw', 'trade': 'TradeRaw'} | 输入委托和成交的表名 |
| initDb | Boolean | false | 是否覆盖输出库 |
| initTb | Boolean | false | 是否覆盖输出表 |

关于**createEntrustCrossSec.dos**运行的配置如下：
| 参数名称      | 类型  | 取值 | 描述 |
| :------------ | :------------- | :------------- | :------------------- |
| dbName| String  | dfs://CROSS_SECTION_6sec | 输出库名 |
| tbName | String | entrust_info | 输出表名 |
| startDate | Date | 2023-04-20 | 处理数据的起始日期 |
| endDate | Date | 2023-04-20 | 处理数据的截止日期 |
| window_size | String | 6s | 滚动时间窗口大小 |
| threadNum | Int | 1 | 线程数目 |
| entrustDbName | String | dfs://LEVEL2_Tick | 输入的快照库名 |
| entrustTbName | String | OrderRaw | 输入的快照表名 |
| initDb | Boolean | false | 是否覆盖输出库 |
| initTb | Boolean | false | 是否覆盖输出表 |

关于**createCancelOrderCrossSec.dos**运行的配置如下：
| 参数名称      | 类型  | 取值 | 描述 |
| :------------ | :------------- | :------------- | :------------------- |
| dbName| String  | dfs://CROSS_SECTION_6sec | 输出库名 |
| tbName | String | cancelOrder_info | 输出表名 |
| startDate | Date | 2023-04-20 | 处理数据的起始日期 |
| endDate | Date | 2023-04-20 | 处理数据的截止日期 |
| window_size | String | 6s | 滚动时间窗口大小 |
| threadNum | Int | 1 | 线程数目 |
| fromDbNameStr | String | {'entrust': 'dfs://LEVEL2_Tick', 'trade': 'dfs://LEVEL2_Tick'} | 输入委托和成交的库名 |
| fromTbNameStr | String | {'entrust': 'OrderRaw', 'trade': 'TradeRaw'} | 输入委托和成交的表名 |
| initDb | Boolean | false | 是否覆盖输出库 |
| initTb | Boolean | false | 是否覆盖输出表 |


**createSnapCrossSec.dos**提取出的盘口数据特征如下：
| 特征名      | 特征代码  | 描述 |
| :-------- | :-------- | :--------- | 
| 卖盘最新最优价 | s1 | 滚动窗口内最后三秒卖一价格 |
| 卖盘最新五档价 | s5 | 滚动窗口内最后三秒卖五价格 |
| 卖盘最新十档价 | s10 | 滚动窗口内最后三秒卖十价格 |
| 买盘最新最优价 | b1 | 滚动窗口内最后三秒买一价格 |
| 买盘最新五档价 | b5 | 滚动窗口内最后三秒买五价格 |
| 买盘最新十档价 | b10 | 滚动窗口内最后三秒买十价格 |
| 卖盘所有卖一量之和 | sv1_sum | 滚动窗口内所有三秒盘口的卖一挂单量之和 |
| 卖盘所有卖一至卖五量之和 | sv5_sum | 滚动窗口内所有三秒盘口的$\sum_{i=1}^{5}\text{vol}_i$之和, 其中$\text{vol}_i$代表卖i的挂单量 |
| 卖盘所有卖一至卖十量之和 | sv10_sum | 滚动窗口内所有三秒盘口的$\sum_{i=1}^{10}\text{vol}_i$之和, 其中$\text{vol}_i$代表卖i的挂单量 |
| 买盘所有买一量之和 | bv1_sum | 滚动窗口内所有三秒盘口的买一挂单量之和 |
| 买盘所有买一至买五量之和 | bv5_sum | 滚动窗口内所有三秒盘口的$\sum_{i=1}^{5}\text{vol}_i$之和, 其中$\text{vol}_i$代表买i的挂单量 |
| 买盘所有买一至买十量之和 | bv10_sum | 滚动窗口内所有三秒盘口的$\sum_{i=1}^{10}\text{vol}_i$之和, 其中$\text{vol}_i$代表买i的挂单量 |
| 卖盘所有卖一价量积之和 | ssv1_sum | 滚动窗口内所有三秒盘口的卖一挂单量和卖一价乘积之和 |
| 卖盘所有卖一至卖五价量积之和 | ssv5_sum | 滚动窗口内所有三秒盘口的$\sum_{i=1}^{5}\text{vol}_{i}\times \text{price}_{i}$之和, 其中$\text{vol}_i$代表卖i的挂单量, $\text{price}_i$代表卖i的挂单价|
| 卖盘所有卖一至卖十价量积之和 | ssv10_sum | 滚动窗口内所有三秒盘口的$\sum_{i=1}^{10}\text{vol}_{i}\times \text{price}_{i}$之和, 其中$\text{vol}_i$代表卖i的挂单量, $\text{price}_i$代表卖i的挂单价|
| 买盘所有买一价量积之和 | bbv1_sum | 滚动窗口内所有三秒盘口的买一挂单量和买一价乘积之和 |
| 买盘所有买一至买五价量积之和 | bbv5_sum | 滚动窗口内所有三秒盘口的$\sum_{i=1}^{5}\text{vol}_{i}\times \text{price}_{i}$之和, 其中$\text{vol}_i$代表买i的挂单量, $\text{price}_i$代表买i的挂单价|
| 买盘所有买一至买十价量积之和 | bbv10_sum | 滚动窗口内所有三秒盘口的$\sum_{i=1}^{10}\text{vol}_{i}\times \text{price}_{i}$之和, 其中$\text{vol}_i$代表买i的挂单量, $\text{price}_i$代表买i的挂单价|
| 1档委比 | wb1 | $\frac{滚动窗口内所有三秒盘口的1档买单量 - 滚动窗口内所有三秒盘口的1档卖单量}{滚动窗口内所有三秒盘口的1档买单量 + 滚动窗口内所有三秒盘口的1档卖单量} $ |
| 5档委比 | wb5 | $\frac{滚动窗口内所有三秒盘口的1-5档买单量之和 - 滚动窗口内所有三秒盘口的1-5档卖单量}{滚动窗口内所有三秒盘口的1-5档买单量 + 滚动窗口内所有三秒盘口的1-5档卖单量} $ |
| 10档委比 | wb10 | $\frac{滚动窗口内所有三秒盘口的1-10档买单量之和 - 滚动窗口内所有三秒盘口的1-10档卖单量}{滚动窗口内所有三秒盘口的1-10档买单量 + 滚动窗口内所有三秒盘口的1-10档卖单量} $ |
| 盘口最新均价 | bs_avg_price | 滚动窗口内最后三秒买一和卖一的价格平均 |


**createTradeCrossSec.dos**提取出的盘口数据特征如下：

下表中涉及到资金来源的定义
* 超大单(enormous)：当笔成交对应的委托信息中委托金额 > 100万元
* 大单(large)： 100万元 $\geq$ 委托金额 > 20万元
* 中单(middle)： 20万元 $\geq$ 委托金额 > 4万元
* 小单(small)： 4万元 $\geq$ 委托金额 

| 特征名      | 特征代码  | 描述 |
| :-------- | :-------- | :--------- | 
| 开盘价 | open | 滚动窗口内第一笔成交价 |
| 收盘价 | close | 滚动窗口内最后一笔成交价 |
| 最高价 | high | 滚动窗口内最高的成交价 |
| 最底价 | high | 滚动窗口内最低的成交价 |
| 买单成交笔数 | td_buy_num | 滚动窗口内买单成交笔数 |
| 卖单成交笔数 | td_sell_num | 滚动窗口内卖单成交笔数 |
| 买单成交量 | td_buy_vol | 滚动窗口内买单成交量 |
| 卖单成交量 | td_sell_vol | 滚动窗口内卖单成交量 |
| 买单加权成交价 | td_buy_price | 滚动窗口内买单按照量加权的成交价 |
| 卖单加权成交价 | td_sell_price | 滚动窗口内卖单按照量加权的成交价 |
| 买单成交价标准差 | td_buy_price_std | 滚动窗口内买单成交价的标准差 |
| 卖单成交价标准差 | td_sell_price_std | 滚动窗口内卖单成交价的标准差 |
| 总成交量 | td_vol | 滚动窗口内总的成交量 |
| \${source}买单成交金额 | \${source}_buy_money | \${source}可指代为超大单/大单/中单/小单, 当\${source}为enormous时，表示资金方为超大单的机构在当前滚动窗口内的累积流入金额 |
| \${source}卖单成交金额 | \${source}_sell_money | \${source}可指代为超大单/大单/中单/小单, 当\${source}为enormous时，表示资金方为超大单的机构在当前滚动窗口内的累积流出金额 |
| \${source}买单主动成交金额 | \${source}_buy_active_money | \${source}可指代为超大单/大单/中单/小单, 当\${source}为enormous时，表示资金方为超大单的机构在当前滚动窗口内的累积主动流入金额，买方主动意味着成交意愿来自多头 |
| \${source}卖单主动成交金额 | \${source}_buy_active_money | \${source}可指代为超大单/大单/中单/小单, 当\${source}为enormous时，表示资金方为超大单的机构在当前滚动窗口内的累积主动流出金额，卖方主动意味着成交意愿来自空头 |
| \${source}买单成交量 | \${source}_buy_vol | \${source}可指代为超大单/大单/中单/小单, 当\${source}为enormous时，表示资金方为超大单的机构在当前滚动窗口内的累积买入量 |
| \${source}卖单成交量 | \${source}_sell_vol | \${source}可指代为超大单/大单/中单/小单, 当\${source}为enormous时，表示资金方为超大单的机构在当前滚动窗口内的累积卖出量 |
| \${source}买单主动成交量 | \${source}_buy_active_vol | \${source}可指代为超大单/大单/中单/小单, 当\${source}为enormous时，表示资金方为超大单的机构在当前滚动窗口内的累积买入量，买方主动意味着成交意愿来自多头 |
| \${source}卖单主动成交量 | \${source}_buy_active_vol | \${source}可指代为超大单/大单/中单/小单, 当\${source}为enormous时，表示资金方为超大单的机构在当前滚动窗口内的累积卖出量，卖方主动意味着成交意愿来自空头 |


**createEntrustCrossSec.dos**提取出的盘口数据特征如下：
| 特征名      | 特征代码  | 描述 |
| :-------- | :-------- | :--------- | 
| 买单委托笔数 | en_buy_num | 滚动窗口内买单委托笔数 |
| 卖单委托笔数 | en_sell_num | 滚动窗口内卖单委托笔数 |
| 买单委托量 | en_buy_vol | 滚动窗口内买单委托量 |
| 卖单委托量 | en_sell_vol | 滚动窗口内卖单委托量 |
| 买单委托价 | en_buy_price | 滚动窗口内买单按照量加权的委托价 |
| 卖单委托价 | en_sell_price | 滚动窗口内卖单按照量加权的委托价 |
| 买单委托价标准差 | en_buy_price_std | 滚动窗口内买单委托价的标准差 |
| 卖单委托价标准差 | en_sell_price_std | 滚动窗口内卖单委托价的标准差 |
| 委托价标准差 | en_price_std | 滚动窗口内所有委托价的标准差 |

en_buy_num	en_sell_num	en_buy_vol	en_sell_vol	en_buy_price	en_sell_price	en_buy_price_std	en_sell_price_std	en_price_std

**createCancelOrderCrossSec.dos**提取出的盘口数据特征如下：
| 特征名      | 特征代码  | 描述 |
| :-------- | :-------- | :--------- | 
| 买单撤单笔数 | cancel_buy_num | 滚动窗口内买单撤单笔数 |
| 卖单撤单笔数 | cancel_sell_num | 滚动窗口内卖单撤单笔数 |
| 买单撤单量 | cancel_buy_vol | 滚动窗口内买单撤单量 |
| 卖单撤单量 | cancel_sell_vol | 滚动窗口内卖单撤单量 |
| 买单撤单金额 | cancel_buy_money | 滚动窗口内买单撤单金额 |
| 卖单撤单金额 | cancel_sell_money | 滚动窗口内卖单撤单金额 |
| 买单撤单时间极差 | cancel_buy_time_range | 滚动窗口内买单撤单的撤单时间分布的极差 |
| 卖单撤单时间极差 | cancel_sell_time_range | 滚动窗口内卖单撤单的撤单时间分布的极差 |
| 买单撤单时间中位数 | cancel_buy_time_med | 滚动窗口内买单撤单的撤单时间分布的中位数 |
| 卖单撤单时间中位数 | cancel_sell_time_med | 滚动窗口内卖单撤单的撤单时间分布的中位数 |
| 买单撤单时间标准差 | cancel_buy_time_std | 滚动窗口内买单撤单的撤单时间分布的标准差 |
| 卖单撤单时间标准差 | cancel_sell_time_std | 滚动窗口内卖单撤单的撤单时间分布的标准差 |
