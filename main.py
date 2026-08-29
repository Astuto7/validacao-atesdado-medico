from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
import json, os, hashlib
from datetime import datetime

app = FastAPI()
ARQUIVO = "documentos.json"

# --- CONFIGURA AQUI ---
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
async def validar(doc: str = "", request: Request = None):
    try:
        docs = carregar()
        codigo = doc.upper().strip()
        info = docs.get(codigo)
        if not info:
            return f"""
            <html><body style="font-family:Arial;background:#f4f6f9;display:flex;justify-content:center;align-items:center;height:100vh;margin:0">
            <div style="background:white;padding:40px;border-radius:12px;text-align:center;box-shadow:0 10px 30px rgba(0,0,0,.1);max-width:420px">
            <div style="width:60px;height:60px;background:#ffebee;color:#c62828;border-radius:50%;display:flex;align-items:center;justify-content:center;margin:0 auto 15px;font-size:30px">✕</div>
            <h2 style="color:#c62828">Documento Não Encontrado</h2><p style="color:#666">O código <b>{doc}</b> não consta em nossa base.<br>Verifique o código ou entre em contato com a clínica.</p>
            <small style="color:#999">{NOME_CLINICA} - {TELEFONE}</small>
            </div></body></html>
            """

        # dados com fallback pra não quebrar doc antigo
        hash_valid = hashlib.md5(f"{codigo}{info.get('cpf','')}{info.get('data','')}".encode()).hexdigest().upper()[:16]
        ip = request.client.host if request else "N/A"

        return f"""
        <html><head><meta name="viewport" content="width=device-width, initial-scale=1"><title>Validação - {codigo} - {NOME_CLINICA}</title>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
        <style>
            *{{font-family:'Inter',Arial,sans-serif}} body{{margin:0;background:#eef2f7}}
           .page{{max-width:800px;margin:20px auto;background:white;border-radius:16px;overflow:hidden;box-shadow:0 10px 40px rgba(0,0,0,.12)}}
           .header{{background:linear-gradient(135deg,#0f3554 0%,#163e6b 100%);color:white;padding:20px 30px;display:flex;justify-content:space-between;align-items:center}}
           .header img{{max-height:52px;background:white;padding:6px 10px;border-radius:8px}}
           .badge{{background:#00c853;color:white;padding:8px 16px;border-radius:20px;font-size:13px;font-weight:700;display:inline-flex;align-items:center;gap:6px}}
           .content{{padding:0 30px 30px}}
           .status-box{{background:#e8f5e9;border:1px solid #a5d6a7;border-radius:12px;padding:16px 20px;display:flex;justify-content:space-between;align-items:center;margin:20px 0}}
           .grid{{display:grid;grid-template-columns:1fr 1fr;gap:0}}
           .field{{padding:14px 0;border-bottom:1px solid #f0f0f0;display:flex;flex-direction:column}}
           .field.full{{grid-column:1 / -1}}.field.l{{font-size:11px;color:#8a8a8a;text-transform:uppercase;letter-spacing:.5px;margin-bottom:4px}}.field.v{{font-size:14px;font-weight:600;color:#1a1a1a}}
           .section-title{{font-size:13px;font-weight:700;color:#0f3554;text-transform:uppercase;letter-spacing:1px;margin:30px 0 10px;padding-left:12px;border-left:4px solid #0f3554}}
           .qr-box{{background:#fafafa;border:1px dashed #ddd;border-radius:12px;padding:20px;text-align:center;margin-top:20px}}
           .footer{{background:#f8f9fa;padding:20px 30px;font-size:11px;color:#888;border-top:1px solid #eee}}
           .hash{{font-family:monospace;background:#eee;padding:4px 8px;border-radius:4px;font-size:12px}}
            @media(max-width:600px){{.grid{{grid-template-columns:1fr}}.header{{flex-direction:column;gap:12px}}}}
        </style></head>
        <body><div class="page">
            <div class="header">
                <div><img src="{LOGO_URL}"><div style="margin-top:8px;font-size:12px;opacity:.9">{CNPJ} • {ENDERECO}</div></div>
                <div style="text-align:right"><div style="font-size:12px;opacity:.8">Sistema de Validação Digital</div><div style="font-weight:700">{NOME_CLINICA}</div></div>
            </div>
            <div class="content">
                <div class="status-box">
                    <div><div style="font-weight:700;color:#2e7d32;font-size:15px">✓ DOCUMENTO AUTENTICADO COM SUCESSO</div><div style="font-size:12px;color:#555;margin-top:4px">Este documento foi emitido por nossa instituição e consta em nossa base oficial.</div></div>
                    <div style="text-align:right"><div style="font-size:11px;color:#888">CÓDIGO</div><div style="font-weight:800;font-size:16px;color:#0f3554">{codigo}</div></div>
                </div>

                <div class="section-title">1. Identificação do Paciente / Beneficiário</div>
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
                    <div class="field full"><span class="l">Observações / Finalidade</span><span class="v">{info.get('obs','Atestado para fins de comprovação junto ao empregador.')}</span></div>
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
                    <div class="field"><span class="l">Hash de Autenticidade</span><span class="v"><span class="hash">{hash_valid}</span></span></div>
                    <div class="field"><span class="l">IP da Validação</span><span class="v">{ip}</span></div>
                    <div class="field full"><span class="l">Link Permanente</span><span class="v" style="font-size:12px;word-break:break-all">https://validacao-atesdado-medico.onrender.com/validar?doc={codigo}</span></div>
                </div>

                <div class="qr-box">
                    <img src="https://api.qrserver.com/v1/create-qr-code/?size=160x160&data=https://validacao-atesdado-medico.onrender.com/validar?doc={codigo}" style="border-radius:8px"><br>
                    <div style="margin-top:12px;font-size:12px;color:#555">Escaneie o QR Code para validar novamente<br><b>{codigo}</b> • Validado em {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</div>
                </div>

                <div style="background:#fff8e1;border:1px solid #ffe082;border-radius:8px;padding:12px 16px;margin-top:25px;font-size:12px;color:#6d4c00">
                <b>⚠️ Aviso Legal:</b> A falsificação deste documento é crime previsto no art. 302 do Código Penal. Em caso de dúvida, contate {NOME_CLINICA} em {TELEFONE} ou {EMAIL} informando o código <b>{codigo}</b>.
                </div>
            </div>
            <div class="footer">
                <div style="display:flex;justify-content:space-between;flex-wrap:wrap;gap:10px">
                    <span>© {datetime.now().year} {NOME_CLINICA} - Todos os direitos reservados</span>
                    <span>Documento gerado eletronicamente - Não necessita assinatura física - Lei 14.063/2020</span>
                </div>
            </div>
        </div></body></html>
        """
    except Exception as e:
        return HTMLResponse(f"<h2>Erro: {e}</h2>", status_code=500)

