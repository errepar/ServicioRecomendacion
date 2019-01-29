import sqlite3
import pandas as pd


connection = sqlite3.connect('errepar-data.db')
cursor = connection.cursor()
query_servicios = open('search_most_used.sql', mode='r', encoding='utf-8')
query_clientes = open('get_clients.sql', mode='r', encoding='utf-8')

cursor.execute(query_clientes.read())
clientes = list(map(lambda cliente: cliente[0], cursor.fetchall()))


def get_client_n_most_used_services(client_code, n):
    cursor.execute(query_servicios.read() % (client_code, n))
    headers = list(map(lambda x: x[0], cursor.description))
    results = cursor.fetchall()
    return headers, results


def clean_values(value):
    aux = value.strip()

    if aux == 'ND':
        return 'None'

    if aux == 'SC':
        return 'None'

    if aux == 'N':
        return 'False'

    if aux == 'S':
        return 'True'

    if aux == 'PJ':
        return '1'

    if aux == 'PF':
        return '0'

    return aux


header, datos = get_client_n_most_used_services(90218, 5)
datos = list(map(lambda lista: list(map(lambda x: clean_values(str(x)), lista)), datos))

df = pd.DataFrame(data=datos, columns=header)


