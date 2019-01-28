import sqlite3
import pandas as pd


connection = sqlite3.connect('errepar-data.db')
cursor = connection.cursor()
query = open('search_most_used.sql', mode='r', encoding='utf-8')
cursor.execute(query.read() % (90218, 10))

headers = list(map(lambda x: x[0], cursor.description))

results = cursor.fetchall()


def clean_values(value):
    aux = value.strip()

    if aux == 'ND':
        return 'None'

    return aux


df = pd.DataFrame(data=results, columns=headers)
df = df.drop(axis='columns', labels='index')
df['age'] = df['age'].apply(lambda x: clean_values(x))
df['nameSubtema'] = df['nameSubTema'].apply(lambda x: clean_values(x))
df['nameOfBehaviour'] = df['nameOfBehaviour'].apply(lambda x: clean_values(x))
