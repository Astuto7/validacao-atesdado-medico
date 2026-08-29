from fastapi import FastAPI, Form, Request, Response
from fastapi.responses import HTMLResponse, RedirectResponse
import json, os, urllib.parse
from datetime import datetime

app = FastAPI()
ARQUIVO = "documentos.json"

# CONFIG
LOGO_URL = "https://i.postimg.cc/NMr6VDft/logo-png.jpg"
NOME_CLINICA = "UPA 24 HORAS - SENADOR CAMARÁ"
ENDEREÇO = "Av. de Santa Cruz, 6.486 - Senador Camará, Rio de Janeiro - RJ, 21830-264"
USUARIO = "admin"
SENHA = "medico2026"

def carregar():
    if os.path.exists(ARQUIVO):
        try:
            with open(ARQUIVO, "r", encoding="utf-8") as f: return json.load(f)
        except: return {}
    return {}
def salvar(d):
    with open(ARQUIVO, "w", encoding="utf-8") as f: json.dump(d, f, ensure_ascii=False, indent=2)

def check_auth(request: Request):
    return request.cookies.get("auth") == "logado"

@app.get("/validar", response_class=HTMLResponse)
async def validar(doc: str = ""):
    docs = carregar()
    codigo = doc.upper().strip()
    info = docs.get(codigo)
    if not info:
        return f"<html><body style='font-family:Arial;text-align:center;padding:50px'><h3>Código {doc} não encontrado</h3></body></html>"

    return f"""
    <html>
    <head><meta name="viewport" content="width=device-width, initial-scale=1"><title>Validação {codigo}</title>
    <style>
        body{{margin:0;background:#e9ecef;font-family:Arial, sans-serif}}
       .container{{max-width:720px;margin:0 auto;background:white;min-height:100vh;box-shadow:0 0 20px rgba(0,0,0,.08)}}
       .top{{text-align:center;padding:12px;color:#6c757d;font-size:13px;border-bottom:1px solid #eee}}
       .content{{padding:25px 30px}}
       .titulo{{color:#0f3554;font-weight:bold;font-size:14px;border-left:4px solid #0f3554;padding-left:10px;margin:28px 0 10px;text-transform:uppercase}}
       .linha{{display:flex;justify-content:space-between;padding:12px 0;border-bottom:1px solid #f1f1f1;font-size:14px}}
       .label{{color:#6c757d}}.valor{{font-weight:bold;color:#212529;text-align:right}}
       .footer{{text-align:center;padding:20px;font-size:11px;color:gray;background:#fafafa;border-top:1px solid #eee}}
       .aviso{{background:#f8f9fa;padding:12px;border-radius:6px;font-size:12px;color:#555;margin-top:20px}}
    </style>
    </head>
    <body>
    <div class="container">
        <div class="top">Código: <b>{codigo}</b></div>
        <div class="content">
            <div class="titulo">Dados do Paciente</div>
            <div class="linha"><span class="label">Nome Completo</span><span class="valor">{info.get('paciente','')}</span></div>
            <div class="linha"><span class="label">CPF</span><span class="valor">{info.get('cpf','')}</span></div>
            <div class="linha"><span class="label">Data de Nascimento</span><span class="valor">{info.get('nascimento','')}</span></div>
            <div class="linha"><span class="label">Data do Atendimento</span><span class="valor">{info.get('data','')}</span></div>
            <div class="linha"><span class="label">Horário do Atendimento</span><span class="valor">{info.get('horario','')}</span></div>
            <div class="linha"><span class="label">CID</span><span class="valor">{info.get('cid','')}</span></div>

            <div class="titulo">Dados do Médico Responsável</div>
            <div class="linha"><span class="label">Nome Completo</span><span class="valor">{info.get('medico','')}</span></div>
            <div class="linha"><span class="label">CRM</span><span class="valor">{info.get('crm','')}</span></div>

            <div class="titulo">Validação</div>
            <div class="linha"><span class="label">Tipo de Documento</span><span class="valor">{info.get('tipo','Declaração de Comparecimento')}</span></div>
            <div class="linha"><span class="label">Emitido em</span><span class="valor">{info.get('emitido','')}</span></div>

            <div class="aviso">Em caso de dúvida, contate {NOME_CLINICA} pelo telefone {TELEFONE} informando o código.</div>
        </div>
        <div class="footer">
            <img src="{LOGO_URL}" style="max-height:45px;opacity:.7"><br><br>
            {NOME_CLINICA}
        </div>
    </div>
    </body></html>
    """

# --- ADMIN COM SENHA ---

