外部拓展应用的文件结构如下：

│ ├── external
│ │ ├── DownloadData 
│ │ │ └── data_prepare.ipynb  利用DDB的Python API将库表中的数据导入到本地的csv文件
│ │ ├── DeepLearning 该路径下存放着一个普通的CNN模型训练及运用的代码，其中包括利用DDB提供的DDBDataLoader的版本
│ │ ├── GeneticProgramming 该路径下存放着利用DEAP库实现的遗传算法的代码以及分层回测
