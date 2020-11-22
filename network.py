import pandas as pd
import os

df = pd.read_csv(os.path.dirname(__file__) + '/Amtrak_Routes.csv', engine='python') # test with , nrows=20
df = df.loc[df['STATEAB'] == 'TX']

#Create an example dataframe
# data = {'name': ['Jason', 'Molly', 'Tina'], 
#         'TOFRANODE': ['four', 'one', 'three'], 
#         'FRFRANODE': ['three', 'two', 'zero']}
# df = pd.DataFrame(data)
# print(df)

# def networks(n,lst):
#     groups= []
#     for i in range(n):
#         groups.append({i})
#     for pair in lst:
#         union = groups[pair[0]]|groups[pair[1]]
#         for p in union:
#             groups[p]=union
#     sets= set()
#     for g in groups:
#         sets.add(tuple(g))
#     i=0
#     for s in sets:
#         print("network",i,"is",set(s))
#         i+=1



def networks(df, to_, from_):
    u_vals = (df[to_].append(df[from_])).unique()
    val_2_index = {}
    index_2_val = {}   
    i = 0
    for val in u_vals:
        val_2_index[val] = i
        index_2_val[i] = val
        i += 1
    df['to_id'] = df[to_].replace(val_2_index)
    df['from_id'] = df[from_].replace(val_2_index)
    groups= []
    for i in range(len(u_vals)):
        groups.append({i})
    for index, row in df.iterrows():
        union = groups[row['from_id']]|groups[row['to_id']]
        for p in union:
            groups[p]=union
    sets= set()
    for g in groups:
        sets.add(tuple(g))
    # i=0
    # for s in sets:
    #     print("network",i,"is",set(s))
    #     i+=1
    sets_final= set()
    for s in sets:
        L = list(s)
        for i in range(len(L)):
            L[i] = index_2_val[s[i]]
        sets_final.add(tuple(L))
    return(sets_final)

sets = networks(df, 'TOFRANODE', 'FRFRANODE')
print(sets)