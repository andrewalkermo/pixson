from __future__ import annotations
import sys
import socket
import signal

from pixson import utils
from pixson.protocolo import *

HOST_SERVIDOR = 'localhost'
PORTA_SERVIDOR = 5000


class Cliente:
    def __init__(self, rg: str) -> None:
        """
        Construtor da classe Cliente.
        :param rg: string com o RG do cliente.
        :type rg: str
        """
        self.rg = rg
        self.socket = None
        self.conectado = False
        self.relogio = 0

    def conectar(self) -> None:
        """
        Conecta o cliente ao servidor.
        """
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.socket.connect((HOST_SERVIDOR, PORTA_SERVIDOR))
            self.conectado = True
            print(f"Conectado ao servidor")
        except ConnectionRefusedError:
            print('Erro ao conectar ao servidor')
            self.encerrar()

    def desconectar(self) -> None:
        """
        Desconecta o cliente do servidor.
        """
        self.socket.close()
        self.conectado = False

    def encerrar(self) -> None:
        """
        Encerra o cliente.
        """
        print('Encerrando...')
        self.desconectar()
        exit()

    def enviar_mensagem(self, mensagem: str) -> None:
        """
        Envia uma mensagem para o servidor.
        :param mensagem: Mensagem a ser enviada.
        :type mensagem: str
        """
        if isinstance(mensagem, str):
            mensagem = mensagem.encode()
        self.socket.send(mensagem)

    def receber_mensagem(self) -> str:
        """
        Recebe uma mensagem do servidor.
        :rtype: object
        """
        return self.socket.recv(utils.TAMANHO_BUFFER_PADRAO).decode()

    def enviar_mensagem_e_imprimir_resposta(self, mensagem: str) -> None:
        """
        Envia uma mensagem para o servidor e imprime a resposta.
        :param mensagem:
        :type mensagem:
        """
        self.enviar_mensagem(mensagem)
        resposta = self.receber_mensagem()
        if match(RespostaSucesso.pattern, resposta):
            resposta = RespostaSucesso.desencapsular(resposta)
        elif match(RespostaErro.pattern, resposta):
            resposta = RespostaErro.desencapsular(resposta)
        print(resposta.resposta)

    @staticmethod
    def criar(args: list) -> Cliente | None:
        """
        Cria um cliente.
        :rtype: Cliente or None
        """
        rg = args[1] if len(args) > 1 else str(input('Digite o RG associado a conta: '))

        cliente = Cliente(rg)
        cliente.conectar()
        signal.signal(signal.SIGINT, lambda signum, frame: cliente.encerrar())

        cliente.enviar_mensagem(OperacaoLogin(rg).encapsular())
        resposta = cliente.receber_mensagem()
        if match(RespostaErro.pattern, resposta):
            resposta = RespostaErro.desencapsular(resposta)
            print(resposta.resposta)
            cliente.encerrar()
            return None
        elif match(RespostaSucesso.pattern, resposta):
            resposta = RespostaSucesso.desencapsular(resposta)
            print(resposta.resposta)
            return cliente

    def processar_comando_saldo(self) -> None:
        """
        Processa o comando de consulta de saldo.
        """
        mensagem = OperacaoSaldo(self.rg)
        self.enviar_mensagem_e_imprimir_resposta(mensagem=mensagem.encapsular())

    def processar_comando_saque(self) -> None:
        """
        Processa o comando de saque.
        """
        valor = float(input('Digite o valor do saque: '))
        mensagem = OperacaoSaque(self.rg, valor)
        self.enviar_mensagem_e_imprimir_resposta(mensagem=mensagem.encapsular())

    def processar_comando_deposito(self) -> None:
        """
        Processa o comando de depósito.
        """
        valor = float(input('Digite o valor do deposito: '))
        mensagem = OperacaoDeposito(self.rg, valor)
        self.enviar_mensagem_e_imprimir_resposta(mensagem=mensagem.encapsular())

    def processar_comando_transferencia(self) -> None:
        """
        Processa o comando de transferencia.
        """
        rg_destino = str(input('Digite o RG do destinatário: '))
        valor = float(input('Digite o valor da transferência: '))
        mensagem = OperacaoTransferencia(self.rg, rg_destino, valor)
        self.enviar_mensagem_e_imprimir_resposta(mensagem=mensagem.encapsular())


def main(args: list) -> None:
    """
    Função principal que inicia o cliente e processa os comandos.
    """
    cliente = Cliente.criar(args)

    if cliente is not None:
        while cliente.conectado:
            print('\n1 - SALDO\n2 - SAQUE\n3 - DEPOSITO\n4 - TRANSFERENCIA\n0 - SAIR\n')
            comando = input('Digite o comando: ')
            if isinstance(comando, str) and comando.isdigit():
                comando = int(comando)

            if comando == Operacoes.SALDO.value:
                cliente.processar_comando_saldo()
            elif comando == Operacoes.SAQUE.value:
                cliente.processar_comando_saque()
            elif comando == Operacoes.DEPOSITO.value:
                cliente.processar_comando_deposito()
            elif comando == Operacoes.TRANSFERENCIA.value:
                cliente.processar_comando_transferencia()
            elif comando == Operacoes.SAIR.value:
                break
            else:
                print('Comando inválido!')

        cliente.desconectar()


if __name__ == '__main__':
    main(sys.argv)
    exit()
