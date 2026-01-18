from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os

app = Flask(__name__)
CORS(app)

JS_FILE_PATH = 'date_comenzi.js'

def citeste_comenzi():
    if not os.path.exists(JS_FILE_PATH): return []
    try:
        with open(JS_FILE_PATH, 'r', encoding='utf-8') as f:
            content = f.read()
            json_str = content.split('=', 1)[1].strip().rstrip(';')
            return json.loads(json_str)
    except: return []

def salveaza_comenzi(comenzi):
    with open(JS_FILE_PATH, 'w', encoding='utf-8') as f:
        f.write(f"window.date_comenzi = {json.dumps(comenzi, indent=4, ensure_ascii=False)};")

@app.route('/comanda_gata', methods=['GET'])
def comanda_gata():
    ora_id = request.args.get('id')
    titlu_comanda = request.args.get('nume')

    comenzi = citeste_comenzi()
    comanda_gasita = next((c for c in comenzi if c.get('data') == ora_id), None)

    if comanda_gasita:
        # Cream lista de produse pentru Popup
        lista_nume = [p['nume'] for p in comanda_gasita.get('produse', [])]
        string_produse = ", ".join(lista_nume)

        # Stergem comanda
        comenzi_noi = [c for c in comenzi if c.get('data') != ora_id]
        salveaza_comenzi(comenzi_noi)

        # Scriere notificare: GATA|Titlu|Produse
        with open('notificare_client.txt', 'w', encoding='utf-8') as f:
            f.write(f"GATA|{titlu_comanda}|{string_produse}")

    return jsonify({"status": "success"})

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=False)
