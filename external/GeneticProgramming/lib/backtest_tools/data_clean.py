import numpy as np

# data wash
class data_wash:
    #去极值    
    def three_sigma(factor):
        mean = factor.mean()
        std = factor.std()
        up = mean + 3*std
        down = mean - 3*std
        return np.clip(factor,down,up)
    #标准化
    def standardize(factor):
        mean = factor.mean()
        std = factor.std()
        factor = (factor - mean)/std
        return factor