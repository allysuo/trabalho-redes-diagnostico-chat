import subprocess
import socket
import urllib.request
import re
import statistics
import threading

def executar(comando):
    try:
        resultado = subprocess.run(
            comando,
            capture_output=True,
            text=True,
            shell=True,
            encoding="cp850",
            errors="ignore"
        )
        return resultado.stdout
    except Exception as erro:
        return f"Erro: {erro}"

def obter_ip_local():
    try:
        hostname = socket.gethostname()
        return socket.gethostbyname(hostname)
    except:
        return "Não encontrado"

def obter_ip_publico():
    try:
        with urllib.request.urlopen("https://api.ipify.org", timeout=5) as resposta:
            return resposta.read().decode()
    except:
        return "Não encontrado"

def obter_configuracao():
    resultado = executar("ipconfig /all")
    gateway = "Não encontrado"
    dns = "Não encontrado"

    match_gateway = re.search(r"(?:Default Gateway|Gateway Padrão)[^:]*:\s*([0-9.]+)", resultado, re.IGNORECASE)
    if match_gateway:
        gateway = match_gateway.group(1)

    match_dns = re.search(r"(?:DNS Servers|Servidores DNS)[^:]*:\s*([0-9.]+)", resultado, re.IGNORECASE)
    if match_dns:
        dns = match_dns.group(1)

    return gateway, dns

def testar_ping(ip_alvo):
    print("\n[ CONEXÃO ]")
    print(f"Testando ping em {ip_alvo}...\n")
    resultado = executar(f"ping -n 10 {ip_alvo}")
    print(resultado)

    tempos = re.findall(r"(?:time|tempo)[=<]\s*(\d+)\s*ms", resultado, re.IGNORECASE)
    tempos = [int(t) for t in tempos]

    if not tempos:
        print("Não foi possível calcular o ping.")
        return

    ping_medio = statistics.mean(tempos)
    diferencas = [abs(tempos[i] - tempos[i - 1]) for i in range(1, len(tempos))]
    jitter = statistics.mean(diferencas) if diferencas else 0
    enviados = 10
    recebidos = len(tempos)
    perda = ((enviados - recebidos) / enviados) * 100

    print("--------------------------------")
    print(f"Ping médio : {ping_medio:.2f} ms")
    print(f"Jitter     : {jitter:.2f} ms")
    print(f"Perda      : {perda:.0f}%")
    print("--------------------------------")

def testar_porta(ip_alvo, porta):
    print(f"\n[ TESTE DE PORTA ]\nVerificando porta {porta} em {ip_alvo}...")
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(3)
        resultado = s.connect_ex((ip_alvo, porta))
        s.close()
        
        if resultado == 0:
            print(f"-> A porta {porta} está ABERTA!")
        else:
            print(f"-> A porta {porta} está FECHADA ou bloqueada.")
    except Exception as erro:
        print(f"Erro ao testar a porta: {erro}")

def nslookup(ip_alvo):
    print("\n[ NSLOOKUP ]\n")
    resultado = executar(f"nslookup {ip_alvo}")
    print(resultado)

def tracert(ip_alvo):
    print("\n[ TRACERT ]")
    print(f"Rota até {ip_alvo}:\n")
    resultado = executar(f"tracert -h 10 {ip_alvo}")
    print(resultado)

# --- FUNÇÕES DE CHAT ---
def chat_receber(conexao):
    while True:
        try:
            mensagem = conexao.recv(1024).decode('utf-8')
            if not mensagem:
                break
            print(f"\n[Mensagem recebida]: {mensagem}")
        except:
            print("\n[Chat desconectado]")
            break

def main():
    print("╔══════════════════════════════════════╗")
    print("║      DIAGNÓSTICO & CHAT DE REDE      ║")
    print("╚══════════════════════════════════════╝")

    nickname = input("\nDigite seu Nickname: ").strip()
    chave = input("Digite a Chave de seleção: ").strip()

    while True:
        print("\n================ MENU PRINCIPAL ================")
        print("1 - Fazer Diagnóstico de Rede (Ping, Tracert, Porta)")
        print("2 - Criar sala de Chat (Ficar esperando alguém)")
        print("3 - Entrar em sala de Chat (Conectar em um IP)")
        print("0 - Sair do programa")
        
        escolha = input("\nEscolha uma opção (0, 1, 2 ou 3): ").strip()

        if escolha == '0':
            print("Saindo...")
            break

        elif escolha == '1':
            ip_alvo = input("\nDigite o IP do alvo [padrão: 8.8.8.8]: ").strip()
            if not ip_alvo:
                ip_alvo = "8.8.8.8"
                
            porta_str = input("Digite a Porta [padrão: 80]: ").strip()
            porta = int(porta_str) if porta_str.isdigit() else 80

            print("\n[ IDENTIFICAÇÃO ]")
            print(f"Usuário : {nickname}")
            print(f"Chave   : {chave}")

            ip_local = obter_ip_local()
            ip_publico = obter_ip_publico()
            gateway, dns = obter_configuracao()

            print("\n[ SUA REDE ]")
            print(f"IP local   : {ip_local}")
            print(f"IP público : {ip_publico}")
            print(f"Gateway    : {gateway}")
            print(f"DNS        : {dns}")

            testar_ping(ip_alvo)
            testar_porta(ip_alvo, porta)
            nslookup(ip_alvo)
            tracert(ip_alvo)
            
            print("════════════════════════════════════════")
            print("          TESTE FINALIZADO")
            print("════════════════════════════════════════")

        elif escolha == '2':
            porta_chat = 50000
            servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            servidor.bind(('0.0.0.0', porta_chat))
            servidor.listen(1)
            
            print(f"\n[SALA CRIADA] Seu IP local é {obter_ip_local()}. Esperando conexão...")
            conexao, endereco = servidor.accept()
            print(f"\n[{endereco[0]} entrou na sala!] Digite 'sair' para encerrar.")
            
            threading.Thread(target=chat_receber, args=(conexao,)).start()
            
            while True:
                texto = input("")
                if texto.lower() == 'sair':
                    break
                conexao.send(f"[{nickname}] {texto}".encode('utf-8'))
                
            conexao.close()
            servidor.close()

        elif escolha == '3':
            ip_amigo = input("\nDigite o IP de quem criou a sala: ").strip()
            porta_chat = 50000
            
            cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                cliente.connect((ip_amigo, porta_chat))
                print(f"\n[Conectado a {ip_amigo}!] Digite 'sair' para encerrar.")
                
                threading.Thread(target=chat_receber, args=(cliente,)).start()
                
                while True:
                    texto = input("")
                    if texto.lower() == 'sair':
                        break
                    cliente.send(f"[{nickname}] {texto}".encode('utf-8'))
                    
                cliente.close()
            except:
                print("\nFalha ao conectar. Tem certeza que o IP está certo e a sala foi criada?")

        else:
            print("Opção inválida! Digite apenas 0, 1, 2 ou 3.")

if __name__ == "__main__":
    main()
