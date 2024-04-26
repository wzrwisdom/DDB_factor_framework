import dolphindb as ddb
import torch
import torch.nn as nn
from net import SimpleNet
from tqdm import tqdm
import os

from dolphindb_tools.dataloader import DDBDataLoader
def constructDataLoader():
    s = ddb.session()
    s.connect("127.0.0.1", 11281, "admin", "123456")
    # 加载库表
    dbPath = "dfs://ai_dataloader"
    tbName = "wide_factor_table"
    t1 = s.loadTable(tableName=tbName,dbPath=dbPath)
    symbols = t1.exec(['distinct security_code']).toList().tolist()
    symbols = ["`"+i for i in symbols]
    times = t1.exec(['distinct trade_time']).toList().tolist()
    times = [i.strftime("%Y.%m.%d") for i in times]
    times = list(set(times))
    
    splitTS = "2023.04.21 13:00:00"
    sql = f"""select * from loadTable("{dbPath}", "{tbName}") where trade_time >= {splitTS} """
    
    dataloader = DDBDataLoader(
        s, sql, targetCol=["label"], batchSize=64, shuffle=True,
        windowSize=[1, 1], windowStride=[1, 1],
        repartitionCol="date(trade_time)", repartitionScheme=times,
        groupCol="security_code", groupScheme=symbols,
        seed=0,
        excludeCol=["label"], device="cuda",
        prefetchBatch=5, prepartitionNum=3
    )
    return dataloader
    
def apply():
    dataloader = constructDataLoader()
    
    torch.set_default_tensor_type(torch.DoubleTensor)
    model = SimpleNet(features_in=60)
    model.load_state_dict(torch.load("./models/simple_model.pth"))
     
    model.eval()
    with torch.no_grad():
        for x, y in tqdm(dataloader, mininterval=1):
            x = x.to("cuda")
            y_pred = model(x)
            print(type(y_pred))