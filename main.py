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

# >>> COLOCA SUA LOGO AQUI <<<
LOGO_URL = "https://i.postimg.cc/NMr6VDft/logo-png.jpg" # <-- TROCA ESSE LINK
NOME_CLINICA = "UPA SENADOR CAMARÁ"
CNPJ_ENDERECO = "Av. de Santa Cruz, 6.486 - Senador Camará, Rio de Janeiro - RJ, 21830-264"

def verificar_login(credentials: HTTPBasicCredentials = Depends(security)):
    if not (secrets.compare_digest(credentials.username, USUARIO_CORRETO) and secrets.compare_digest(credentials.password, SENHA_CORRETA)):
        raise HTTPException(status_code=401, detail="Login incorreto", headers={"WWW-Authenticate": "Basic"})
    return credentials.username

def carregar():
    if os.path.exists(ARQUIVO):
        try:
            with open(ARQUIVO, "r", encoding="utf-8") as f:
                return json.load(f)
        except: return {}
    return {}
def salvar(dados):
    with open(ARQUIVO, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)

@app.get("/validar", response_class=HTMLResponse)
async def validar(doc: str = ""):
    docs = carregar()
    info = docs.get(doc.upper().strip())
    if not info:
        return f"<html><body style='font-family:Arial;text-align:center;padding:50px'><h2 style='color:red'>Documento não encontrado</h2><p>{doc}</p></body></html>"

    # Logo no topo
    logo_html = f"<img src='{LOGO_URL}' style='max-height:80px;max-width:220px;background:white;padding:8px;border-radius:8px'>" if "http" in LOGO_URL else ""

    return f"""
    <html><head><meta name="viewport" content="width=device-width, initial-scale=1"><style>body{{font-family:Arial;background:#f4f6f9;margin:0}}.topo{{background:#0f3554;color:white;padding:20px;text-align:center}}.card{{max-width:650px;margin:20px auto;background:white;border-radius:12px;overflow:hidden;box-shadow:0 4px 12px rgba(0,0,0,0.1)}}</style></head>
    <body>
      <div class="card">
        <div class="topo">
          {logo_html}
          <h2 style="margin:10px 0 5px 0">{NOME_CLINICA}</h2>
          <p style="font-size:12px;margin:0;opacity:0.8">{CNPJ_ENDERECO}</p>
        </div>
        <div style="padding:25px">
          <div style="text-align:center"><span style="background:#e6f4ea;color:#1b5e20;padding:8px 16px;border-radius:20px;font-weight:bold;font-size:13px">✓ DOCUMENTO AUTÊNTICO</span><p style="font-size:12px;color:gray">Código: {info['codigo']}</p></div>
          <h4 style="color:#0f3554;border-left:4px solid #0f3554;padding-left:8px">DADOS DO PACIENTE</h4>
          <p style="display:flex;justify-content:space-between;border-bottom:1px solid #eee;padding:8px 0"><span style="color:#666">Nome Completo</span><b>{info.get('paciente','')}</b></p>
          <p style="display:flex;justify-content:space-between;border-bottom:1px solid #eee;padding:8px 0"><span style="color:#666">CPF</span><b>{info.get('cpf','')}</b></p>
          <p style="display:flex;justify-content:space-between;border-bottom:1px solid #eee;padding:8px 0"><span style="color:#666">Data de Nascimento</span><b>{info.get('nascimento','')}</b></p>
          <p style="display:flex;justify-content:space-between;border-bottom:1px solid #eee;padding:8px 0"><span style="color:#666">Data do Atendimento</span><b>{info.get('data','')}</b></p>
          <p style="display:flex;justify-content:space-between;border-bottom:1px solid #eee;padding:8px 0"><span style="color:#666">Horário do Atendimento</span><b>{info.get('horario','')}</b></p>
          <p style="display:flex;justify-content:space-between;border-bottom:1px solid #eee;padding:8px 0"><span style="color:#666">CID</span><b>{info.get('cid','')}</b></p>
          <h4 style="color:#0f3554;border-left:4px solid #0f3554;padding-left:8px;margin-top:25px">DADOS DO MÉDICO RESPONSÁVEL</h4>
          <p style="display:flex;justify-content:space-between;border-bottom:1px solid #eee;padding:8px 0"><span style="color:#666">Nome Completo</span><b>{info.get('medico','')}</b></p>
          <p style="display:flex;justify-content:space-between;padding:8px 0"><span style="color:#666">CRM</span><b>{info.get('crm','')}</b></p>
          <div style="text-align:center;margin-top:20px"><img src="https://api.qrserver.com/v1/create-qr-code/?size=120x120&data=https://validacao-atesdado-medico.onrender.com/validar?doc={urllib.parse.quote(info['codigo'])}" /></div>
        </div>
      </div>
    </body></html>"""

