from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
import json, os, urllib.parse
from datetime import datetime

app = FastAPI()
ARQUIVO = "documentos.json"

LOGO_URL = "https://i.postimg.cc/NMr6VDft/logo-png.jpg"
NOME_CLINICA = "UPA 24 HORAS - Senador Camará"

def carregar():
    if os.path.exists(ARQUIVO):
        try:
            with open(ARQUIVO, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}
    return {}

def salvar(d):
    with open(ARQUIVO, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=2)

@app.get("/validar", response_class=HTMLResponse)
async def validar(doc: str = ""):
    docs = carregar()
    info = docs.get(doc.upper().strip())
    if not info:
        return f"<html><body style='font-family:Arial;text-align:center;padding:50px'><h2 style='color:red'>Documento {doc} nao encontrado</h2></body></html>"

    logo = f"<img src='{LOGO_URL}' style='max-height:70px;background:white;padding:6px;border-radius:8px;margin-bottom:8px'><br>" if LOGO_URL else ""

    return f"""
    <html><head><meta name="viewport" content="width=device-width, initial-scale=1">
    <style>body{{margin:0;font-family:Arial;background:#f0f2f5}}.top{{background:#0f3554;color:white;padding:20px;text-align:center}}.card{{max-width:620px;margin:20px auto;background:white;border-radius:12px;overflow:hidden;box-shadow:0 4px 15px rgba(0,0,0,.1)}}.content{{padding:20px}}.row{{display:flex;justify-content:space-between;border-bottom:1px solid #eee;padding:10px 0}}.label{{color:#666}} </style>
    </head><body><div class="card"><div class="top">{logo}<h2 style="margin:5px 0">{NOME_CLINICA}</h2></div>
    <div class="content">
    <div style="text-align:center;margin-bottom:15px"><span style="background:#e6f4ea;color:#1b5e20;padding:6px 14px;border-radius:20px;font-weight:bold">✓ DOCUMENTO AUTÊNTICO</span><br><small style="color:gray">Código: {info.get('codigo')}</small></div>
    <h4 style="color:#0f3554;border-left:4px solid #0f3554;padding-left:8px">DADOS DO PACIENTE</h4>
    <div class="row"><span class="label">Nome Completo</span><b>{info.get('paciente','')}</b></div>
    <div class="row"><span class="label">CPF</span><b>{info.get('cpf','')}</b></div>
    <div class="row"><span class="label">Nascimento</span><b>{info.get('nascimento','')}</b></div>
    <div class="row"><span class="label">Data Atendimento</span><b>{info.get('data','')}</b></div>
    <div class="row"><span class="label">Horário</span><b>{info.get('horario','')}</b></div>
    <div class="row"><span class="label">CID</span><b>{info.get('cid','')}</b></div>
    <h4 style="color:#0f3554;border-left:4px solid #0f3554;padding-left:8px;margin-top:20px">MÉDICO RESPONSÁVEL</h4>
    <div class="row"><span class="label">Nome</span><b>{info.get('medico','')}</b></div>
    <div class="row"><span class="label">CRM</span><b>{info.get('crm','')}</b></div>
    <div style="text-align:center;margin-top:20px"><img src="https://api.qrserver.com/v1/create-qr-code/?size=130x130&data=https://validacao-atesdado-medico.onrender.com/validar?doc={urllib.parse.quote(info.get('codigo',''))}" /></div>
    </div></div></body></html>
    """

@app.get("/admin", response_class=HTMLResponse)
async def admin_form():
    docs = carregar()
    linhas = ""
    for cod, d in reversed(list(docs.items())):
        link = f"https://validacao-atesdado-medico.onrender.com/validar?doc={cod}"
        linhas += f"<tr><td>{cod}</td><td>{d.get('paciente','')}</td><td><a href='{link}' target='_blank'>Ver</a></td></tr>"
    return f"""
    <html><head><meta name="viewport" content="width=device-width, initial-scale=1"></head>
    <body style="font-family:Arial;background:#f5f5f5;padding:20px"><div style="max-width:800px;margin:auto;background:white;padding:20px;border-radius:10px">
    <h2>Admin - Painel</h2>
    <form method="post" action="/admin">
    <input name="codigo" placeholder="Código ex: LT-49395" required style="width:100%;padding:10px;margin:5px 0">
    <input name="paciente" placeholder="Paciente" required style="width:100%;padding:10px;margin:5px 0">
    <input name="cpf" placeholder="CPF" style="width:100%;padding:10px;margin:5px 0">
    <input name="nascimento" placeholder="Nascimento" style="width:100%;padding:10px;margin:5px 0">
    <input name="data" placeholder="Data Atendimento" style="width:100%;padding:10px;margin:5px 0">
    <input name="horario" placeholder="Horário" style="width:100%;padding:10px;margin:5px 0">
    <input name="cid" placeholder="CID" style="width:100%;padding:10px;margin:5px 0">
    <input name="medico" placeholder="Médico" style="width:100%;padding:10px;margin:5px 0">
    <input name="crm" placeholder="CRM" style="width:100%;padding:10px;margin:5px 0">
    <button style="width:100%;padding:12px;background:#0f3554;color:white;border:none;border-radius:6px;margin-top:10px">SALVAR</button>
    </form><hr><table border="1" cellpadding="8" style="width:100%;border-collapse:collapse"><tr><th>Código</th><th>Paciente</th><th>Link</th></tr>{linhas}</table></div></body></html>
    """

@app.post("/admin", response_class=HTMLResponse)
async def admin_save(codigo: str = Form(...), paciente: str = Form(...), cpf: str = Form(""), nascimento: str = Form(""), data: str = Form(""), horario: str = Form(""), cid: str = Form(""), medico: str = Form(""), crm: str = Form("")):
    docs = carregar()
    cod = codigo.upper().strip()
    docs[cod] = {"codigo": cod, "paciente": paciente, "cpf": cpf, "nascimento": nascimento, "data": data, "horario": horario, "cid": cid, "medico": medico, "crm": crm, "criado": datetime.now().isoformat()}
    salvar(docs)
    link = f"https://validacao-atesdado-medico.onrender.com/validar?doc={cod}"
    return f"<body style='font-family:Arial;text-align:center;padding:30px'><h2 style='color:green'>Salvo {cod}</h2><p><a href='{link}' target='_blank'>{link}</a></p><br><a href='/admin'>Voltar</a></body>"

@app.get("/", response_class=HTMLResponse)
async def home():
    return '<meta http-equiv="refresh" content="0; url=/admin">'
