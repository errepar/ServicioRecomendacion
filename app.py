from flask import Flask, jsonify
from keras.models import load_model
import numpy as np

app = Flask(__name__)
clasificador_tema = load_model('./dls/models/recomendador-errepar-tema_4/model.h5')


@app.route('/')
def hello_world():
    # Hacer que lleguen 10 parámetros (uno por cada feature del vector de entrada)
    entrada = np.array([[0, 0, 0, 0, 0, 0, 0, 0, 0, 0]])

    # Ranking
    prediccion = clasificador_tema.predict(entrada)

    return jsonify(prediccion=str(prediccion))


if __name__ == '__main__':
    app.run()

