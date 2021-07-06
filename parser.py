import pandas as pd

def gettable(id):
    table = pd.read_html('https://db-nica.ru/ranking?group='+str(id)+'&region=0')
    return table[0]

df = gettable(1)
for i in range(2,13):
    df = df.append(gettable(i), ignore_index=True)

print(df.info())

df.to_csv ('univers.csv', index = False, header=True)