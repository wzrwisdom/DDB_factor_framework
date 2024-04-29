
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
利用导入到DDB的原始快照，逐笔成交以及逐笔委托数据，我们按照一定的滚动时间窗口进行特征提取。以000014标的为例，按照6s的频率特征提取的输出保存在./output/CROSS_SECTION_6SEC中。

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