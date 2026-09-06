# Ferramenta de Rede

Script em Python com um menu interativo que reúne várias utilidades de diagnóstico de rede: consulta de IP, gateway, DNS, tracert, jitter, nslookup e um chat simples entre máquinas na mesma rede.

## Funcionalidades

1. **Mostrar IP** — exibe o IP local (da rede interna) e o IP público (via [ipify](https://www.ipify.org/)).
2. **Mostrar Gateway** — identifica o gateway padrão (compatível com Windows e Linux).
3. **Mostrar DNS** — lista os servidores DNS configurados (compatível com Windows e Linux).
4. **Executar Tracert** — roda `tracert` (Windows) ou `traceroute` (Linux) até um destino.
5. **Executar Jitter** — calcula o jitter médio (variação de latência) a partir de múltiplos pings.
6. **Executar Nslookup** — consulta a resolução DNS de um domínio.
7. **Chat** — troca mensagens em tempo real com outra máquina na mesma rede, via socket TCP.

## Requisitos

- Python 3.7 ou superior
- Sistema operacional: Windows ou Linux
  - No Linux, o comando `traceroute` precisa estar instalado (`sudo apt install traceroute` em distribuições baseadas em Debian/Ubuntu)
- Conexão com a internet (para IP público e tracert/nslookup com destinos externos)

Não é necessário instalar nenhuma biblioteca externa — o script usa apenas módulos nativos do Python (`socket`, `urllib`, `subprocess`, `sys`, `re`, `threading`).

## Como executar

```bash
python redes.py
```

Isso abre o menu interativo:

```
===== FERRAMENTA DE REDE =====
1 - Mostrar IP (Local e Público)
2 - Mostrar Gateway
3 - Mostrar DNS
4 - Executar Tracert
5 - Executar Jitter
6 - Executar Nslookup
7 - Iniciar Chat
0 - Sair
===============================
```

Basta digitar o número da opção desejada e seguir as instruções exibidas.

## Como testar o Chat

O chat funciona com duas instâncias do script rodando ao mesmo tempo — uma "escuta" mensagens enquanto a outra se conecta a ela.

### Testando na mesma máquina (sem precisar de outro PC)

1. Abra dois terminais.
2. Em cada um, rode `python redes.py` e escolha a opção **7**.
3. Quando pedir o IP de destino, use `127.0.0.1` nos dois.

> ⚠️ **Atenção:** como o código atual escuta e conecta na mesma porta (5000) para ambas as pontas, rodar duas instâncias na mesma máquina pode gerar erro de "porta em uso". Para testar localmente, ajuste a função `iniciarChat` para aceitar uma porta de escuta e uma porta de destino separadas, e use portas diferentes em cada terminal (ex: 5000 e 5001).

### Testando entre dispositivos diferentes

1. As duas máquinas precisam estar na **mesma rede** (mesmo Wi-Fi/LAN).
2. Descubra o IP local de cada uma (opção 1 do menu).
3. Libere a porta 5000 no firewall, se necessário.
4. Em cada máquina, rode o script e escolha a opção 7, informando o IP da outra máquina como destino.

Para rodar em celular ou tablet, é necessário um interpretador Python, como [Termux](https://termux.dev/) ou **Pydroid 3** (Android).

## Limitações conhecidas

- O parsing de `ipconfig` (gateway e DNS) foi construído para saídas em português e inglês; outros idiomas do Windows podem não ser reconhecidos corretamente.
- O cálculo de jitter depende do formato de saída do `ping`, que varia entre idiomas do sistema operacional (`tempo=` em PT-BR, `time=` em EN-US).
- O chat não possui criptografia nem autenticação — é indicado apenas para uso educacional em redes confiáveis.
- Não há suporte nativo a macOS nas funções de gateway e tracert.
