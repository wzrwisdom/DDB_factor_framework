import pickle
import time
def get_symbols_times():
    import dolphindb as ddb 
    s = ddb.session()
    s.connect("localhost", 11281, "admin", "123456")
    dbPath = "dfs://ai_dataloader"
    tbName = "wide_factor_table"
    
    t1 = s.loadTable(tableName=tbName,dbPath=dbPath)
    
    symbols = t1.exec(['distinct security_code']).toList().tolist()
    # symbols = ["`"+i for i in symbols]
    times = t1.exec(['distinct trade_time']).toList().tolist()
    times = [i.strftime("%Y.%m.%d") for i in times]
    return symbols, times
    
if __name__ == "__main__":
    # 每天每支股票有多少行数据
    block_size = 110 #4802

    # 滑动窗口大小和步长
    window_size = 1 #200
    window_stride = 1
    # 偏移行数
    offset = 0 #window_size

    # symbols = [f"{i}.SH".zfill(9) for i in range(1, 251)]
    ## Test
    # symbols = [f"{i}.SH".zfill(9) for i in range(1, 11)]
    # times = ["2020.01." + f"{i+1}".zfill(2) for i in range(31)]
    symbols, times = get_symbols_times()
    symbols = symbols[:1000]

    index_list = []

    st = time.time()

    for symbol in symbols:
        all_length = block_size * len(times)
        data_n = (all_length - window_size) // window_stride + 1

        for idx in range(data_n):
            idx_L = idx * window_stride
            idx_R = idx_L + window_size - 1
            bid_L = idx_L // block_size
            bid_R = idx_R // block_size
            if bid_L == bid_R:
                X_info = [
                    (f"datas/{symbol}-{times[bid_L]}.bin", idx_L % block_size, idx_R % block_size),
                ]
            else:
                X_info = [
                    (f"datas/{symbol}-{times[bid_L]}.bin", idx_L % block_size, block_size),
                    (f"datas/{symbol}-{times[bid_R]}.bin", 0, idx_R % block_size),
                ]

            idx_L = idx_L + offset
            idx_R = idx_L
            if idx_R >= all_length:
                break
            bid_L = idx_L // block_size
            bid_R = idx_R // block_size
            if bid_L == bid_R:
                Y_info = [
                    (f"datas/{symbol}-{times[bid_L]}.bin", idx_L % block_size, idx_R % block_size),
                ]
            else:
                Y_info = [
                    (f"datas/{symbol}-{times[bid_L]}.bin", idx_L % block_size, block_size),
                    (f"datas/{symbol}-{times[bid_R]}.bin", 0, idx_R % block_size),
                ]
            index_list.append({'x': X_info, 'y': Y_info})
        print(f"[{symbol}] READY")

    # 将索引信息保存至文件
    with open("../datas/index.pkl", 'wb') as f:
        pickle.dump(index_list, f)
    ed = time.time()
    # 统计计算索引信息所需时间
    print("total time: ", ed-st)



