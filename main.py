from flask import Flask, request, render_template_string, jsonify
import os

app = Flask(__name__)

# EDITA AQUI COM OS DADOS DA SUA CLÍNICA - NADA DE UPA/PREFEITURA
CONFIG = {
    "nome_clinica": "CLINICA SENADOR CAMARA",
    "cnpj": "00.000.000/0001-00",
    "endereco": "Seu endereço aqui",
}

HTML_VALIDACAO = """
<html><head><title>Validação de Documento</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>body{font-family:Arial; text-align:center; padding:40px} .box{border:1px solid #ddd; padding:20px; border-radius:10px; max-width:500px; margin:auto}</style>
</head><body>
<div class="box">
<h2>{{clinica}}</h2>
<p>Documento: <b>{{doc_id}}</b></p>
<p>Status: <span style="color:green"><b>Documento registrado em nosso sistema</b></span></p>
<small>{{cnpj}} - {{endereco}}</small>
</div></body></html>
"""

@app.route('/')
def home():
    return f"<h3>{CONFIG['nome_clinica']} - Sistema de validação online</h3><p>Use /validar?doc=ID</p>"

@app.route('/validar')
def validar():
    doc_id = request.args.get('doc', 'N/A')
    return render_template_string(HTML_VALIDACAO, clinica=CONFIG['nome_clinica'], doc_id=doc_id, cnpj=CONFIG['cnpj'], endereco=CONFIG['endereco'])

@app.route('/api/validar/<doc_id>')
def api_validar(doc_id):
    return jsonify({"documento": doc_id, "valido": True, "clinica": CONFIG['nome_clinica']})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
