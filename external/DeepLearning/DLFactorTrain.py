import dolphindb as ddb
import torch
import torch.nn as nn
from net import SimpleNet, MultiChannNet
from tqdm import tqdm
import os

from dolphindb_tools.dataloader import DDBDataLoader

def get_model(model_name):
    if model_name == "simple_model":
        model = SimpleNet(features_in=60)
    elif model_name == "multichann_model":
        model = MultiChannNet(features_in=6)
    
    model = model.to("cuda")
    return model


def main():
    torch.set_default_tensor_type(torch.DoubleTensor)

    model_name = "multichann_model"
    model = get_model(model_name)
    loss_fn = nn.MSELoss()
    loss_fn = loss_fn.to("cuda")
    optimizer = torch.optim.Adam(model.parameters(), lr=0.05)

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
    sql = f"""select * from loadTable("{dbPath}", "{tbName}")"""
    
    dataloader = DDBDataLoader(
        s, sql, targetCol=["label"], batchSize=64, shuffle=True,
        windowSize=[1, 1], windowStride=[1, 1],
        repartitionCol="date(trade_time)", repartitionScheme=times,
        groupCol="security_code", groupScheme=symbols,
        seed=0, offset=0,
        excludeCol=["label"], device="cuda",
        prefetchBatch=5, prepartitionNum=3
    )

    epoch = 1
    model.train()
    for _ in range(epoch):
        for x, y in tqdm(dataloader, mininterval=1):
            x = x.to("cuda")
            y = y.to("cuda")
            y_pred = model(x)
            loss = loss_fn(y_pred, y)
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
    os.makedirs("./models/", exist_ok=True)
    torch.save(model.state_dict(),  f"./models/{model_name}.pth")


if __name__ == "__main__":
    main()
