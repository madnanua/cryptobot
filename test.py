import pandas as pd

retlast = 0.12
def add(retlast):
    df = pd.read_csv("returns.csv",names=['r'])
    retprev = df['r'].iloc[-1]
    retnew = float(retlast)+float(retprev)
    df2 = pd.DataFrame({'r': [retnew]})
    df2.to_csv("returns.csv", mode='a', header=False,index=False)

    return retnew

result = add(retlast=retlast)
# result=retlast
print(result)

# retprev = ret(1)
# rettotal = retprev+retlast
# returns.append(rettotal)
