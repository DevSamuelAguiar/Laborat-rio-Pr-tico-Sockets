import socket
import json
import datetime

CONFIGURACAO = {
    'ip': 'http://samuelaguiar.ddns.net/',
    'porta': 8080
}

def alterar_servidor():
    print("\nAlterar Configuração do Servidor")
    novo_ip = input(f"Novo IP (atual: {CONFIGURACAO['ip']}): ") or CONFIGURACAO['ip']
    nova_porta = input(f"Nova Porta (atual: {CONFIGURACAO['porta']}): ") or CONFIGURACAO['porta']
    
    try:
        nova_porta = int(nova_porta)
        with socket.create_connection((novo_ip, nova_porta), timeout=2):
            CONFIGURACAO.update({"ip": novo_ip, "porta": nova_porta})
            print("Servidor Disponivel ! Atualizado com sucesso!")
    except Exception:
        print("Erro ao conectar. As configurações antigas serão mantidas.")

def enviar_mensagem(dados):
    with socket.create_connection((CONFIGURACAO["ip"], CONFIGURACAO["porta"])) as conn:
        conn.sendall(json.dumps(dados).encode())
        return json.loads(conn.recv(1024).decode())

def criar_conta():
    dados = {
        "acao": "cadastro",
        "nome": input("Nome completo: "),
        "usuario": input("Usuário: ").strip().replace(" ", ""),
        "senha": input("Senha: ")
    }
    resposta = enviar_mensagem(dados)
    print(resposta["mensagem"])

def acessar_conta():
    global usuario_atual
    credenciais = {
        "acao": "login",
        "usuario": input("Usuário: ").strip(),
        "senha": input("Senha: ")
    }
    resposta = enviar_mensagem(credenciais)
    if resposta["status"] == "sucesso":
        usuario_atual = credenciais["usuario"]
        print(f"\n Seja Muito Bem-vindo, {resposta['nome']}!")
        menu_principal()
    else:
        print(resposta["mensagem"])

def escrever_email():
    if not usuario_atual:
        print(" É Necessário fazer login primeiro.")
        return
    
    email = {
        "acao": "enviar",
        "de": usuario_atual,
        "para": input("Destinatário: "),
        "data": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "assunto": input("Assunto: "),
        "conteudo": input("Mensagem: ")
    }
    print(enviar_mensagem(email)["mensagem"])

def visualizar_emails():
    if not usuario_atual:
        print("É Necessário fazer login primeiro.")
        return
    
    resposta = enviar_mensagem({"acao": "listar", "usuario": usuario_atual})
    emails = resposta.get("emails", [])
    
    if emails:
        print(f"\nVocê tem {len(emails)} novos e-mails:")
        for idx, email in enumerate(emails, start=1):
            print(f"[{idx}] {email['de']} - {email['assunto']}")
        escolha = int(input("Abrir qual e-mail? ")) - 1
        if 0 <= escolha < len(emails):
            email = emails[escolha]
            print(f"\nDe: {email['de']}\nAssunto: {email['assunto']}\n{email['conteudo']}")
    else:
        print("Você não possui novas mensagens.")

def menu_principal():
    while True:
        escolha = input("\nCliente E-mail Service BSI Online\n1) Escrever E-mail\n2) Ver E-mails\n3) Sair\nEscolha: ")
        if escolha == "1":
            escrever_email()
        elif escolha == "2":
            visualizar_emails()
        elif escolha == "3":
            print("Saindo...")
            break

def iniciar():
    global usuario_atual
    usuario_atual = None
    while True:
        opcao = input("\n1) Apontar Servidor\n2) Cadastrar Conta \n3) Acessar E-mail \n4) Sair ")
        if opcao == "1":
            alterar_servidor()
        elif opcao == "2":
            criar_conta()
        elif opcao == "3":
            acessar_conta()
        elif opcao == "4":
            print("Encerrando...")
            break

if __name__ == "__main__":
    iniciar()
