
数据导入模块下的文件结构以及对应文件的功能简介：

│ ├── data_loader
│ │ ├── loader_library
│ │ │ └── CSVDataModule.dos  提供解析路径，导入csv文件到DDB库表，提交导入job等函数
│ │ ├── data_load_template
│ │ │ └── loadTrade.dos  指定csv存放的路径，按照日期范围进行导入逐笔成交数据
│ │ │ └── loadEntrust.dos  指定csv存放的路径，按照日期范围进行导入逐笔委托数据
│ │ │ └── loadSnapshot.dos  指定csv存放的路径，按照日期范围进行导入原始3s快照数据
│ │ │ └── createOneMinuteKLineChart.dos  将导入的原始快照数据聚合生成1min的K线数据
│ │ │ └── createFiveMinuteKLineChart.dos  将导入的原始快照数据聚合生成5min的K线数据
