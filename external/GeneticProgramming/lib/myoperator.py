import numpy as np
import pandas as pd

def div(X:pd.DataFrame, Y:pd.DataFrame)->pd.DataFrame:
    assert isinstance(X, pd.DataFrame) and isinstance(Y, pd.DataFrame), "a and b should be pandas dataframe" 
    assert X.shape == Y.shape, "The shape of two dataframes should be the same"
    result = X / Y
    return result.where(np.isfinite(result), 0)

def inv(X:pd.DataFrame)->pd.DataFrame:
    assert isinstance(X, pd.DataFrame), "a should be a pandas dataframe" 
    result = 1 / X
    return result.where(np.isfinite(result), 0) 

def rank(X:pd.DataFrame)->pd.DataFrame:
    ranked_X = X.rank(axis=1)
    return ranked_X.astype(int)

def delay(X:pd.DataFrame, n:int=5)->pd.DataFrame:
    assert isinstance(X, pd.DataFrame), "a should be a pandas dataframe" 
    result = X.shift(n)
    return result

def ts_corr(X:pd.DataFrame, Y:pd.DataFrame, d:int)->pd.DataFrame:
    assert isinstance(X, pd.DataFrame) and isinstance(Y, pd.DataFrame), "X and Y should be pandas dataframe" 
    assert X.shape == Y.shape, "The shape of two dataframes should be the same"
    result = X.rolling(window=d).corr(Y)
    return result # result.where(np.isfinite(result), 0)

def ts_cov(X:pd.DataFrame, Y:pd.DataFrame, n:int)->pd.DataFrame:
    assert isinstance(X, pd.DataFrame) and isinstance(Y, pd.DataFrame), "X and Y should be pandas dataframe" 
    assert X.shape == Y.shape, "The shape of two dataframes should be the same"
    result = X.rolling(window=n).cov(Y)
    return result

def scale(X:pd.DataFrame, a:float=1.)->pd.DataFrame:
    assert isinstance(X, pd.DataFrame), "X should be pandas dataframe" 
    assert isinstance(a, (int, float)), "a should be number"
    a = abs(a)
    return a*(X.div(X.abs().sum(axis=1), axis=0))

def delta(X:pd.DataFrame, n:int)->pd.DataFrame:
    assert isinstance(X, pd.DataFrame), "a should be a pandas dataframe" 
    result = X - X.shift(n)
    return result

def signedpower(X:pd.DataFrame, a:float)->pd.DataFrame:
    assert isinstance(X, pd.DataFrame), "X should be a pandas dataframe" 
    assert isinstance(a, (int, float)), "a should be number"
    result = np.sign(X) * (np.abs(X) ** a)
    return result


def decay_linear(X:pd.DataFrame, n:int)->pd.DataFrame:
    assert isinstance(X, pd.DataFrame), "X should be a pandas dataframe" 
    assert isinstance(n, (int)) and n > 0, "n should be positive integer"
    def weighted_average(arr:pd.Series, weights:range)->float:
        return np.average(arr, weights=weights) 
    weights = range(n, 0, -1)
    result = X.rolling(window=n).apply(weighted_average, args=(weights,))
    return result

def ts_min(X:pd.DataFrame, n:int)->pd.DataFrame:
    assert isinstance(X, pd.DataFrame), "X should be a pandas dataframe" 
    result = X.rolling(window=n).min()
    return result

def ts_max(X:pd.DataFrame, n:int)->pd.DataFrame:
    assert isinstance(X, pd.DataFrame), "X should be a pandas dataframe" 
    result = X.rolling(window=n).max()
    return result

def ts_argmin(X:pd.DataFrame, n:int)->pd.DataFrame:
    assert isinstance(X, pd.DataFrame), "X should be a pandas dataframe" 
    result = X.rolling(window=n).apply(np.argmin)
    return result

def ts_argmax(X:pd.DataFrame, n:int)->pd.DataFrame:
    assert isinstance(X, pd.DataFrame), "X should be a pandas dataframe" 
    result = X.rolling(window=n).apply(np.argmax)
    return result

def ts_rank(X:pd.DataFrame, n:int)->pd.DataFrame:
    assert isinstance(X, pd.DataFrame), "X should be a pandas dataframe" 
    def rank_pct(arr:pd.Series)->float:
        return arr.rank(pct=True).iloc[-1]
    result = X.rolling(window=n).apply(rank_pct)
    return result

def ts_sum(X:pd.DataFrame, n:int)->pd.DataFrame:
    assert isinstance(X, pd.DataFrame), "X should be a pandas dataframe" 
    result = X.rolling(window=n).sum()
    return result

def ts_prod(X:pd.DataFrame, n:int)->pd.DataFrame:
    assert isinstance(X, pd.DataFrame), "X should be a pandas dataframe" 
    result = X.rolling(window=n).apply(np.prod)
    return result

def ts_stddev(X:pd.DataFrame, n:int)->pd.DataFrame:
    assert isinstance(X, pd.DataFrame), "X should be a pandas dataframe" 
    result = X.rolling(window=n).std()
    return result


def ts_zscore(X:pd.DataFrame, n:int)->pd.DataFrame:
    assert isinstance(X, pd.DataFrame), "X should be a pandas dataframe" 
    result = (X - X.rolling(window=d).mean()) / X.rolling(window=d).std()
    return result

def rank_sub(X:pd.DataFrame, Y:pd.DataFrame)->pd.DataFrame:
    assert isinstance(X, pd.DataFrame) and isinstance(Y, pd.DataFrame), "X and Y should be pandas dataframe" 
    assert X.shape == Y.shape, "The shape of two dataframes should be the same"
    result = X.rank(axis=1) - Y.rank(axis=1)
    return result

def rank_div(X:pd.DataFrame, Y:pd.DataFrame)->pd.DataFrame:
    assert isinstance(X, pd.DataFrame) and isinstance(Y, pd.DataFrame), "X and Y should be pandas dataframe" 
    assert X.shape == Y.shape, "The shape of two dataframes should be the same"
    result = X.rank(axis=1) / Y.rank(axis=1)
    return result

def sigmoid(X:pd.DataFrame)->pd.DataFrame:
    assert isinstance(X, pd.DataFrame), "X should be a pandas dataframe" 
    result = 1 / (1 + np.exp(-X))
    return result