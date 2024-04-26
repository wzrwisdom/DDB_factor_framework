import mmap
import pickle

import numpy as np
import torch
import torch.nn as nn
from net import SimpleNet, MultiChannNet
from torch.utils.data import DataLoader, Dataset
from tqdm import tqdm
from prepare import prepare_index
import os

class MyDataset(Dataset):
    def __init__(self, block_size, ):
        with open("./datas/index.pkl", 'rb') as f:
            self.index_list = pickle.load(f)

        self.data_n = len(self.index_list)
        self.block_size = block_size

        symbols, times = prepare_index.get_symbols_times()
        symbols = symbols[:1000]


        mp_dict = dict()

        for id, symbol in enumerate(symbols):
            for t in times:
                if id >= 1000:
                    mp_dict[f"datas/{symbol}-{t}.bin"] = mp_dict[f"datas/{symbols[id % 1000]}-{t}.bin"]
                    continue
                f = open(f"./datas/{symbol}-{t}.bin", 'rb')
                mp_f = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
                mp_dict[f"datas/{symbol}-{t}.bin"] = [f, mp_f]
        self.mp_dict = mp_dict
        self.symbols = symbols
        self.times = times
        

    def __len__(self):
        return self.data_n

    def __del__(self):
        for id, symbol in enumerate(self.symbols):
            if id >= 1000:
                continue
            for t in self.times:
                f, mp_f = self.mp_dict[f"datas/{symbol}-{t}.bin"]
                mp_f.close()
                f.close()
    
    def __getitem__(self, index):
        x_infos = self.index_list[index]["x"]
        y_infos = self.index_list[index]["y"]
        x_datas = []
        y_datas = []
        for x_info in x_infos:
            f, mp_f = self.mp_dict[x_info[0]]
            mp_f.seek( x_info[1] *8*61)
            data = mp_f.read(((x_info[2]+1) - x_info[1])*8*61)
            data = np.frombuffer(data, dtype=np.float64)
            x_datas.append(data[:60].reshape(-1, 60))
            y_datas.append(data[60:].reshape(-1, 1))
        x_datas = np.concatenate(x_datas, axis=0)
        # y_datas = []
        # for y_info in y_infos:
        #     f, mp_f = self.mp_dict[y_info[0]]
        #     mp_f.seek(y_info[1]*8*1)
        #     data = mp_f.read((y_info[2] - y_info[1])*8*1)
        #     data = np.frombuffer(data, dtype=np.float64)
        #     data = data.reshape(-1, 1)
        #     y_datas.append(data)
        y_datas = np.concatenate(y_datas, axis=0)
        return x_datas, y_datas

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
    dataset = MyDataset(110)
    dataloader = DataLoader(
        dataset, batch_size=128, shuffle=False, num_workers=4,
        pin_memory=True, # pin_memory_device="cuda",
        prefetch_factor=5,
    )

    epoch = 10
    train_losses = []
    
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
        train_losses.append(loss.data)
            
    os.makedirs("./models/", exist_ok=True)
    torch.save(model.state_dict(),  f"./models/{model_name}_old.pth")
    
    # plot the distribution of train losses
    import matplotlib.pyplot as plt
    os.makedirs("./plots", exist_ok=True)
    train_losses = [i.cpu().detach().numpy() for i in train_losses]
    plt.plot(train_losses, label='Training Loss')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.title('Training Loss')
    plt.legend()
    plt.savefig(f"plots/{model_name}_train_loss.pdf")

if __name__ == "__main__":
    main()

