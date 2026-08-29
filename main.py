from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
import json, os, hashlib
from datetime import datetime

app = FastAPI()
ARQUIVO = "documentos.json"

LOGO_URL = "https://i.postimg.cc/NMr6VDft/logo-png.jpg"
NOME_CLINICA = "UPA 24 HORAS - SENADOR CAMARÁ"
ENDERECO = "Av. de Santa Cruz, 6.486 - Senador Camará, Rio de Janeiro - RJ, 21830-264"
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

def check_auth(r: Request): return r.cookies.get("auth") == "logado"

@app.get("/validar", response_class=HTMLResponse)
async def validar(doc: str = ""):
    docs = carregar()
    codigo = doc.upper().strip()
    info = docs.get(codigo)
    if not info:
        return f"<html><body style='font-family:Arial;background:#f4f6f9;display:flex;justify-content:center;align-items:center;height:100vh;margin:0'><div style='background:white;padding:40px;border-radius:12px;text-align:center'><h2 style='color:#c62828'>Documento Não Encontrado</h2><p>Código <b>{doc}</b> não consta.</p></div></body></html>"

    hash_valid = hashlib.md5(f"{codigo}{info.get('cpf','')}{info.get('data','')}".encode()).hexdigest().upper()[:16]

    return f"""
    <html><head><meta name="viewport" content="width=device-width, initial-scale=1"><title>Validação - {codigo}</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
    <style>
        *{{font-family:'Inter',Arial}} body{{margin:0;background:#eef2f7}}
    .page{{max-width:800px;margin:20px auto;background:white;border-radius:16px;overflow:hidden;box-shadow:0 10px 40px rgba(0,0,0,.12)}}
    .header{{background:linear-gradient(135deg,#0f3554 0%,#163e6b 100%);color:white;padding:22px 30px;display:flex;justify-content:space-between;align-items:center}}
    .header img{{max-height:52px;background:white;padding:6px 10px;border-radius:8px}}
    .content{{padding:0 30px 30px}}
    .status-box{{background:#e8f5e9;border:1px solid #a5d6a7;border-radius:12px;padding:16px 20px;display:flex;justify-content:space-between;align-items:center;margin:20px 0}}
    .grid{{display:grid;grid-template-columns:1fr 1fr;gap:0}}
    .field{{padding:14px 0;border-bottom:1px solid #f0f0f0;display:flex;flex-direction:column}}
    .field.full{{grid-column:1 / -1}}.field.l{{font-size:11px;color:#8a8a8a;text-transform:uppercase;letter-spacing:.5px;margin-bottom:4px}}.field.v{{font-size:14px;font-weight:600;color:#1a1a1a}}
    .section-title{{font-size:13px;font-weight:700;color:#0f3554;text-transform:uppercase;letter-spacing:1px;margin:30px 0 10px;padding-left:12px;border-left:4px solid #0f3554}}
    .qr-box{{background:#fafafa;border:1px dashed #ddd;border-radius:12px;padding:20px;text-align:center;margin-top:20px}}
    .footer{{background:#f8f9fa;padding:20px 30px;font-size:11px;color:#888;border-top:1px solid #eee;text-align:center}}
    .hash{{font-family:monospace;background:#eee;padding:4px 8px;border-radius:4px;font-size:12px}}
    </style></head>
    <body><div class="page">
        <div class="header">
            <div style="display:flex;align-items:center;gap:14px"><img src="{LOGO_URL}"><div><div style="font-weight:700;font-size:15px">{NOME_CLINICA}</div><div style="font-size:11px;opacity:.85;margin-top:3px">{ENDERECO}</div></div></div>
            <div><span style="background:white;color:#0f3554;padding:6px 14px;border-radius:20px;font-size:12px;font-weight:700">DOCUMENTO OFICIAL</span></div>
        </div>
        <div class="content">
            <div class="status-box">
                <div><div style="font-weight:700;color:#2e7d32;font-size:15px">✓ DOCUMENTO AUTENTICADO COM SUCESSO</div><div style="font-size:12px;color:#555;margin-top:4px">Este documento consta em nossa base oficial.</div></div>
                <div style="text-align:right"><div style="font-size:11px;color:#888">CÓDIGO</div><div style="font-weight:800;font-size:16px;color:#0f3554">{codigo}</div></div>
            </div>

            <div class="section-title">1. Identificação do Paciente</div>
            <div class="grid">
                <div class="field full"><span class="l">Nome Completo</span><span class="v">{info.get('paciente','-')}</span></div>
                <div class="field"><span class="l">CPF</span><span class="v">{info.get('cpf','-')}</span></div>
                <div class="field"><span class="l">RG</span><span class="v">{info.get('rg','-')}</span></div>
                <div class="field"><span class="l">Data de Nascimento</span><span class="v">{info.get('nascimento','-')} ({info.get('idade','-')} anos)</span></div>
                <div class="field"><span class="l">Sexo</span><span class="v">{info.get('sexo','-')}</span></div>
            </div>

            <div class="section-title">2. Dados do Atendimento</div>
            <div class="grid">
                <div class="field"><span class="l">Data do Atendimento</span><span class="v">{info.get('data','-')}</span></div>
                <div class="field"><span class="l">Horário</span><span class="v">{info.get('horario','-')}</span></div>
                <div class="field"><span class="l">Unidade</span><span class="v">{info.get('unidade', NOME_CLINICA)}</span></div>
                <div class="field"><span class="l">Tipo de Documento</span><span class="v">{info.get('tipo','Atestado Médico')}</span></div>
                <div class="field"><span class="l">CID-10</span><span class="v">{info.get('cid','-')} - {info.get('cid_desc','')}</span></div>
                <div class="field"><span class="l">Período de Afastamento</span><span class="v">{info.get('dias','1')} dia(s) - {info.get('afastamento','-')}</span></div>
                <div class="field full"><span class="l">Observações</span><span class="v">{info.get('obs','-')}</span></div>
            </div>

            <div class="section-title">3. Médico Responsável</div>
            <div class="grid">
                <div class="field"><span class="l">Nome</span><span class="v">{info.get('medico','-')}</span></div>
                <div class="field"><span class="l">CRM / UF</span><span class="v">{info.get('crm','-')}</span></div>
                <div class="field full"><span class="l">Especialidade</span><span class="v">{info.get('especialidade','Clínica Geral')}</span></div>
            </div>

            <div class="section-title">4. Validação e Segurança</div>
            <div class="grid">
                <div class="field"><span class="l">Data de Emissão</span><span class="v">{info.get('emitido','-')}</span></div>
                <div class="field"><span class="l">Validade da Consulta Online</span><span class="v">Indeterminada</span></div>
                <div class="field full"><span class="l">Hash de Autenticidade</span><span class="v"><span class="hash">{hash_valid}</span></span></div>
            </div>

            <div class="qr-box">
                <img src="https://api.qrserver.com/v1/create-qr-code/?size=160x160&data=https://validacao-atesdado-medico.onrender.com/validar?doc={codigo}" style="border-radius:8px"><br>
                <div style="margin-top:12px;font-size:12px;color:#555">Escaneie o QR Code para validar novamente<br><b>{codigo}</b> • {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</div>
            </div>
        </div>
        <div class="footer">{NOME_CLINICA} • {ENDERECO} • Documento gerado eletronicamente - Lei 14.063/2020</div>
    </div></body></html>
    """

