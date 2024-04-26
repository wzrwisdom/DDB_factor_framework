import operator
import random
import numpy as np
import pandas as pd
from scipy.stats import pearsonr
from deap import base, creator, tools, gp
import operator
from functools import partial
import warnings
from scipy.stats import ConstantInputWarning 
import inspect
from lib import mygp
from lib import myoperator  # 导入你的myopt模块
from deap import algorithms

random.seed(10)
# Load stock data 
data = pd.read_csv('../DownloadData/csv/OneMin_KLine.csv', index_col=0)
data['trade_time'] = pd.to_datetime(data['trade_time'])
data['security_code'] = data['security_code'].astype(str).str.zfill(6)

# Obtain  the return for the next n minutes
n = 5
grouped = data.groupby(['security_code'])
data['new_ret'] = grouped['close'].apply(lambda x: x.shift(-n)/x.shift(-1)-1).droplevel(0)
# data['new_ret'] = data.groupby('security_code')['ret'].shift(-n)
data = data[~data.isna().any(axis=1)]

infos = {}
cols = ['open', 'close', 'high', 'low']
for col in cols:
    infos[col] = pd.pivot_table(data, values=col, index=["trade_time"], columns=["security_code"])
    infos[col] = infos[col]
    
# creating a primitive set
# pset = gp.PrimitiveSet("MAIN", len(infos))

pset = gp.PrimitiveSetTyped("MAIN", [pd.DataFrame]*len(infos), pd.DataFrame)
pset.addPrimitive(np.add, [pd.DataFrame, pd.DataFrame], pd.DataFrame)
pset.addPrimitive(np.subtract, [pd.DataFrame, pd.DataFrame], pd.DataFrame)
pset.addPrimitive(np.multiply, [pd.DataFrame, pd.DataFrame], pd.DataFrame)
pset.addPrimitive(np.abs, [pd.DataFrame], pd.DataFrame)
pset.addPrimitive(np.negative, [pd.DataFrame], pd.DataFrame)
pset.addPrimitive(np.log, [pd.DataFrame], pd.DataFrame)
pset.addPrimitive(np.sqrt, [pd.DataFrame], pd.DataFrame)


# 获取myopt模块中的所有函数
functions = inspect.getmembers(myoperator, inspect.isfunction)
for name, func in functions[:2]:
    # obtain the function signature
    signature = inspect.signature(func) 
    # obtain the parameter types
    param_types = [param.annotation for param in signature.parameters.values()]
    # obtain the return value type
    return_type = signature.return_annotation
    print(name)
    pset.addPrimitive(func, param_types, return_type)

pset.addEphemeralConstant("randFloat", partial(random.uniform, -1, 1), float)
pset.addEphemeralConstant("randInt", partial(random.randint, 1, 10), int)
pset.renameArguments(ARG0='open')
pset.renameArguments(ARG1='close')
pset.renameArguments(ARG2='high')
pset.renameArguments(ARG3='low')

# evaluate the fitness for each indivisual
# Define evaluation function based on IC
warnings.filterwarnings('error')
def evaluate_factor(individual, pset):
    # print(individual)
    func = gp.compile(individual, pset)
    try:
        factor_values = func(*[infos[i] for i in cols])
    except Warning as w:
        if issubclass(type(w), RuntimeWarning):
            # handle ConstantInputWarning
            return (-1,)
        else:
            # other warnings
            print(individual)
            print(w)
            pass
        
    if not isinstance(factor_values, pd.DataFrame):
        return (-1,)
    
    df1 = pd.melt(factor_values.reset_index(), id_vars='trade_time', value_vars=factor_values.columns.tolist(), var_name='security_code', value_name='value', )
    df1.sort_values(by=['security_code', 'trade_time'], ascending=[True, True])
    df1 = df1[~df1['value'].isna()]
    if df1.empty:
        return (-1,)
    df1 = pd.merge(df1, data[['trade_time', 'security_code', 'new_ret']], on=['trade_time', 'security_code'], how='inner')
    try:
        result = pearsonr(df1['value'], df1['new_ret'])
    except Warning as w:
        if issubclass(type(w), ConstantInputWarning):
            # handle ConstantInputWarning
            return (-1,)
        else:
            # other warnings
            print(individual)
            print(w)
            pass
        
    return (abs(result[0]),)
    # expression = ''.join(individual)
    # factor_values = eval(expression, {'__builtins__': None}, data)  # Evaluate expression using data
    # ic_value, _ = pearsonr(factor_values, data['returns'])  # Calculate Pearson correlation coefficient (IC value)
    # return ic_value,
    

