# Diagnóstico & Chat de Rede

Uma ferramenta de linha de comando (CLI) desenvolvida em Python que combina utilitários clássicos de diagnóstico de rede com um sistema de chat P2P (ponto a ponto) direto pelo terminal. 

Este script foi projetado para facilitar testes rápidos de conectividade, resolução de DNS e comunicação simples entre máquinas na mesma rede (ou pela internet, caso haja redirecionamento de portas).

## Funcionalidades

**1. Diagnóstico de Rede Completo**
*   **Identificação de IP:** Descobre automaticamente o IP local e o IP público da máquina.
*   **Configuração de Rede:** Captura o Gateway Padrão e os Servidores DNS locais.
*   **Análise de Ping:** Envia pacotes ICMP e calcula a latência média, o *jitter* (variação de latência) e a porcentagem de perda de pacotes.
*   **Teste de Porta:** Verifica se uma porta TCP específica está aberta ou fechada em um IP alvo.
*   **NSLookup & Tracert:** Realiza a resolução de nomes (DNS) e mapeia a rota (saltos) até o destino.

**2. Chat P2P Integrado**
*   **Modo Servidor (Criar Sala):** Abre a porta `50000` na máquina local para aguardar conexões.
*   **Modo Cliente (Entrar na Sala):** Conecta diretamente ao IP de um amigo para trocar mensagens no terminal em tempo real usando *threads*.

## Pré-requisitos

*   **Python 3.x** instalado.
*   **Sistema Operacional:** O código atual utiliza comandos nativos do Windows (`ipconfig`, `ping -n`, `tracert -h`, codificação `cp850`). Pode ser necessário adaptar as chamadas do `subprocess` para uso em sistemas Linux ou macOS.

## Como Usar

1. Clone o repositório ou baixe o arquivo `.py`.
2. Abra o terminal e navegue até a pasta do arquivo.
3. Execute o script:
   ```bash
   python nome_do_arquivo.py
   ```
4. Insira seu *Nickname* e uma chave de sessão quando solicitado.
5. Escolha a ação desejada no menu principal:
   * **[ 1 ]** Para testar uma conexão (requer um IP ou domínio e uma porta).
   * **[ 2 ]** Para hospedar um chat e esperar alguém conectar no seu IP.
   * **[ 3 ]** Para conectar ao chat de um amigo usando o IP dele.

## Aviso Legal
Esta é uma ferramenta educacional e de diagnóstico. Use as opções de teste de porta e envio de pacotes apenas em redes e servidores nos quais você tem permissão para realizar testes.