@app.get("/admin", response_class=HTMLResponse)
async def admin_page(request: Request):
    if not check_auth(request):
        return """<html><body style="font-family:Arial;background:#eef2f7;display:flex;align-items:center;justify-content:center;height:100vh;margin:0">
        <form method="post" action="/login" style="background:white;padding:35px;border-radius:14px;width:320px"><h3 style="text-align:center;color:#0f3554">LOGIN</h3>
        <input name="user" placeholder="Usuário" required style="width:100%;padding:12px;margin:8px 0"><input name="senha" type="password" placeholder="Senha" required style="width:100%;padding:12px;margin:8px 0">
        <button style="width:100%;padding:12px;background:#0f3554;color:white;border:none;border-radius:8px;margin-top:10px">ENTRAR</button></form></body></html>"""
    docs = carregar()
    linhas = "".join([f"<tr><td><b>{c}</b></td><td>{d.get('paciente','')}</td><td>{d.get('data','')}</td><td><a href='/validar?doc={c}' target='_blank'>Ver</a></td></tr>" for c,d in reversed(list(docs.items()))])
    return f"""<html><body style="font-family:Arial;background:#f5f7fb;padding:20px"><div style="max-width:1100px;margin:auto;background:white;padding:25px;border-radius:14px">
    <div style="display:flex;justify-content:space-between"><h2>{NOME_CLINICA}</h2><a href="/logout" style="color:#c00">Sair</a></div>
    <form method="post" action="/admin-salvar"><div style="display:grid;grid-template-columns:2fr 1fr 1fr;gap:10px">
    <input name="paciente" placeholder="Nome *" required style="padding:10px;border:1px solid #ddd;border-radius:6px"><input name="cpf" placeholder="CPF" style="padding:10px;border:1px solid #ddd;border-radius:6px"><input name="rg" placeholder="RG" style="padding:10px;border:1px solid #ddd;border-radius:6px">
    <input name="nascimento" placeholder="Nascimento" style="padding:10px;border:1px solid #ddd;border-radius:6px"><input name="idade" placeholder="Idade" style="padding:10px;border:1px solid #ddd;border-radius:6px"><input name="sexo" placeholder="Sexo" style="padding:10px;border:1px solid #ddd;border-radius:6px">
    <input name="codigo" placeholder="Código * ex: JB-90032" required style="padding:10px;border:1px solid #ddd;border-radius:6px"><input name="data" placeholder="Data" style="padding:10px;border:1px solid #ddd;border-radius:6px"><input name="horario" placeholder="Horário" style="padding:10px;border:1px solid #ddd;border-radius:6px">
    <input name="cid" placeholder="CID" style="padding:10px;border:1px solid #ddd;border-radius:6px"><input name="cid_desc" placeholder="Desc CID" style="padding:10px;border:1px solid #ddd;border-radius:6px"><input name="dias" placeholder="Dias" style="padding:10px;border:1px solid #ddd;border-radius:6px">
    <input name="medico" placeholder="Médico" style="padding:10px;border:1px solid #ddd;border-radius:6px"><input name="crm" placeholder="CRM" style="padding:10px;border:1px solid #ddd;border-radius:6px"><input name="especialidade" placeholder="Especialidade" style="padding:10px;border:1px solid #ddd;border-radius:6px">
    </div><button style="width:100%;padding:14px;background:#0f3554;color:white;border:none;border-radius:8px;margin-top:15px;font-weight:800">💾 SALVAR</button></form><hr><table border="1" cellpadding="10" style="width:100%;border-collapse:collapse"><tr style="background:#0f3554;color:white"><th>Código</th><th>Paciente</th><th>Data</th><th>Link</th></tr>{linhas}</table></div></body></html>"""

