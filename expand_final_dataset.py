import csv
import pandas as pd

csv_file = open('dataset_intermedio.csv', mode='r')
csv_reader = csv.reader(csv_file, delimiter=';')
csv_rows = list(csv_reader)

# Elimino el header del CSV
header = csv_rows[0]

del csv_rows[0]

posicion_cantidad_replicaciones = 13

final_csv = []
# for row in csv_rows:
for i in range(0, len(csv_rows)):
    print('Procesando fila {0} de {1}'.format(i, len(csv_rows)))

    row = csv_rows[i]

    # Agrego UNO por las filas que no tienen replicación
    cantidad_replicaciones = round(float(row[posicion_cantidad_replicaciones]) + 1)

    # Replico las filas según la cantidad especificada en el último campo del CSV
    for j in range(0, cantidad_replicaciones):
        final_csv.append(row)

df = pd.DataFrame(data=final_csv, columns=header)
del df['CantidadReplicaciones']
del df['Proporcion']
del df['TotalVisitas']
del df['CantidadVisitas']
df.to_csv('dataset_final.csv', index=False, sep=',')
