from flask import Flask, request, render_template_string, jsonify
import os, json
from datetime import datetime

app = Flask(__name__)

# --- CONFIG DA SUA CLINICA ---
NOME_CLINICA = "SUA CLINICA AQUI"
CNPJ = "00.000.000/0001-00"
ENDERECO = "Rua Exemplo, 123 - Centro"
TELEFONE = "(47) 99999-9999"

DB_FILE = "documentos.json"

def load_db():
    if not os.path.exists(DB_FILE): return {}
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f: return json.load(f)
    except: return {}

def save_db(db):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)

def mascarar_cpf(cpf):
    cpf = ''.join(filter(str.isdigit, cpf))
    if len(cpf) != 11: return cpf
    return f"***.***.{cpf[6:9]}-{cpf[9:]}"

HTML_VALIDAR = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Validação - {{clinica}}</title>
<style>
body{font-family:Arial,sans-serif;background:#eef2f7;margin:0;padding:16px}
.card{max-width:700px;margin:30px auto;background:#fff;border-radius:14px;box-shadow:0 12px 30px rgba(0,0,0,.08);overflow:hidden}
.header{background:#0a3d62;color:#fff;padding:22px;text-align:center}
.header h1{margin:0;font-size:20px}
.header p{opacity:.8;font-size:12px;margin-top:6px}
.content{padding:24px}
.badge{display:inline-block;background:#e8f8f0;color:#0a7a42;border:1px solid #b6e9cc;padding:7px 14px;border-radius:20px;font-weight:700;font-size:13px}
.section{margin-top:22px}
.section h4{margin:0 0 10px;color:#0a3d62;font-size:14px;text-transform:uppercase;letter-spacing:.5px;border-left:4px solid #0a3d62;padding-left:8px}
.row{display:flex;justify-content:space-between;gap:10px;padding:10px 0;border-bottom:1px solid #eef1f4}
.label{color:#6b7a8f;font-size:13px}
.value{font-weight:600;color:#1a2a3a;font-size:14px;text-align:right}
.footer{background:#fafbfc;padding:16px;text-align:center;font-size:11px;color:#8a95a5;border-top:1px solid #eef1f4}
</style>
</head>
<body>
<div class="card">
  <div class="header"><h1>{{clinica}}</h1><p>{{cnpj}} - {{endereco}}</p></div>
  <div class="content">
  {% if doc %}
    <div style="text-align:center"><span class="badge">✓ DOCUMENTO AUTÊNTICO</span><p style="font-size:12px;color:#5a6b80;margin-top:10px">Código: <b>{{doc_id}}</b></p></div>
    
    <div class="section"><h4>Dados do Paciente</h4>
      <div class="row"><span class="label">Nome Completo</span><span class="value">{{doc.nome_paciente}}</span></div>
      <div class="row"><span class="label">CPF</span><span class="value">{{doc.cpf_masc}} ({{doc.cpf}})</span></div>
      <div class="row"><span class="label">Data de Nascimento</span><span class="value">{{doc.nascimento}}</span></div>
      <div class="row"><span class="label">Data do Atendimento</span><span class="value">{{doc.data_atendimento}}</span></div>
      <div class="row"><span class="label">Horário do Atendimento</span><span class="value">{{doc.horario}}</span></div>
      <div class="row"><span class="label">CID</span><span class="value">{{doc.cid}}</span></div>
    </div>

    <div class="section"><h4>Dados do Médico Responsável</h4>
      <div class="row"><span class="label">Nome Completo</span><span class="value">{{doc.nome_medico}}</span></div>
      <div class="row"><span class="label">CRM</span><span class="value">{{doc.crm}}</span></div>
    </div>

    <div class="section"><h4>Validação</h4>
      <div class="row"><span class="label">Tipo de Documento</span><span class="value">{{doc.tipo}}</span></div>
      <div class="row"><span class="label">Emitido em</span><span class="value">{{doc.emitido_em}}</span></div>
    </div>

    <div style="margin-top:18px;background:#f8fafc;padding:12px;border-radius:8px;font-size:11px;color:#5a6b80">Em caso de dúvida, contate {{clinica}} pelo telefone {{telefone}} informando o código.</div>

  {% else %}
    <div style="text-align:center;padding:20px"><span class="badge" style="background:#fdecea;color:#a33;border-color:#f5c6cb">✕ DOCUMENTO NÃO ENCONTRADO</span><p>Código <b>{{doc_id}}</b> não consta na base.</p></div>
  {% endif %}
  </div>
  <div class="footer">{{clinica}}<br>{{cnpj}} - {{telefone}}</div>
</div>
</body>
</html>
"""

HTML_ADMIN = """
<!DOCTYPE html>
<html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Admin - {{clinica}}</title>
<style>body{font-family:Arial;background:#f4f6f9;padding:16px}.box{max-width:560px;margin:20px auto;background:#fff;padding:22px;border-radius:12px}input,select{width:100%;padding:10px;margin:5px 0 10px;border:1px solid #ccc;border-radius:8px;box-sizing:border-box}button{width:100%;padding:12px;background:#0a3d62;color:#fff;border:0;border-radius:8px;font-weight:bold}label{font-size:12px;color:#5a6b80;font-weight:600}</style>
</head><body>
<div class="box">
<h3>Painel Admin - Registrar / Editar</h3>
<p style="font-size:12px;color:#6b7a8f">Se digitar um código que já existe, ele vai ATUALIZAR os dados (pra você editar nome, etc).</p>
<form method="POST">
<label>Código do Documento</label><input name="doc_id" placeholder="AT-2026-0001" required>
<label>Nome Completo do Paciente</label><input name="nome_paciente" required>
<label>CPF do Paciente</label><input name="cpf" placeholder="000.000.000-00" required>
<label>Data de Nascimento</label><input name="nascimento" type="date" required>
<label>Data do Atendimento</label><input name="data_atendimento" type="date" required>
<label>Horário do Atendimento</label><input name="horario" type="time" required>
<label>CID</label><input name="cid" placeholder="Ex: J06.9" required>
<label>Tipo</label><select name="tipo"><option>Atestado Médico</option><option>Declaração de Comparecimento</option><option>Atestado de Afastamento</option></select>
<hr style="margin:16px 0">
<label>Nome Completo do Médico</label><input name="nome_medico" placeholder="Dr. Fulano" required>
<label>CRM / UF</label><input name="crm" placeholder="CRM/SC 123456" required>
<button>Salvar / Atualizar</button>
</form>
{% if link %}<div style="margin-top:16px;background:#e8f8f0;padding:10px;border-radius:8px;font-size:13px">Salvo! Link de validação:<br><a href="{{link}}" target="_blank">{{link}}</a><br><br>Esse é o link que vai no QR Code.</div>{% endif %}
</div>
</body></html>
"""

@app.route("/")
def home(): return f"{NOME_CLINICA} - Sistema Online"

@app.route("/validar")
def validar():
    doc_id = request.args.get("doc","").strip()
    db = load_db()
    doc = db.get(doc_id)
    if doc:
        # cria versão mascarada pro front
        doc_view = doc.copy()
        doc_view["cpf_masc"] = mascarar_cpf(doc.get("cpf",""))
    else:
        doc_view = None
    return render_template_string(HTML_VALIDAR, clinica=NOME_CLINICA, cnpj=CNPJ, endereco=ENDERECO, telefone=TELEFONE, doc=doc_view or doc, doc_id=doc_id)

@app.route("/admin", methods=["GET","POST"])
def admin():
    link=None
    if request.method=="POST":
        db=load_db()
        doc_id=request.form["doc_id"].strip()
        db[doc_id]={
            "nome_paciente": request.form["nome_paciente"],
            "cpf": request.form["cpf"],
            "nascimento": request.form["nascimento"],
            "data_atendimento": request.form["data_atendimento"],
            "horario": request.form["horario"],
            "cid": request.form["cid"],
            "tipo": request.form["tipo"],
            "nome_medico": request.form["nome_medico"],
            "crm": request.form["crm"],
            "emitido_em": datetime.now().strftime("%d/%m/%Y %H:%M")
        }
        save_db(db)
        base = request.host_url.rstrip("/")
        link = f"{base}/validar?doc={doc_id}"
    return render_template_string(HTML_ADMIN, clinica=NOME_CLINICA, link=link)

@app.route("/api/registrar")
def api_registrar():
    # pra seu gerador de PDF registrar automaticamente
    doc_id=request.args.get("doc")
    if not doc_id: return jsonify({"erro":"doc obrigatório"}),400
    db=load_db()
    db[doc_id]={
        "nome_paciente": request.args.get("nome_paciente",""),
        "cpf": request.args.get("cpf",""),
        "nascimento": request.args.get("nascimento",""),
        "data_atendimento": request.args.get("data_atendimento",""),
        "horario": request.args.get("horario",""),
        "cid": request.args.get("cid",""),
        "tipo": request.args.get("tipo","Atestado Médico"),
        "nome_medico": request.args.get("nome_medico",""),
        "crm": request.args.get("crm",""),
        "emitido_em": datetime.now().strftime("%d/%m/%Y %H:%M")
    }
    save_db(db)
    return jsonify({"ok":True})

if __name__=="__main__":
    app.run(host="0.0.0.0",port=10000)
