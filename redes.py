#!/usr/bin/env python3
"""
Projeto: Diagnóstico & Chat de Rede
---------------------------
CLI em Python que combina utilitários de diagnóstico de rede
(ping, teste de porta, DNS, traceroute) com um chat P2P simples
via sockets TCP.

Compatível com Windows, Linux e macOS.
"""

import os
import sys
import re
import time
import socket
import platform
import threading
import subprocess
import urllib.request

SYSTEM = platform.system()  # 'Windows', 'Linux', 'Darwin'
CHAT_PORT = 50000
BUFFER_SIZE = 4096


# =========================================================
# Utilidades gerais
# =========================================================

def limpar_tela():
    os.system('cls' if SYSTEM == 'Windows' else 'clear')


def executar_comando(cmd):
    """Executa um comando no shell e retorna o stdout como texto,
    tratando a codificação correta em cada sistema operacional."""
    try:
        encoding = 'cp850' if SYSTEM == 'Windows' else 'utf-8'
        resultado = subprocess.run(
            cmd, capture_output=True, timeout=15
        )
        saida = resultado.stdout.decode(encoding, errors='ignore')
        if not saida.strip() and resultado.stderr:
            saida = resultado.stderr.decode(encoding, errors='ignore')
        return saida
    except FileNotFoundError:
        return f"Comando não encontrado: {cmd[0]}"
    except subprocess.TimeoutExpired:
        return "Comando expirou (timeout)."
    except Exception as e:
        return f"Erro ao executar comando: {e}"


# =========================================================
# Diagnóstico de rede
# =========================================================

