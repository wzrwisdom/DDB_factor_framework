# DDB_factor_framework
## 简介
本因子研发框架是利用DolphinDB（之后简称为DDB）的脚本语言编写的。在此基础上，研发框架依赖于DDB的因子开发管理平台(简称因子平台)，将重复性的工作流程整合在这个研究框架内。因子平台包括因子库，因子评价以及数据导入模块。本项目按照这些模块的结构进行保存管理相关代码。在因子平台中按照下面的文件结构在对应的模块创建文件，并将对应的代码复制过去即可。

项目的路径大致如下:

```
├── DDB_factor_framework 
│ ├── data_loader
│ │ ├── loader_library
│ │ ├── data_load_template
│ ├── factor
│ │ ├── factor_draft
│ │ ├── factor_cal_template
│ ├── factor_evaluate
│ │ ├── evaluate_library
│ │ ├── evaluate_template
│ ├── external
```




## 数据导入模块
数据导入模块对应文件夹/data_loader，数据导入模块中包括"导入函数库"以及"数据导入模版",分别对应文件夹data_loader下的loader_library和data_load_template子文件夹

## 因子库模块
因子库模块对应文件夹/factor，因子库模块中包括"我的草稿"以及"因子计算模版",分别对应文件夹factor下的factor_draft和factor_cal_template子文件夹

## 因子评价模块
因子评价模块对应文件夹/factor_evaluate，因子评价模块中包括"评价函数库"以及"评价模版",分别对应文件夹factor_evaluate下的evaluate_library和evaluate_template子文件夹

## 外部应用
由于并非量化研究的所有工作都能便捷地在因子管理平台中实现。比如当我们有使用遗传算法挖掘有效因子、利用更复杂的深度学习模型进行因子组合等需求时，因子管理平台目前来说无能为力。这部分代码我们使用DDB的API来获取数据，然后结合Python的生态环境中的Package进行实现需求。这部分代码存放在/external文件夹

