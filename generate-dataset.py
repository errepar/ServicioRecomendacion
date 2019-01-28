import sqlite3
import pandas as pd

connection = sqlite3.connect('errepar-data.db')
cursor = connection.cursor()
query = open('search_most_used_service.sql', mode='r', encoding='utf-8')
cursor.execute(query.read())

headers = list(map(lambda x: x[0], cursor.description))
results = cursor.fetchall()

df = pd.DataFrame(data=results, columns=headers)