# DEAP setup
creator.create("FitnessMax", base.Fitness, weights=(1.0,))
# creator.create("Individual", list, fitness=creator.FitnessMin)
creator.create("Individual", gp.PrimitiveTree, fitness=creator.FitnessMax)


toolbox = base.Toolbox()
toolbox.register("expr", mygp.mygenGrow, pset=pset, min_=1, max_=4)
# toolbox.register("individual", initIndividual, creator.Individual, toolbox.expr, size=3)  # 假设我们创建3个特征
toolbox.register("individual", tools.initIterate, creator.Individual, toolbox.expr)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)
toolbox.register("compile", gp.compile, pset=pset)


toolbox.register("evaluate", evaluate_factor, pset=pset)
toolbox.register("select", tools.selTournament, tournsize=3)
toolbox.register("mate", mygp.cxOnePoint)
toolbox.register("expr_mut", mygp.mygenGrow, min_=0, max_=2)
toolbox.register("mutate", gp.mutUniform, expr=toolbox.expr_mut, pset=pset)




# 定义统计指标
stats_fit = tools.Statistics(lambda ind: ind.fitness.values)
# stats_size = tools.Statistics(len)
# mstats = tools.MultiStatistics(fitness=stats_fit, size=stats_size)
stats_fit.register("avg", np.nanmean)
stats_fit.register("std", np.nanstd)
stats_fit.register("min", np.nanmin)
stats_fit.register("max", np.nanmax)

# # 使用默认算法
# def main():
#     population = toolbox.population(n=100)
#     num_best = 20
#     hof = tools.HallOfFame(num_best)
#     pop, log  = algorithms.eaSimple(population=population,
#                             toolbox=toolbox, cxpb=0.6, mutpb=0.1, ngen=10, stats=stats_fit, halloffame=hof, verbose=True)

    

#     # best_ind = tools.selBest(population, 1)[0]
#     print([ind.fitness.values[0] for ind in population])
#     for i in range(num_best):
#         print("The %dth best individual is: " % i)
#         print(hof[i])
#         print(hof[i].fitness.values[0])
#     # best_ind = hof[0]
#     # print("Best individual is %s, %s" % (best_ind, best_ind.fitness.values))
    
def main(checkpoint=None):
    import pickle
    if checkpoint:
        # A file name has been given, then load the data from the file
        with open(checkpoint, "rb") as cp_file:
            cp = pickle.load(cp_file)
        population = cp["population"]
        start_gen = cp["generation"]
        halloffame = cp["halloffame"]
        logbook = cp["logbook"]
        random.setstate(cp["rndstate"])
    else:
        # Start a new evolution
        population = toolbox.population(n=100)
        start_gen = 0
        halloffame = tools.HallOfFame(maxsize=20)
        logbook = tools.Logbook()

    NGEN=10
    FREQ = 5
    for gen in range(start_gen, NGEN):
        population = algorithms.varAnd(population, toolbox, cxpb=0.6, mutpb=0.1)

        # Evaluate the individuals with an invalid fitness
        invalid_ind = [ind for ind in population if not ind.fitness.valid]
        fitnesses = toolbox.map(toolbox.evaluate, invalid_ind)
        for ind, fit in zip(invalid_ind, fitnesses):
            ind.fitness.values = fit

        halloffame.update(population)
        record = stats_fit.compile(population)
        logbook.record(gen=gen, evals=len(invalid_ind), **record)

        population = toolbox.select(population, k=len(population))

        if gen % FREQ == 0:
            # Fill the dictionary using the dict(key=value[, ...]) constructor
            cp = dict(population=population, generation=gen, halloffame=halloffame,
                      logbook=logbook, rndstate=random.getstate())

            with open("checkpoint_name.pkl", "wb") as cp_file:
                pickle.dump(cp, cp_file)

if __name__ == "__main__":
    main()