@app.get("/admin", response_class=HTMLResponse)
async def admin_form(usuario: str = Depends(verificar_login)):
    docs = carregar()
    linhas = ""
    for codigo, d in reversed(list(docs.items())):
        link = f"https://validacao-atesdado-medico.onrender.com/validar?doc={codigo}"
        qr_api = f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data={urllib.parse.quote(link)}"
        linhas += f"<tr><td>{codigo}</td><td>{d.get('paciente','')}</td><td><a href='{link}' target='_blank'>Abrir</a></td><td><img src='{qr_api}' width='80'></td></tr>"
    return f"""<html><head><meta name="viewport" content="width=device-width, initial-scale=1"></head><body style="font-family:Arial;padding:20px;background:#f9f9f9"><div style="max-width:900px;margin:auto;background:white;padding:20px;border-radius:10px"><h2>Painel - {usuario}</h2><form method="post" action="/admin"><input name="codigo" placeholder="Código ex: AB-78675" required style="width:100%;padding:8px;margin:5px 0"><br><input name="paciente" placeholder="Nome" required style="width:100%;padding:8px;margin:5px 0"><br><input name="cpf" placeholder="CPF" style="width:100%;padding:8px;margin:5px 0"><br><input name="nascimento" placeholder="Nascimento" style="width:100%;padding:8px;margin:5px 0"><br><input name="data" placeholder="Data Atendimento" style="width:100%;padding:8px;margin:5px 0"><br><input name="horario" placeholder="Horário" style="width:100%;padding:8px;margin:5px 0"><br><input name="cid" placeholder="CID" style="width:100%;padding:8px;margin:5px 0"><br><input name="medico" placeholder="Médico" style="width:100%;padding:8px;margin:5px 0"><br><input name="crm" placeholder="CRM" style="width:100%;padding:8px;margin:5px 0"><br><button type="submit" style="width:100%;padding:12px;background:#1976d2;color:white;border:none;border-radius:6px">SALVAR</button></form><hr><table border="1" cellpadding="8" style="width:100%;border-collapse:collapse"><tr><th>Código</th><th>Paciente</th><th>Link</th><th>QR</th></tr>{linhas}</table></div></body></html>"""

@app.post("/admin", response_class=HTMLResponse)
async def admin_save(codigo: str = Form(...), paciente: str = Form(...), cpf: str = Form(""), nascimento: str = Form(""), data: str = Form(""), horario: str = Form(""), cid: str = Form(""), medico: str = Form(""), crm: str = Form(""), usuario: str = Depends(verificar_login)):
    docs = carregar()
    cod = codigo.upper().strip()
    docs[cod] = {"codigo": cod, "paciente": paciente, "cpf": cpf, "nascimento": nascimento, "data": data, "horario": horario, "cid": cid, "medico": medico, "crm": crm, "criado_em": datetime.now().isoformat()}
    salvar(docs)
    link = f"https://validacao-atesdado-medico.onrender.com/validar?doc={cod}"
    return f"<html><body style='text-align:center;padding:30px;font-family:Arial'><h2>✅ Salvo {cod}</h2><a href='{link}' target='_blank'>{link}</a><br><br><a href='/admin'>Voltar</a></body></html>"

@app.get("/", response_class=HTMLResponse)
async def home(): return '<meta http-equiv="refresh" content="0; url=/admin">'
