from fastapi import FastAPI, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import json, os
from datetime import datetime
import urllib.parse
import secrets

app = FastAPI()
ARQUIVO = "documentos.json"
security = HTTPBasic()

USUARIO_CORRETO = "admin"
SENHA_CORRETA = "medico2026"

LOGO_URL = "" # deixa vazio por enquanto, depois colocamos sua logo
NOME_CLINICA = "UPA SENADOR CAMARÁ"
CNPJ_ENDERECO = "Av. de Santa Cruz, 6.486 - Senador Camará, Rio de Janeiro - RJ, 21830-264"

def verificar_login(credentials: HTTPBasicCredentials = Depends(security)):
    ok_user = secrets.compare_digest(credentials.username, USUARIO_CORRETO)
    ok_pass = secrets.compare_digest(credentials.password, SENHA_CORRETA)
    if not (ok_user and ok_pass):
        raise HTTPException(status_code=401, detail="Unauthorized", headers={"WWW-Authenticate": "Basic"})
    return credentials.username

def carregar():
    if os.path.exists(ARQUIVO):
        try:
            with open(ARQUIVO, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}
    return {}

def salvar(dados):
    with open(ARQUIVO, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)

@app.get("/validar", response_class=HTMLResponse)
async def validar(doc: str = ""):
    docs = carregar()
    info = docs.get(doc.upper().strip())
    if not info:
        return f"<h2>Documento {doc} nao encontrado</h2>"
    return f"""
    <html><head><meta name="viewport" content="width=device-width, initial-scale=1"></head>
    <body style="font-family:Arial;background:#f4f6f9;padding:20px">
    <div style="max-width:600px;margin:auto;background:white;padding:25px;border-radius:12px">
        <h2 style="color:#0f3554;text-align:center">{NOME_CLINICA}</h2>
        <p style="text-align:center;font-size:12px">{CNPJ_ENDERECO}</p>
        <h3 style="color:green;text-align:center">✅ DOCUMENTO AUTÊNTICO</h3>
        <p><b>Código:</b> {info.get('codigo')}</p>
        <p><b>Paciente:</b> {info.get('paciente')}</p>
        <p><b>CPF:</b> {info.get('cpf')}</p>
        <p><b>Nascimento:</b> {info.get('nascimento')}</p>
        <p><b>Data:</b> {info.get('data')}</p>
        <p><b>Horário:</b> {info.get('horario')}</p>
        <p><b>CID:</b> {info.get('cid')}</p>
        <p><b>Médico:</b> {info.get('medico')}</p>
        <p><b>CRM:</b> {info.get('crm')}</p>
    </div>
    </body></html>
    """

@app.get("/admin", response_class=HTMLResponse)
async def admin_form(usuario: str = Depends(verificar_login)):
    docs = carregar()
    return f"<html><body><h2>OK Logado como {usuario} - Total {len(docs)} docs</h2><form method='post' action='/admin'><input name='codigo' placeholder='Codigo' required><br><input name='paciente' placeholder='Paciente' required><br><button type='submit'>Salvar</button></form></body></html>"

@app.post("/admin", response_class=HTMLResponse)
async def admin_save(codigo: str = Form(...), paciente: str = Form(...), cpf: str = Form(""), nascimento: str = Form(""), data: str = Form(""), horario: str = Form(""), cid: str = Form(""), medico: str = Form(""), crm: str = Form(""), usuario: str = Depends(verificar_login)):
    docs = carregar()
    cod = codigo.upper().strip()
    docs[cod] = {"codigo": cod, "paciente": paciente, "cpf": cpf, "nascimento": nascimento, "data": data, "horario": horario, "cid": cid, "medico": medico, "crm": crm}
    salvar(docs)
    return f"<h2>Salvo {cod}</h2><a href='/admin'>Voltar</a>"

@app.get("/", response_class=HTMLResponse)
async def home():
    return '<meta http-equiv="refresh" content="0; url=/admin">'
