from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
import json, os
from datetime import datetime

app = FastAPI()
ARQUIVO = "documentos.json"

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
    try:
        docs = carregar()
        codigo = doc.upper().strip()
        info = docs.get(codigo)
        if not info:
            return f"<html><body style='font-family:Arial;text-align:center;padding:50px'><h3>Código {doc} não encontrado ou inválido</h3><p>Verifique o código digitado.</p></body></html>"

        # corrige docs antigos que não tem esses campos
        paciente = info.get('paciente','-')
        cpf = info.get('cpf','-')
        nascimento = info.get('nascimento','-')
        data_at = info.get('data','-')
        horario = info.get('horario','-')
        cid = info.get('cid','-')
        medico = info.get('medico','-')
        crm = info.get('crm','-')
        tipo = info.get('tipo','Declaração de Comparecimento')
        emitido = info.get('emitido', datetime.now().strftime("%d/%m/%Y %H:%M"))

        return f"""
        <html><head><meta name="viewport" content="width=device-width, initial-scale=1"><title>Validação {codigo}</title>
        <style>
            body{{margin:0;background:#e9ecef;font-family:Arial}}.container{{max-width:720px;margin:0 auto;background:white;min-height:100vh}}
           .top{{text-align:center;padding:12px;color:#6c757d;font-size:13px;border-bottom:1px solid #eee}}
           .content{{padding:25px 30px}}.titulo{{color:#0f3554;font-weight:bold;font-size:14px;border-left:4px solid #0f3554;padding-left:10px;margin:28px 0 10px;text-transform:uppercase}}
           .linha{{display:flex;justify-content:space-between;padding:12px 0;border-bottom:1px solid #f1f1f1;font-size:14px}}
           .label{{color:#6c757d}}.valor{{font-weight:bold;color:#212529;text-align:right}}.aviso{{background:#f8f9fa;padding:12px;border-radius:6px;font-size:12px;color:#555;margin-top:20px}}.footer{{text-align:center;padding:20px;font-size:11px;color:gray;background:#fafafa;border-top:1px solid #eee}}
        </style></head><body><div class="container"><div class="top">Código: <b>{codigo}</b></div>
        <div class="content">
            <div class="titulo">Dados do Paciente</div>
            <div class="linha"><span class="label">Nome Completo</span><span class="valor">{paciente}</span></div>
            <div class="linha"><span class="label">CPF</span><span class="valor">{cpf}</span></div>
            <div class="linha"><span class="label">Data de Nascimento</span><span class="valor">{nascimento}</span></div>
            <div class="linha"><span class="label">Data do Atendimento</span><span class="valor">{data_at}</span></div>
            <div class="linha"><span class="label">Horário do Atendimento</span><span class="valor">{horario}</span></div>
            <div class="linha"><span class="label">CID</span><span class="valor">{cid}</span></div>
            <div class="titulo">Dados do Médico Responsável</div>
            <div class="linha"><span class="label">Nome Completo</span><span class="valor">{medico}</span></div>
            <div class="linha"><span class="label">CRM</span><span class="valor">{crm}</span></div>
            <div class="titulo">Validação</div>
            <div class="linha"><span class="label">Tipo de Documento</span><span class="valor">{tipo}</span></div>
            <div class="linha"><span class="label">Emitido em</span><span class="valor">{emitido}</span></div>
            <div class="aviso">Em caso de dúvida, contate {NOME_CLINICA} pelo telefone {TELEFONE} informando o código.</div>
        </div><div class="footer"><img src="{LOGO_URL}" style="max-height:40px;opacity:.8"><br><br>{NOME_CLINICA}</div></div></body></html>
        """
    except Exception as e:
        return HTMLResponse(f"<h3>Erro interno: {e}</h3>", status_code=500)

