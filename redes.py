"""
O que o esse código tem que fazer/ter:
    1 - Mostrar IP (coloquei pra mostar o IP Local e o Público);
    2 - Mostrar Gateway (win32 e linux);
    3 - Mostrar DNS;
    4 - Executar Tracert;
    5 - Executar Jitter;
    6 - Executar nslookup;
    7 - Ter um chat.
"""

import socket
import urllib.request
import subprocess
import sys
import re
import threading

def mostrarIpLocal():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    try:
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    except:
        ip = '127.0.0.1'
    finally:
        s.close()

    return ip


def mostrarIpPublico():
    try:
        url = "https://api.ipify.org"
        with urllib.request.urlopen(url) as resposta:
            ip = resposta.read().decode('utf-8')
            return ip
    except Exception:
        return 'Não foi possível obter o IP Público.'


def mostrarGateway():
    sistema = sys.platform
    try:
    #Para Windows
        if sistema == 'win32':
            saida = subprocess.check_output("ipconfig", text=True, encoding='cp850')
            linhas = saida.split("\n")
            aguardando_ipv4 = False

            for linha in linhas:
                if "Gateway Padrão" in linha or "Default Gateway" in linha:
                    partes = linha.split(":")
                    valor = partes[1].strip() if len(partes) > 1 else ""
                    if "fe80" in valor.lower():
                        aguardando_ipv4 = True
                        continue #Pula pra próxima linha, que vai dar o valor
                    if valor:
                        return valor
                elif aguardando_ipv4 and linha.strip():
                    return linha.strip()

    #Para Linux
        elif sistema.startswith("linux"):
            saida = subprocess.check_output(['ip', 'route'], text=True)
            for linha in saida.split("\n"):
                if "default via" in linha:
                    partes = linha.split()
                    if len(partes) >= 3:
                        return partes[2]

    except Exception as erro:
        return f"Erro ao identificar o gateway no sistema {sistema}: {erro}."

    return "Gateway não encontrado."


def mostrarDNS():
    sistema = sys.platform
    try:
        if sistema == 'win32':
            saida = subprocess.check_output("ipconfig /all", text=True, encoding='cp850')
            dns_servers = []
            capturando = False

            for linha in saida.split("\n"):
                if "Servidores DNS" in linha or "DNS Servers" in linha:
                    partes = linha.split(":")
                    if len(partes) > 1 and partes[1].strip():
                        dns_servers.append(partes[1].strip())
                    capturando = True
                    continue
                if capturando:
                    linha_strip = linha.strip()
                    # linha de continuação (IPv4/IPv6 do DNS secundário)
                    if linha_strip and re.match(r'^[\d\.\:a-fA-F%]+$', linha_strip):
                        dns_servers.append(linha_strip)
                    else:
                        capturando = False
            return dns_servers if dns_servers else ["Nenhum DNS encontrado."]

        elif sistema.startswith("linux"):
            with open('/etc/resolv.conf', 'r') as f:
                dns_servers = [linha.split()[1] for linha in f if linha.startswith("nameserver")]
            return dns_servers if dns_servers else ["Nenhum DNS encontrado."]

    except Exception as erro:
        return [f"Erro ao identificar DNS: {erro}"]


def executarTracert(destino="8.8.8.8"):
    sistema = sys.platform
    try:
        if sistema == 'win32':
            comando = ["tracert", destino]
        elif sistema.startswith("linux"):
            comando = ["traceroute", destino]
        else:
            return "Tracert não suportado nesse sistema."

        saida = subprocess.check_output(
            comando, text=True,
            encoding='cp850' if sistema == 'win32' else 'utf-8'
        )
        return saida
    except Exception as erro:
        return f"Erro ao executar tracert: {erro}"