@app.get("/admin", response_class=HTMLResponse)
async def admin_page(request: Request):
    if not check_auth(request):
        return """<html><head><meta name="viewport" content="width=device-width, initial-scale=1"></head>
        <body style="font-family:Arial;background:#eef2f7;display:flex;align-items:center;justify-content:center;height:100vh;margin:0">
        <form method="post" action="/login" style="background:white;padding:35px;border-radius:14px;width:320px;box-shadow:0 10px 30px rgba(0,0,0,.1)">
        <h3 style="text-align:center;color:#0f3554">PAINEL PROFISSIONAL</h3>
        <input name="user" placeholder="Usuário" required style="width:100%;padding:12px;margin:8px 0;box-sizing:border-box;border:1px solid #ddd;border-radius:8px">
        <input name="senha" type="password" placeholder="Senha" required style="width:100%;padding:12px;margin:8px 0;box-sizing:border-box;border:1px solid #ddd;border-radius:8px">
        <button style="width:100%;padding:12px;background:#0f3554;color:white;border:none;border-radius:8px;margin-top:10px;font-weight:700">ENTRAR</button>
        </form></body></html>"""
    docs = carregar()
    linhas = ""
    for cod, d in reversed(list(docs.items())):
        link = f"https://validacao-atesdado-medico.onrender.com/validar?doc={cod}"
        linhas += f"<tr><td><b>{cod}</b></td><td>{d.get('paciente','')}</td><td>{d.get('data','')}</td><td>{d.get('cid','')}</td><td><a href='{link}' target='_blank'>Validar</a></td></tr>"
    return f"""
    <html><head><meta name="viewport" content="width=device-width, initial-scale=1"></head>
    <body style="font-family:Arial;background:#f5f7fb;padding:20px"><div style="max-width:1100px;margin:auto;background:white;padding:25px;border-radius:14px;box-shadow:0 5px 20px rgba(0,0,0,.06)">
    <div style="display:flex;justify-content:space-between;align-items:center"><h2 style="color:#0f3554;margin:0">Gerador PRO - {NOME_CLINICA}</h2><a href="/logout" style="color:#c00">Sair</a></div><br>
    <form method="post" action="/admin-salvar">
    <h4 style="color:#0f3554;border-bottom:2px solid #0f3554;padding-bottom:6px">Paciente</h4>
    <div style="display:grid;grid-template-columns:2fr 1fr 1fr;gap:10px">
        <input name="paciente" placeholder="Nome Completo *" required style="padding:10px;border:1px solid #ddd;border-radius:6px">
        <input name="cpf" placeholder="CPF" style="padding:10px;border:1px solid #ddd;border-radius:6px">
        <input name="rg" placeholder="RG" style="padding:10px;border:1px solid #ddd;border-radius:6px">
        <input name="nascimento" placeholder="Nascimento (AAAA-MM-DD)" style="padding:10px;border:1px solid #ddd;border-radius:6px">
        <input name="idade" placeholder="Idade" style="padding:10px;border:1px solid #ddd;border-radius:6px">
        <input name="sexo" placeholder="Sexo M/F" style="padding:10px;border:1px solid #ddd;border-radius:6px">
    </div>
    <h4 style="color:#0f3554;border-bottom:2px solid #0f3554;padding-bottom:6px;margin-top:20px">Atendimento</h4>
    <div style="display:grid;grid-template-columns:1fr 1fr 1fr 1fr;gap:10px">
        <input name="codigo" placeholder="Código * ex: JB-93495" required style="padding:10px;border:1px solid #ddd;border-radius:6px">
        <input name="data" placeholder="Data ex: 2026-08-19" style="padding:10px;border:1px solid #ddd;border-radius:6px">
        <input name="horario" placeholder="Horário ex: 14:07" style="padding:10px;border:1px solid #ddd;border-radius:6px">
        <input name="tipo" value="Atestado Médico" style="padding:10px;border:1px solid #ddd;border-radius:6px">
        <input name="cid" placeholder="CID ex: J06" style="padding:10px;border:1px solid #ddd;border-radius:6px">
        <input name="cid_desc" placeholder="Descrição CID ex: Gripe" style="padding:10px;border:1px solid #ddd;border-radius:6px">
        <input name="dias" placeholder="Dias afastamento ex: 3" style="padding:10px;border:1px solid #ddd;border-radius:6px">
        <input name="afastamento" placeholder="Período ex: 19/08 a 22/08" style="padding:10px;border:1px solid #ddd;border-radius:6px">
        <input name="unidade" placeholder="Unidade" value="{NOME_CLINICA}" style="padding:10px;border:1px solid #ddd;border-radius:6px;grid-column: span 4">
        <input name="obs" placeholder="Observações" style="padding:10px;border:1px solid #ddd;border-radius:6px;grid-column: span 4">
    </div>
    <h4 style="color:#0f3554;border-bottom:2px solid #0f3554;padding-bottom:6px;margin-top:20px">Médico</h4>
    <div style="display:grid;grid-template-columns:2fr 1fr 1fr;gap:10px">
        <input name="medico" placeholder="Dr. Nome" style="padding:10px;border:1px solid #ddd;border-radius:6px">
        <input name="crm" placeholder="CRM/RJ 1234" style="padding:10px;border:1px solid #ddd;border-radius:6px">
        <input name="especialidade" placeholder="Especialidade" value="Clínica Geral" style="padding:10px;border:1px solid #ddd;border-radius:6px">
    </div>
    <button style="width:100%;padding:14px;background:#0f3554;color:white;border:none;border-radius:8px;margin-top:20px;font-weight:800;font-size:15px">💾 SALVAR DOCUMENTO PROFISSIONAL</button>
    </form><hr style="margin:25px 0"><table border="1" cellpadding="10" style="width:100%;border-collapse:collapse;font-size:13px"><tr style="background:#0f3554;color:white"><th>Código</th><th>Paciente</th><th>Data</th><th>CID</th><th>Link</th></tr>{linhas}</table>
    </div></body></html>
    """

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
async def admin_salvar(request: Request, codigo: str = Form(...), paciente: str = Form(...), cpf: str = Form(""), rg: str = Form(""), nascimento: str = Form(""), idade: str = Form(""), sexo: str = Form(""), data: str = Form(""), horario: str = Form(""), tipo: str = Form("Atestado Médico"), cid: str = Form(""), cid_desc: str = Form(""), dias: str = Form("1"), afastamento: str = Form(""), unidade: str = Form(""), obs: str = Form(""), medico: str = Form(""), crm: str = Form(""), especialidade: str = Form("Clínica Geral")):
    if not check_auth(request): return RedirectResponse(url="/admin", status_code=302)
    docs = carregar()
    cod = codigo.upper().strip()
    docs[cod] = {"codigo": cod, "paciente": paciente, "cpf": cpf, "rg": rg, "nascimento": nascimento, "idade": idade, "sexo": sexo, "data": data, "horario": horario, "tipo": tipo, "cid": cid, "cid_desc": cid_desc, "dias": dias, "afastamento": afastamento, "unidade": unidade or NOME_CLINICA, "obs": obs or "Atestado para fins de comprovação junto ao empregador.", "medico": medico, "crm": crm, "especialidade": especialidade, "emitido": datetime.now().strftime("%d/%m/%Y às %H:%M:%S")}
    salvar(docs)
    return RedirectResponse(url="/admin", status_code=302)

@app.get("/", response_class=HTMLResponse)
async def home(): return '<meta http-equiv="refresh" content="0; url=/admin">'