@app.get("/admin", response_class=HTMLResponse)
async def admin_page(request: Request):
    if not check_auth(request):
        return """
        <html><head><meta name="viewport" content="width=device-width, initial-scale=1"></head>
        <body style="font-family:Arial;background:#f0f2f5;display:flex;align-items:center;justify-content:center;height:100vh;margin:0">
        <form method="post" action="/login" style="background:white;padding:30px;border-radius:10px;box-shadow:0 4px 15px rgba(0,0,0,.1);width:300px">
        <h3 style="text-align:center;color:#0f3554">Login Admin</h3>
        <input name="user" placeholder="Usuário" required style="width:100%;padding:10px;margin:8px 0;box-sizing:border-box">
        <input name="pass" type="password" placeholder="Senha" required style="width:100%;padding:10px;margin:8px 0;box-sizing:border-box">
        <button style="width:100%;padding:12px;background:#0f3554;color:white;border:none;border-radius:6px;margin-top:10px">ENTRAR</button>
        </form></body></html>
        """

    docs = carregar()
    linhas = ""
    for cod, d in reversed(list(docs.items())):
        link = f"/validar?doc={cod}"
        linhas += f"<tr><td>{cod}</td><td>{d.get('paciente','')}</td><td>{d.get('data','')}</td><td><a href='{link}' target='_blank'>Ver</a></td></tr>"

    return f"""
    <html><head><meta name="viewport" content="width=device-width, initial-scale=1"></head>
    <body style="font-family:Arial;background:#f5f5f5;padding:20px"><div style="max-width:900px;margin:auto;background:white;padding:20px;border-radius:10px">
    <div style="display:flex;justify-content:space-between"><h2>Painel Admin</h2><a href="/logout">Sair</a></div>
    <form method="post" action="/admin-salvar">
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px">
    <input name="codigo" placeholder="Código ex: AB-78675" required style="padding:10px">
    <input name="paciente" placeholder="Nome Completo ex: JORGE" required style="padding:10px">
    <input name="cpf" placeholder="CPF ex: 123 (123)" style="padding:10px">
    <input name="nascimento" placeholder="Data Nascimento ex: 8888-11-11" style="padding:10px">
    <input name="data" placeholder="Data Atendimento ex: 2026-08-19" style="padding:10px">
    <input name="horario" placeholder="Horário ex: 12:33" style="padding:10px">
    <input name="cid" placeholder="CID ex: J76" style="padding:10px">
    <input name="tipo" placeholder="Tipo Doc" value="Declaração de Comparecimento" style="padding:10px">
    <input name="medico" placeholder="Médico ex: Dr. Silvão Abrao" style="padding:10px">
    <input name="crm" placeholder="CRM ex: CRM/RJ 1234" style="padding:10px">
    </div>
    <button style="width:100%;padding:12px;background:#0f3554;color:white;border:none;border-radius:6px;margin-top:15px">SALVAR DOCUMENTO</button>
    </form>
    <hr><table border="1" cellpadding="8" style="width:100%;border-collapse:collapse;margin-top:15px"><tr><th>Código</th><th>Paciente</th><th>Data</th><th>Link</th></tr>{linhas}</table>
    </div></body></html>
    """

@app.post("/login")
async def login(user: str = Form(...), pass_: str = Form(..., alias="pass")):
    if user == USUARIO and pass_ == SENHA:
        resp = RedirectResponse(url="/admin", status_code=302)
        resp.set_cookie(key="auth", value="logado", httponly=True, max_age=86400)
        return resp
    return HTMLResponse("<h3>Senha errada</h3><a href='/admin'>Voltar</a>", status_code=401)

@app.get("/logout")
async def logout():
    resp = RedirectResponse(url="/admin", status_code=302)
    resp.delete_cookie("auth")
    return resp

@app.post("/admin-salvar")
async def admin_salvar(request: Request, codigo: str = Form(...), paciente: str = Form(...), cpf: str = Form(""), nascimento: str = Form(""), data: str = Form(""), horario: str = Form(""), cid: str = Form(""), tipo: str = Form("Declaração de Comparecimento"), medico: str = Form(""), crm: str = Form("")):
    if not check_auth(request):
        return RedirectResponse(url="/admin", status_code=302)
    docs = carregar()
    cod = codigo.upper().strip()
    docs[cod] = {
        "codigo": cod, "paciente": paciente, "cpf": cpf, "nascimento": nascimento,
        "data": data, "horario": horario, "cid": cid, "tipo": tipo,
        "medico": medico, "crm": crm,
        "emitido": datetime.now().strftime("%d/%m/%Y %H:%M")
    }
    salvar(docs)
    return RedirectResponse(url="/admin", status_code=302)

@app.get("/", response_class=HTMLResponse)
async def home():
    return '<meta http-equiv="refresh" content="0; url=/admin">'
