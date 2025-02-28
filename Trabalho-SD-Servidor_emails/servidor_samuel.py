import socket
import json
import datetime
import bcrypt
from concurrent.futures import ThreadPoolExecutor


banco_usuarios = {} 
banco_mensagens = {}  

def registrar_evento(tipo, descricao=""):
    momento = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{momento}] {tipo}: {descricao}")

def processar_cliente(conexao):
    try:
        while True:
            dados = conexao.recv(1024).decode()
            if not dados:
                break

            requisicao = json.loads(dados)
            operacao = requisicao.get("acao")
            registrar_evento("Requisição recebida", f"Operação: {operacao}")

            operacoes = {
                "cadastro": cadastrar_usuario,
                "login": autenticar_usuario,
                "enviar_mensagem": enviar_email,
                "receber_mensagens": consultar_emails
            }

            resposta = operacoes.get(operacao, lambda x: {"status": "erro", "mensagem": "Operação inválida"})(requisicao)
            conexao.send(json.dumps(resposta).encode())
    except Exception as erro:
        registrar_evento("Erro", str(erro))
    finally:
        conexao.close()
        registrar_evento("A Conexão foi finalizada!", "O Cliente está desconectado !")

def cadastrar_usuario(dados):
    usuario, nome, senha = dados["usuario"], dados["nome"], dados["senha"].encode()

    if usuario in banco_usuarios:
        registrar_evento("Falha no cadastro", f"Usuário {usuario} já cadastrado")
        return {"status": "erro", "mensagem": "Usuário já existe."}

    senha_hash = bcrypt.hashpw(senha, bcrypt.gensalt())
    banco_usuarios[usuario] = {"nome": nome, "senha": senha_hash}
    registrar_evento("Cadastro realizado", f"Novo usuário: {usuario} ({nome})")
    return {"status": "sucesso", "mensagem": "Registro do usuário concluído."}

def autenticar_usuario(dados):
    usuario, senha = dados["usuario"], dados["senha"].encode()
    credenciais = banco_usuarios.get(usuario)
    
    if not credenciais or not bcrypt.checkpw(senha, credenciais["senha"]):
        registrar_evento("Ocorreu uma falha no login", f"Usuário: {usuario}")
        return {"status": "erro", "mensagem": "Credenciais incorretas."}
    
    registrar_evento("Login bem-sucedido", f"Usuário: {usuario}")
    return {"status": "sucesso", "mensagem": f"Bem-vindo {credenciais['nome']}!", "nome": credenciais["nome"]}

def enviar_email(dados):
    remetente, destinatario, assunto, conteudo, data = (
        dados["remetente"], dados["destinatario"], dados["assunto"], dados["conteudo"], dados["data"]
    )
    
    if destinatario not in banco_usuarios:
        registrar_evento("Atenção!! Ocorreu um erro, o envio não foi concluído!", f"Destinatário não foi localizado: {destinatario}")
        return {"status": "erro", "mensagem": "Destinatário não encontrado."}

    banco_mensagens.setdefault(destinatario, []).append({
        "remetente": remetente,
        "destinatario": destinatario,
        "data": data,
        "assunto": assunto,
        "conteudo": conteudo
    })
    
    registrar_evento("Sua mensagem enviada, com sucesso!", f"De: {remetente} Para: {destinatario} - Assunto: {assunto}")
    return {"status": "sucesso", "mensagem": "O e-mail teve seu envio concluído sucesso."}

def consultar_emails(dados):
    usuario = dados["usuario"]
    mensagens = banco_mensagens.pop(usuario, [])
    registrar_evento("Mensagens entregues", f"{len(mensagens)} mensagem(ns) para {usuario}")
    return {"status": "sucesso", "emails": mensagens}

def iniciar_servidor():
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor.bind(("0.0.0.0", 8080))
    servidor.listen(5)
    registrar_evento("Servidor em execução", "Porta 8080")
    
    with ThreadPoolExecutor() as executor:
        while True:
            cliente, endereco = servidor.accept()
            registrar_evento("Nova conexão", f"Origem: {endereco}")
            executor.submit(processar_cliente, cliente)

if __name__ == "__main__":
    iniciar_servidor()
