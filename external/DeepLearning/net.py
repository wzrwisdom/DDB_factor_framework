import torch
import torch.nn as nn
def reshape_fortran(x, shape):
    if len(x.shape) > 0:
        x = x.permute(*reversed(range(len(x.shape))))
    return x.reshape(*reversed(shape)).permute(*reversed(range(len(shape))))

class SimpleNet(nn.Module):
    def __init__(self, features_in) -> None:
        super(SimpleNet, self).__init__()
        self.channels = [1, 1, 1]
        self.features_in = features_in
        self.features_out = 1
        self.conv1d_1 = nn.Conv1d(self.channels[0], self.channels[1], 10, 2, 4)
        self.conv1d_2 = nn.Conv1d(self.channels[1], self.channels[2], 10, 2, 4)
        self.fc1 = nn.Linear(self.channels[2] * self.features_in//4, self.features_in)
        self.fc2 = nn.Linear(self.features_in, self.features_out)
        self.relu = nn.ReLU()
        self.sigmoid = nn.Sigmoid()

    def forward(self, x: torch.Tensor):
        x = self.conv1d_1(x)
        x = self.sigmoid(x)
        x = self.conv1d_2(x)
        x = self.sigmoid(x)
        x = x.flatten(start_dim=1)
        x = self.fc1(x)
        x = self.sigmoid(x)
        x = self.fc2(x)
        x = x.reshape([-1, 1, self.features_out])
        return x



class MultiChannNet(nn.Module):
    def __init__(self, features_in) -> None:
        super(MultiChannNet, self).__init__()
        self.channels = [10, 8, 4]
        self.features_in = features_in
        self.features_out = 1
        self.conv1d_1 = nn.Conv1d(self.channels[0], self.channels[1], 4, 2, 4)
        self.conv1d_2 = nn.Conv1d(self.channels[1], self.channels[2], 4, 2, 2)
        self.fc1 = nn.Linear(self.channels[2] * (self.features_in//2+1), self.features_in)
        self.fc2 = nn.Linear(self.features_in, self.features_out)
        self.relu = nn.ReLU()
        self.sigmoid = nn.Sigmoid()
        self.bn1 = nn.BatchNorm1d( self.features_in )
        self.bn2 = nn.BatchNorm1d( (self.features_in -4 +2*2)//2 + 1 )
        self.bn_fc1 = nn.BatchNorm1d( self.features_in )

    def forward(self, x: torch.Tensor):
        x = reshape_fortran(x, (-1, 10, self.features_in))
        x = self.conv1d_1(x)
        x = self.bn1(x.transpose(1, 2)).transpose(1, 2)
        x = self.sigmoid(x)
        
        x = self.conv1d_2(x)
        x = self.bn2(x.transpose(1, 2)).transpose(1, 2)
        x = self.sigmoid(x)
        x = x.flatten(start_dim=1)
        x = self.fc1(x)
        x = self.bn_fc1(x)
        x = self.sigmoid(x)
        x = self.fc2(x)
        x = x.reshape([-1, 1, self.features_out])
        return x