@app.get("/admin", response_class=HTMLResponse)
async def admin_page(request: Request):
    if not check_auth(request):
        return """
        <html><head><meta name="viewport" content="width=device-width, initial-scale=1"></head>
        <body style="font-family:Arial;background:#f0f2f5;display:flex;align-items:center;justify-content:center;height:100vh;margin:0">
        <form method="post" action="/login" style="background:white;padding:30px;border-radius:10px;box-shadow:0 4px 15px rgba(0,0,0,.1);width:300px">
        <h3 style="text-align:center;color:#0f3554">Login Admin</h3>
        <input name="user" placeholder="Usuário" required style="width:100%;padding:10px;margin:8px 0;box-sizing:border-box">
        <input name="senha" type="password" placeholder="Senha" required style="width:100%;padding:10px;margin:8px 0;box-sizing:border-box">
        <button style="width:100%;padding:12px;background:#0f3554;color:white;border:none;border-radius:6px;margin-top:10px">ENTRAR</button>
        </form></body></html>
        """
    docs = carregar()
    linhas = ""
    for cod, d in reversed(list(docs.items())):
        link = f"https://validacao-atesdado-medico.onrender.com/validar?doc={cod}"
        linhas += f"<tr><td>{cod}</td><td>{d.get('paciente','')}</td><td>{d.get('data','')}</td><td><a href='{link}' target='_blank'>Ver</a></td></tr>"
    return f"""
    <html><head><meta name="viewport" content="width=device-width, initial-scale=1"></head>
    <body style="font-family:Arial;background:#f5f5f5;padding:20px"><div style="max-width:900px;margin:auto;background:white;padding:20px;border-radius:10px">
    <div style="display:flex;justify-content:space-between"><h2>Painel Admin</h2><a href="/logout">Sair</a></div>
    <form method="post" action="/admin-salvar">
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px">
    <input name="codigo" placeholder="Código ex: JB-93495" required style="padding:10px">
    <input name="paciente" placeholder="Nome ex: JORGE" required style="padding:10px">
    <input name="cpf" placeholder="CPF" style="padding:10px">
    <input name="nascimento" placeholder="Nascimento" style="padding:10px">
    <input name="data" placeholder="Data Atend." style="padding:10px">
    <input name="horario" placeholder="Horário" style="padding:10px">
    <input name="cid" placeholder="CID" style="padding:10px">
    <input name="medico" placeholder="Médico" style="padding:10px">
    <input name="crm" placeholder="CRM" style="padding:10px">
    </div>
    <button style="width:100%;padding:12px;background:#0f3554;color:white;border:none;border-radius:6px;margin-top:15px">SALVAR</button>
    </form><hr><table border="1" cellpadding="8" style="width:100%;border-collapse:collapse;margin-top:15px"><tr><th>Código</th><th>Paciente</th><th>Data</th><th>Link</th></tr>{linhas}</table></div></body></html>
    """

@app.post("/login")
async def login(user: str = Form(...), senha: str = Form(...)):
    if user == USUARIO and senha == SENHA:
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
async def admin_salvar(request: Request, codigo: str = Form(...), paciente: str = Form(...), cpf: str = Form(""), nascimento: str = Form(""), data: str = Form(""), horario: str = Form(""), cid: str = Form(""), medico: str = Form(""), crm: str = Form("")):
    if not check_auth(request):
        return RedirectResponse(url="/admin", status_code=302)
    docs = carregar()
    cod = codigo.upper().strip()
    docs[cod] = {"codigo": cod, "paciente": paciente, "cpf": cpf, "nascimento": nascimento, "data": data, "horario": horario, "cid": cid, "medico": medico, "crm": crm, "tipo": "Declaração de Comparecimento", "emitido": datetime.now().strftime("%d/%m/%Y %H:%M")}
    salvar(docs)
    return RedirectResponse(url="/admin", status_code=302)

@app.get("/", response_class=HTMLResponse)
async def home(): return '<meta http-equiv="refresh" content="0; url=/admin">'
