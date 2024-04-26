import pandas as pd
import numpy as np
from data_clean import data_wash
import statsmodels.api as sm

def get_factor_total_performance(df:pd.DataFrame)->pd.DataFrame:
    # minute-level volatility
    minute_volatility = df.std()
    minute_volatility.name = 'minute_volatility'
    
    # total return
    total_return = (df+1).prod() - 1
    total_return.name = 'total_erturn'
    
    # annualized return
    total_days = (df.index[-1] - df.index[0]).total_seconds() / (60*60*4)
    annual_return = (1+total_return) ** (252/total_days) - 1
    annual_return.name = 'annual_return'
    
    # maximum drawback
    cumulative_returns = (df + 1).cumprod()
    max_drawdown = (cumulative_returns / cumulative_returns.cummax() - 1).min()
    max_drawdown.name = 'max_drawdown'  
     
    # assume the risk-free rate is 0.02 (2%)
    risk_free_rate = 0.02
    # sharpe ratio
    sharpe_ratio = (total_return - ((1+risk_free_rate)**(total_days/252) - 1)) / (minute_volatility * np.sqrt(total_days*60*4))
    sharpe_ratio.name = 'sharpe_ratio'
    
    return pd.DataFrame(index=df.columns).join([minute_volatility, total_return, annual_return, max_drawdown, sharpe_ratio])

def get_factor_statistics_indicators(df_factor:pd.DataFrame, df_future_return:pd.DataFrame, factor_name:str="factor")->tuple[bool, str]:
    indicators = ['IC', 'RankIC', 'tValue']
    for i in indicators:
        exec(f'group_{i}' + '={}', globals())
    
    date_list = df_factor.index
    for date in date_list:
        # print(date)
        # obtain the current factor and future return
        cur_factor = df_factor.loc[date]
        cur_future_return = df_future_return.loc[date]
        
        index_notna = cur_factor[~cur_factor.isna()].index
        cur_factor = cur_factor[index_notna]
        cur_future_return = cur_future_return[index_notna]
        
        # calculate the IC, RankIC, tValue of the factor  
        group_IC[date] = cur_factor.corr(cur_future_return)
        group_RankIC[date] = cur_factor.corr(cur_future_return, method='spearman')
        
        x = sm.add_constant(cur_factor)
        model = sm.OLS(cur_future_return, x).fit()
        group_tValue[date] = model.tvalues.loc[date]
    
    # collect the IC, RankIC, tValue of the factor  
    group_list = [pd.Series(eval(f"group_{i}"), name=f'group{i}') for i in indicators]
    df_indicators_detail = pd.concat(group_list, axis=1)
    
    IC, IR = df_indicators_detail['groupIC'].mean(), df_indicators_detail['groupIC'].std()
    ICIR = IC/IR
    IClgZero = (df_indicators_detail['groupIC'] > 0).sum() / len(df_indicators_detail['groupIC'])
    RankIC, RankIR = df_indicators_detail['groupRankIC'].mean(), df_indicators_detail['groupRankIC'].std()
    RankICIR = RankIC/RankIR
    RankIClgZero = (df_indicators_detail['groupRankIC'] > 0).sum() / len(df_indicators_detail['groupRankIC'])
    tabsMean = df_indicators_detail['grouptValue'].abs().mean()
    tlgTwo = (df_indicators_detail['grouptValue'].abs()>2).sum() / len(df_indicators_detail['grouptValue'])
    tMean = df_indicators_detail['grouptValue'].mean()
    
    # collect the statistics indicators
    statistics_dict = {
        'IC': IC, 'IR': IR, 'ICIR': ICIR, 'IClgZero': IClgZero, 
        'RankIC': RankIC, 'RankIR': RankIR, 'RankICIR': RankICIR, 'RankIClgZero': RankIClgZero, 
        'tabsMean': tabsMean, 'tlgTwo': tlgTwo, 'tMean': tMean}
    df_agg = pd.concat([pd.Series(statistics_dict, name=factor_name)], axis=1)
    return df_indicators_detail, df_agg
    
    
        

def get_factor_layer_return(df_factor:pd.DataFrame, df_return:pd.DataFrame, n=10, freq=5):
    """
    :param df_factor: factor data
    :param df_return: return data
    :param n: the holding period
    # :param quantile: the number of quantile
    # :param long_short: whether to long and short
    # :param equal_weight: whether to use equal weight
    # :param commission: commission rate
    # :param slippage: slippage rate
    # :param initial_cash: initial cash
    :param freq: the frequency of rebalancing
    :return: backtest result
    """
    # stock_list = df_factor.columns
    date_list = df_factor.index
    # usually we will divide the stocks into n groups,
    # then we need to record how the returns of these groups are generated

    # as you can see, we have n dictionaries
    for i in range(1, n+1):
        exec(f"group_{i}"+ "= {}", globals())
    group_long_short = {}

    # we need to iterate over each day, notice the freq, it means how often we need to regroup
    for i in range(0,len(date_list),freq):
        # initialize the group return
        if (i == 0):
            date = date_list[i]
            for k in range(1, n+1):
                exec(f"group_{k}[date] = 0")
            group_long_short[date] = 0
                
        # obtain the factor value of the ith day
        df_test = df_factor.loc[date_list[i],:]
        # Do data cleaning for the cross-sectional data
        df_test = data_wash.three_sigma(df_test)
        df_test = data_wash.standardize(df_test)
        # sort the factor value and perform the grouping operation
        df_test.sort_values(ascending=True,inplace=True)
        stock_all = list(df_test.index)
        lens = len(stock_all)
        
        edges = [int(ei) for ei in np.linspace(0, lens, n+1)]
        for j, ei in enumerate(range(0, n)):
            exec(f"stock_pool{j+1} = stock_all[edges[ei]:edges[ei+1]]")

        # calculate the cumulative return for current time period
        date_period = date_list[i: i+freq]
        df_cur_cumret = (df_return.loc[date_period]+1).cumprod()
        # record the average daily return of each group
        for j in range(i+1,i+freq):
            try:
                # extract the date of the jth day
                date = date_list[j]
                # calculate the average return of each group each day
                for k in range(1, n+1):
                    exec(f"group_{k}[date] = (df_cur_cumret.loc[date, stock_pool{k}].mean() - 1)")
                group_long_short[date] = eval(f"group_{1}[date] - group_{n}[date]")
            except:
                continue
            
    # combine the data of each group into a dataframe
    group_list = [pd.Series(eval(f"group_{i}"), name=f'group{i}') for i in range(1, n+1)] + [pd.Series(group_long_short, name='group_long_short')]
    df_result = pd.concat(group_list, axis=1)
    return df_result    