@app.post("/login")
async def login(user: str = Form(...), senha: str = Form(...)):
    if user == USUARIO and senha == SENHA:
        r = RedirectResponse(url="/admin", status_code=302)
        r.set_cookie(key="auth", value="logado", httponly=True, max_age=86400)
        return r
    return HTMLResponse("<h3>Senha errada</h3><a href='/admin'>Voltar</a>", status_code=401)

@app.get("/logout")
async def logout():
    r = RedirectResponse(url="/admin", status_code=302)
    r.delete_cookie("auth")
    return r

@app.post("/admin-salvar")
async def admin_salvar(request: Request, codigo: str = Form(...), paciente: str = Form(...), cpf: str = Form(""), rg: str = Form(""), nascimento: str = Form(""), idade: str = Form(""), sexo: str = Form(""), data: str = Form(""), horario: str = Form(""), cid: str = Form(""), cid_desc: str = Form(""), dias: str = Form("1"), afastamento: str = Form(""), unidade: str = Form(""), obs: str = Form(""), medico: str = Form(""), crm: str = Form(""), especialidade: str = Form(""), endereco: str = Form("")):
    if not check_auth(request): return RedirectResponse(url="/admin", status_code=302)
    docs = carregar()
    cod = codigo.upper().strip()
    docs[cod] = {"codigo": cod, "paciente": paciente, "cpf": cpf, "rg": rg, "nascimento": nascimento, "idade": idade, "sexo": sexo, "data": data, "horario": horario, "cid": cid, "cid_desc": cid_desc, "dias": dias, "afastamento": afastamento, "unidade": unidade or NOME_CLINICA, "endereco": endereco or ENDERECO, "obs": obs or "Atestado para fins de comprovação.", "medico": medico, "crm": crm, "especialidade": especialidade, "emitido": datetime.now().strftime("%d/%m/%Y às %H:%M:%S")}
    salvar(docs)
    return RedirectResponse(url="/admin", status_code=302)

@app.get("/")
async def home(): return RedirectResponse(url="/admin")
