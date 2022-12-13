from __future__ import annotations

import time
import signal
import socket
import select
import threading

from pixson import utils
from pixson.protocolo import *
from pixson.conta import Conta

PORTA_PADRAO = 5000

lock = threading.Lock()


class Servidor:
    def __init__(self) -> None:
        """
        Contrutor da classe Servidor.
        """
        if not utils.verificar_porta(porta=PORTA_PADRAO):
            print('Porta já está em uso')
            exit()

        self.porta = PORTA_PADRAO
        self.socket = None
        self.clientes = []
        self.relogio = 0
        self.disponivel = False

    def atualizar_relogio_interno(self) -> None:
        """
        Atualiza o relógio interno do cliente.
        """
        while self.disponivel:
            self.relogio += 1
            time.sleep(1)

    def iniciar(self) -> None:
        """
        Inicia o servidor.
        """
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind(('', self.porta))
        self.socket.listen(1)
        self.disponivel = True
        threading.Thread(target=self.atualizar_relogio_interno).start()
        print(f"Servidor iniciado na porta {self.porta}")

    def aceitar_conexao(self) -> None:
        """
        Aceita uma conexão de um cliente e processa as mensagens dele, numa nova thread.
        """
        cliente_socket, cliente_socket_host = self.socket.accept()
        self.clientes.append(cliente_socket)
        print(f"Novo cliente conectado {cliente_socket_host}")
        server_thread = threading.Thread(target=self.processar_operacoes_cliente, args=(cliente_socket,))
        server_thread.start()

    def processar_operacoes_cliente(self, cliente_socket) -> None:
        """
        Processa as operações do cliente.
        :param cliente_socket: Socket do cliente.
        :type cliente_socket: socket.socket
        """
        while self.disponivel:
            try:
                ready_to_read, ready_to_write, in_error = select.select(
                    [cliente_socket, ],
                    [cliente_socket, ],
                    [],
                    5
                )
            except select.error:
                cliente_socket.shutdown(2)
                cliente_socket.close()
                print('erro de conexão')
                break
            if len(ready_to_read) > 0:
                mensagem = cliente_socket.recv(utils.TAMANHO_BUFFER_PADRAO).decode()
                if mensagem:
                    processar_operacao(cliente_socket=cliente_socket, comando=mensagem)
                else:
                    break
            if len(ready_to_write) > 0:
                pass
            if len(in_error) > 0:
                break

        cliente_socket.close()
        self.clientes.remove(cliente_socket)
        print('Cliente desconectado')

    def encerrar(self) -> None:
        """
        Encerra o servidor.
        """
        print('Encerrando...')
        self.desconectar()
        exit()

    def desconectar(self) -> None:
        """
        Desconecta o servidor.
        """
        self.disponivel = False
        for cliente in self.clientes:
            cliente.shutdown(2)
            cliente.close()
        self.socket.close()

    @staticmethod
    def criar() -> Servidor:
        """
        Cria uma instância do servidor.
        :rtype: Servidor
        """
        servidor = Servidor()
        servidor.iniciar()

        signal.signal(signal.SIGINT, lambda signum, frame: servidor.encerrar())
        return servidor


def processar_operacao_saldo(cliente_socket, comando: str) -> None:
    """
    Processa a operação de saldo.
    :param cliente_socket: Socket do cliente.
    :type cliente_socket: socket.socket
    :param comando: Comando recebido do cliente.
    :type comando: str
    """
    solicitacao = OperacaoSaldo.desencapsular(comando)
    rg = str(solicitacao.rg)

    with lock:
        conta = Conta.obter_conta(rg=rg)
        if conta:
            resposta = RespostaSucesso(f"Saldo: {conta.saldo}")
        else:
            resposta = RespostaErro('Cliente não encontrado')
        cliente_socket.send(resposta.encapsular().encode())


def processar_operacao_saque(cliente_socket, comando: str) -> None:
    """
    Processa a operação de saque.
    :param cliente_socket: Socket do cliente.
    :type cliente_socket: socket.socket
    :param comando: Comando recebido do cliente.
    :type comando: str
    """
    solicitacao = OperacaoSaque.desencapsular(comando)
    rg = str(solicitacao.rg)

    with lock:
        conta = Conta.obter_conta(rg=rg)
        if conta:
            if conta.saldo >= solicitacao.valor:
                conta.sacar(valor=solicitacao.valor)
                resposta = RespostaSucesso('Saque realizado com sucesso')
            else:
                resposta = RespostaErro('Saldo insuficiente')
        else:
            resposta = RespostaErro('Cliente não encontrado')
        cliente_socket.send(resposta.encapsular().encode())