def executarJitter(destino="8.8.8.8", quantidade=10):
    sistema = sys.platform
    try:
        comando = ["ping", destino, "-n", str(quantidade)] if sistema == 'win32' \
            else ["ping", destino, "-c", str(quantidade)]

        saida = subprocess.check_output(
            comando, text=True,
            encoding='cp850' if sistema == 'win32' else 'utf-8'
        )

        tempos = [float(t) for t in re.findall(r'tempo[=<]([\d\.]+)ms', saida, re.IGNORECASE)]
        if not tempos:
            tempos = [float(t) for t in re.findall(r'time[=<]([\d\.]+)\s*ms', saida, re.IGNORECASE)]

        if len(tempos) < 2:
            return "Não foi possível calcular o jitter (poucas respostas)."

        diferencas = [abs(tempos[i] - tempos[i - 1]) for i in range(1, len(tempos))]
        jitter = sum(diferencas) / len(diferencas)
        return f"Jitter médio: {jitter:.2f} ms (baseado em {len(tempos)} respostas)"

    except Exception as erro:
        return f"Erro ao calcular jitter: {erro}"


def executarNslookup(dominio):
    try:
        saida = subprocess.check_output(
            ["nslookup", dominio], text=True,
            encoding='cp850' if sys.platform == 'win32' else 'utf-8'
        )
        return saida
    except Exception as erro:
        return f"Erro ao executar nslookup: {erro}"


def iniciarChat(porta=5000):
    ip_local = mostrarIpLocal()
    print(f"Chat iniciado. Seu IP é {ip_local} — porta {porta}")

    def escutar():
        servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        servidor.bind(('0.0.0.0', porta))
        servidor.listen(1)
        while True:
            conexao, endereco = servidor.accept()
            print(f"\n[Conectado por {endereco[0]}]")
            while True:
                try:
                    dados = conexao.recv(1024)
                    if not dados:
                        break
                    print(f"\n[{endereco[0]}]: {dados.decode('utf-8')}\nVocê: ", end="")
                except:
                    break
            conexao.close()

    threading.Thread(target=escutar, daemon=True).start()

    ip_destino = input("Digite o IP da máquina para conversar: ").strip()

    try:
        cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        cliente.connect((ip_destino, porta))
    except Exception as erro:
        print(f"Não foi possível conectar: {erro}")
        return

    print("Conectado! Digite 'sair' para encerrar.\n")
    while True:
        mensagem = input("Você: ")
        if mensagem.lower() == 'sair':
            break
        try:
            cliente.sendall(mensagem.encode('utf-8'))
        except Exception as erro:
            print(f"Erro ao enviar: {erro}")
            break
    cliente.close()

def menu():
    while True:
        print("\n===== FERRAMENTA DE REDE =====")
        print("1 - Mostrar IP (Local e Público)")
        print("2 - Mostrar Gateway")
        print("3 - Mostrar DNS")
        print("4 - Executar Tracert")
        print("5 - Executar Jitter")
        print("6 - Executar Nslookup")
        print("7 - Iniciar Chat")
        print("0 - Sair")
        print("===============================")

        opcao = input("Escolha uma opção: ").strip()

        if opcao == "1":
            print(f"\nIP Local: {mostrarIpLocal()}")
            print(f"IP Público: {mostrarIpPublico()}")

        elif opcao == "2":
            print(f"\nGateway: {mostrarGateway()}")

        elif opcao == "3":
            dns = mostrarDNS()
            print("\nServidores DNS encontrados:")
            for servidor in dns:
                print(f" - {servidor}")

        elif opcao == "4":
            destino = input("Digite o destino (ou Enter para 8.8.8.8): ").strip()
            destino = destino if destino else "8.8.8.8"
            print(f"\nExecutando tracert para {destino}...\n")
            print(executarTracert(destino))

        elif opcao == "5":
            destino = input("Digite o destino (ou Enter para 8.8.8.8): ").strip()
            destino = destino if destino else "8.8.8.8"
            print(f"\nCalculando jitter para {destino}...\n")
            print(executarJitter(destino))

        elif opcao == "6":
            dominio = input("Digite o domínio (ex: google.com): ").strip()
            if dominio:
                print(f"\nExecutando nslookup para {dominio}...\n")
                print(executarNslookup(dominio))
            else:
                print("\nDomínio não pode ser vazio.")

        elif opcao == "7":
            iniciarChat()

        elif opcao == "0":
            print("\nEncerrando programa...")
            break

        else:
            print("\nOpção inválida. Tente novamente.")


if __name__ == "__main__":
    menu()