def obter_ip_local():
    """Descobre o IP local sem depender de internet real
    (usa um socket UDP 'fake connect')."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(0.5)
        try:
            s.connect(('8.8.8.8', 80))
            ip = s.getsockname()[0]
        finally:
            s.close()
        return ip
    except Exception:
        return "Não foi possível determinar"


def obter_ip_publico():
    try:
        with urllib.request.urlopen('https://api.ipify.org', timeout=5) as resp:
            return resp.read().decode().strip()
    except Exception:
        return "Sem acesso à internet ou serviço indisponível"


def obter_gateway_e_dns():
    gateway = "Não encontrado"
    dns_servers = []

    if SYSTEM == 'Windows':
        saida = executar_comando(['ipconfig', '/all'])
        for linha in saida.splitlines():
            l = linha.strip()
            if 'Gateway Padrão' in linha or 'Default Gateway' in linha:
                partes = l.split(':', 1)
                if len(partes) > 1 and partes[1].strip():
                    gateway = partes[1].strip()
            if 'Servidores DNS' in linha or 'DNS Servers' in linha:
                partes = l.split(':', 1)
                if len(partes) > 1 and partes[1].strip():
                    dns_servers.append(partes[1].strip())

    elif SYSTEM == 'Darwin':
        saida = executar_comando(['route', '-n', 'get', 'default'])
        for linha in saida.splitlines():
            if 'gateway:' in linha:
                gateway = linha.split(':', 1)[1].strip()
        saida_dns = executar_comando(['scutil', '--dns'])
        for linha in saida_dns.splitlines():
            if 'nameserver[0]' in linha:
                dns_servers.append(linha.split(':', 1)[1].strip())
                break

    else:  # Linux
        saida = executar_comando(['ip', 'route'])
        for linha in saida.splitlines():
            if linha.startswith('default'):
                partes = linha.split()
                if 'via' in partes:
                    gateway = partes[partes.index('via') + 1]
        try:
            with open('/etc/resolv.conf') as f:
                for linha in f:
                    if linha.startswith('nameserver'):
                        dns_servers.append(linha.split()[1])
        except Exception:
            pass

    return gateway, (dns_servers if dns_servers else ["Não encontrado"])


def testar_ping(alvo, quantidade=4):
    if SYSTEM == 'Windows':
        cmd = ['ping', '-n', str(quantidade), alvo]
    else:
        cmd = ['ping', '-c', str(quantidade), alvo]

    saida = executar_comando(cmd)

    # cobre "tempo=12ms" (pt-BR) e "time=12 ms" (en)
    tempos = [float(t) for t in re.findall(
        r'(?:tempo|time)[=<]\s*([\d.]+)\s*ms', saida, re.IGNORECASE
    )]

    perdidos = max(quantidade - len(tempos), 0)
    perda_pct = (perdidos / quantidade) * 100 if quantidade else 0

    if tempos:
        media = sum(tempos) / len(tempos)
        if len(tempos) > 1:
            jitter = sum(
                abs(tempos[i] - tempos[i - 1]) for i in range(1, len(tempos))
            ) / (len(tempos) - 1)
        else:
            jitter = 0.0
    else:
        media = 0.0
        jitter = 0.0

    return {
        'saida_bruta': saida,
        'amostras': tempos,
        'latencia_media_ms': round(media, 2),
        'jitter_ms': round(jitter, 2),
        'perda_pct': round(perda_pct, 2),
    }


def testar_porta(alvo, porta, timeout=3):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(timeout)
            resultado = s.connect_ex((alvo, int(porta)))
            return resultado == 0
    except socket.gaierror:
        return None  # não foi possível resolver o host
    except Exception:
        return False


def nslookup(alvo):
    try:
        hostname, aliases, ips = socket.gethostbyname_ex(alvo)
        return {'hostname': hostname, 'aliases': aliases, 'ips': ips}
    except Exception as e:
        return {'erro': str(e)}


def traceroute(alvo, max_saltos=30):
    if SYSTEM == 'Windows':
        cmd = ['tracert', '-h', str(max_saltos), alvo]
    else:
        cmd = ['traceroute', '-m', str(max_saltos), alvo]
    return executar_comando(cmd)


def diagnostico_completo():
    print("\n=== Diagnóstico de Rede ===")
    print(f"IP Local:   {obter_ip_local()}")
    print("Consultando IP público...")
    print(f"IP Público: {obter_ip_publico()}")

    gateway, dns = obter_gateway_e_dns()
    print(f"Gateway Padrão: {gateway}")
    print(f"Servidores DNS: {', '.join(dns)}")


def menu_teste_conexao():
    alvo = input("\nDigite o IP ou domínio alvo: ").strip()
    if not alvo:
        print("Alvo inválido.")
        return

    print("\n--- Resolução DNS ---")
    dns_info = nslookup(alvo)
    if 'erro' in dns_info:
        print(f"Falha na resolução: {dns_info['erro']}")
    else:
        print(f"Hostname: {dns_info['hostname']}")
        print(f"IP(s): {', '.join(dns_info['ips'])}")

    print("\n--- Teste de Ping ---")
    resultado_ping = testar_ping(alvo)
    print(f"Latência média: {resultado_ping['latencia_media_ms']} ms")
    print(f"Jitter: {resultado_ping['jitter_ms']} ms")
    print(f"Perda de pacotes: {resultado_ping['perda_pct']}%")

    porta = input("\nDigite a porta TCP para testar (Enter para pular): ").strip()
    if porta:
        print(f"\n--- Teste de Porta {porta} ---")
        aberta = testar_porta(alvo, porta)
        if aberta is None:
            print("Não foi possível resolver o host.")
        else:
            print(f"Porta {porta} está {'ABERTA' if aberta else 'FECHADA/filtrada'}")

    fazer_trace = input(
        "\nDeseja rastrear a rota até o destino (tracert/traceroute)? (s/n): "
    ).strip().lower()
    if fazer_trace == 's':
        print("\n--- Rota até o destino ---")
        print(traceroute(alvo))


# =========================================================
# Chat P2P
# =========================================================

class Chat:
    """
    Gerencia uma conexão de chat já estabelecida (socket conectado).

    Ponto-chave que costuma quebrar essa funcionalidade:
    - Duas threads chamando input() ao mesmo tempo trava o terminal.
      Aqui, SOMENTE o envio roda no thread principal (via input());
      o recebimento roda em uma thread daemon separada.
    - O socket precisa ser fechado nos dois lados ao sair, senão a
      próxima tentativa de bind() falha com "Address already in use".
    """

    def __init__(self, sock, nickname):
        self.sock = sock
        self.nickname = nickname
        self.ativo = True

    def receber(self):
        while self.ativo:
            try:
                dados = self.sock.recv(BUFFER_SIZE)
                if not dados:
                    print("\n[Sistema] A outra pessoa encerrou a conexão.")
                    self.ativo = False
                    break
                mensagem = dados.decode('utf-8', errors='ignore')
                # Reimprime a linha de prompt depois de mostrar a mensagem recebida
                print(f"\r{' ' * 80}\r{mensagem}\n{self.nickname}> ", end='', flush=True)
            except (ConnectionResetError, ConnectionAbortedError, OSError):
                if self.ativo:
                    print("\n[Sistema] Conexão perdida.")
                self.ativo = False
                break

    def enviar(self):
        while self.ativo:
            try:
                texto = input(f"{self.nickname}> ")
            except (EOFError, KeyboardInterrupt):
                texto = "/sair"

            if not self.ativo:
                break

            if texto.strip().lower() == '/sair':
                try:
                    self.sock.sendall(f"[Sistema] {self.nickname} saiu do chat.".encode('utf-8'))
                except Exception:
                    pass
                self.ativo = False
                break

            if texto == '':
                continue

            mensagem = f"{self.nickname}: {texto}"
            try:
                self.sock.sendall(mensagem.encode('utf-8'))
            except (BrokenPipeError, ConnectionResetError, OSError):
                print("\n[Sistema] Não foi possível enviar. Conexão perdida.")
                self.ativo = False
                break

    def iniciar(self):
        t_recv = threading.Thread(target=self.receber, daemon=True)
        t_recv.start()
        self.enviar()  # roda no thread principal (necessário para input() funcionar bem)
        self.ativo = False
        try:
            self.sock.close()
        except Exception:
            pass
        time.sleep(0.3)
        print("[Sistema] Chat encerrado.")


def hospedar_chat(nickname, porta=CHAT_PORT):
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        servidor.bind(('0.0.0.0', porta))
        servidor.listen(1)
    except OSError as e:
        print(f"Erro ao abrir a porta {porta}: {e}")
        print("Dica: verifique se a porta já está em uso ou se o firewall está bloqueando.")
        return

    ip_local = obter_ip_local()
    print(f"\n[Sistema] Sala aberta! Compartilhe seu IP: {ip_local}  |  Porta: {porta}")
    print("[Sistema] Aguardando conexão... (Ctrl+C para cancelar)\n")

    try:
        conexao, endereco = servidor.accept()
    except KeyboardInterrupt:
        print("\n[Sistema] Cancelado.")
        servidor.close()
        return

    print(f"[Sistema] {endereco[0]} conectou-se! Digite /sair para encerrar.\n")
    servidor.close()  # não aceita mais novas conexões nessa sessão

    chat = Chat(conexao, nickname)
    chat.iniciar()


def entrar_chat(nickname, ip_alvo, porta=CHAT_PORT):
    cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print(f"\n[Sistema] Conectando a {ip_alvo}:{porta}...")
    try:
        cliente.settimeout(10)
        cliente.connect((ip_alvo, porta))
        cliente.settimeout(None)
    except (ConnectionRefusedError, socket.timeout) as e:
        print(f"[Sistema] Não foi possível conectar: {e}")
        print("Dica: confirme se o outro lado está com o chat hospedado (opção 2),")
        print("se o IP está correto e se a porta 50000 não está bloqueada no firewall/roteador.")
        return
    except Exception as e:
        print(f"[Sistema] Erro: {e}")
        return

    print("[Sistema] Conectado! Digite /sair para encerrar.\n")
    chat = Chat(cliente, nickname)
    chat.iniciar()


# =========================================================
# Menu principal
# =========================================================

def menu_principal():
    limpar_tela()
    print("=" * 50)
    print("   DIAGNÓSTICO & CHAT DE REDE".center(50))
    print("=" * 50)

    nickname = input("\nDigite seu Nickname: ").strip() or "Anônimo"
    input("Digite uma chave de sessão (apenas cosmético, Enter para pular): ")

    diagnostico_completo()

    while True:
        print("\n" + "-" * 50)
        print("[ 1 ] Testar uma conexão (IP/domínio + porta)")
        print("[ 2 ] Hospedar chat (aguardar conexão)")
        print("[ 3 ] Conectar ao chat de um amigo")
        print("[ 0 ] Sair")
        opcao = input("\nEscolha uma opção: ").strip()

        if opcao == '1':
            menu_teste_conexao()
        elif opcao == '2':
            hospedar_chat(nickname)
        elif opcao == '3':
            ip_amigo = input("Digite o IP do seu amigo: ").strip()
            if ip_amigo:
                entrar_chat(nickname, ip_amigo)
        elif opcao == '0':
            print("Até mais!")
            break
        else:
            print("Opção inválida.")


if __name__ == '__main__':
    try:
        menu_principal()
    except KeyboardInterrupt:
        print("\n\nPrograma encerrado pelo usuário.")
        sys.exit(0)