def processar_operacao_deposito(cliente_socket, comando: str) -> None:
    """
    Processa a operação de depósito.
    :param cliente_socket: Socket do cliente.
    :type cliente_socket: socket.socket
    :param comando: Comando recebido do cliente.
    :type comando: str
    """
    solicitacao = OperacaoDeposito.desencapsular(comando)
    with lock:
        rg = str(solicitacao.rg)

        conta = Conta.obter_conta(rg=rg)
        if conta:
            conta.depositar(valor=solicitacao.valor)
            resposta = RespostaSucesso('Depósito realizado com sucesso')
        else:
            resposta = RespostaErro('Cliente não encontrado')

        cliente_socket.send(resposta.encapsular().encode())


def processar_operacao_transferencia(cliente_socket, comando: str) -> None:
    """
    Processa a operação de transferência.
    :param cliente_socket: Socket do cliente.
    :type cliente_socket: socket.socket
    :param comando: Comando recebido do cliente.
    :type comando: str
    """
    solicitacao = OperacaoTransferencia.desencapsular(comando)

    if solicitacao.rg_origem == solicitacao.rg_destino:
        resposta = RespostaErro('Não é possível transferir para a mesma conta')
        cliente_socket.send(resposta.encapsular().encode())
        return

    with lock:
        conta_origem = Conta.obter_conta(rg=solicitacao.rg_origem)
        conta_destino = Conta.obter_conta(rg=solicitacao.rg_destino)

        if conta_origem is None:
            resposta = RespostaErro('Conta de origem não encontrada')
            cliente_socket.send(resposta.encapsular().encode())
            return
        if conta_destino is None:
            resposta = RespostaErro('Conta de destino não encontrada')
            cliente_socket.send(resposta.encapsular().encode())
            return
        if conta_origem.saldo < solicitacao.valor:
            resposta = RespostaErro('Saldo insuficiente')
            cliente_socket.send(resposta.encapsular().encode())
            return

        conta_origem.transferir(conta_destino=conta_destino, valor=solicitacao.valor)
        resposta = RespostaSucesso('Transferência realizada com sucesso')
        cliente_socket.send(resposta.encapsular().encode())
        return


def processar_operacao_login(cliente_socket, comando: str) -> None:
    """
    Processa a operação de login.
    :param cliente_socket: Socket do cliente.
    :type cliente_socket: socket.socket
    :param comando: Comando recebido do cliente.
    :type comando: str
    """
    solicitacao = OperacaoLogin.desencapsular(comando)
    rg = str(solicitacao.rg)
    conta = Conta.obter_conta(rg=rg)
    if conta:
        resposta = RespostaSucesso('Login realizado com sucesso')
    else:
        resposta = RespostaErro('Cliente não encontrado')
    cliente_socket.send(resposta.encapsular().encode())


def processar_operacao(cliente_socket, comando: str) -> None:
    """
    Processa o comando do cliente.
    :param cliente_socket: Socket do cliente.
    :type cliente_socket: socket.socket
    :param comando: Comando recebido do cliente.
    :type comando: str
    :rtype: None
    """
    if match(pattern=OperacaoSaldo.pattern, string=comando):
        processar_operacao_saldo(cliente_socket, comando)
    elif match(pattern=OperacaoSaque.pattern, string=comando):
        processar_operacao_saque(cliente_socket, comando)
    elif match(pattern=OperacaoDeposito.pattern, string=comando):
        processar_operacao_deposito(cliente_socket, comando)
    elif match(pattern=OperacaoTransferencia.pattern, string=comando):
        processar_operacao_transferencia(cliente_socket, comando)
    elif match(pattern=OperacaoLogin.pattern, string=comando):
        processar_operacao_login(cliente_socket, comando)
    else:
        resposta = RespostaErro('Comando não reconhecido')
        cliente_socket.send(resposta.encapsular().encode())


def main():
    """
    Função principal.
    """
    servidor = Servidor.criar()
    print('Aguardando conexão...')
    while servidor.disponivel:
        servidor.aceitar_conexao()


if __name__ == '__main__':
    main()
    exit()
