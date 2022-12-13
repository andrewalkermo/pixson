from __future__ import annotations
from re import match
from abc import abstractmethod

from pixson.enums import Operacoes, Resposta


class Protocolo:
    pattern = None

    @abstractmethod
    def encapsular(self) -> str:
        """
        Encapsula o objeto numa ‘string’.
        """
        pass

    @staticmethod
    @abstractmethod
    def desencapsular(mensagem: str) -> Protocolo:
        """
        Desencapsula a mensagem num objeto.
        :param mensagem: Mensagem a ser desencapsulada.
        :type mensagem: str
        """
        pass


class OperacaoSaldo(Protocolo):
    pattern = '^op:1\|rg:([0-9]{1,10})$'

    def __init__(self, rg: str):
        self.rg = rg

    def encapsular(self) -> str:
        return "op:{}|rg:{}".format(Operacoes.SALDO.value, self.rg)

    @staticmethod
    def desencapsular(mensagem: str) -> OperacaoSaldo:
        rg = match(OperacaoSaldo.pattern, mensagem).groups()[0]
        return OperacaoSaldo(rg=str(rg))


class OperacaoSaque(Protocolo):
    pattern = r'^op:2\|rg:([0-9]{1,10})\|valor:(.*)$'

    def __init__(self, rg: str, valor: float):
        self.rg = rg
        self.valor = valor

    def encapsular(self) -> str:
        return "op:{}|rg:{}|valor:{}".format(Operacoes.SAQUE.value, self.rg, self.valor)

    @staticmethod
    def desencapsular(mensagem: str) -> OperacaoSaque:
        rg, valor = match(OperacaoSaque.pattern, mensagem).groups()
        return OperacaoSaque(rg=str(rg), valor=float(valor))


class OperacaoDeposito(Protocolo):
    pattern = r'^op:3\|rg:([0-9]{1,10})\|valor:(.*)$'

    def __init__(self, rg: str, valor: float):
        self.rg = rg
        self.valor = valor

    def encapsular(self) -> str:
        return "op:{}|rg:{}|valor:{}".format(Operacoes.DEPOSITO.value, self.rg, self.valor)

    @staticmethod
    def desencapsular(mensagem: str) -> OperacaoDeposito:
        rg, valor = match(OperacaoDeposito.pattern, mensagem).groups()
        return OperacaoDeposito(rg=str(rg), valor=float(valor))


class OperacaoTransferencia(Protocolo):
    pattern = r'^op:4\|rg_origem:([0-9]{1,10})\|rg_destino:([0-9]{1,10})\|valor:(.*)$'

    def __init__(self, rg_origem: str, rg_destino: str, valor: float):
        self.rg_origem = rg_origem
        self.rg_destino = rg_destino
        self.valor = valor

    def encapsular(self) -> str:
        return "op:{}|rg_origem:{}|rg_destino:{}|valor:{}".format(
            Operacoes.TRANSFERENCIA.value,
            self.rg_origem,
            self.rg_destino,
            self.valor
        )

    @staticmethod
    def desencapsular(mensagem: str) -> OperacaoTransferencia:
        rg_origem, rg_destino, valor = match(OperacaoTransferencia.pattern, mensagem).groups()
        return OperacaoTransferencia(
            rg_origem=str(rg_origem),
            rg_destino=str(rg_destino),
            valor=float(valor)
        )


class OperacaoLogin(Protocolo):
    pattern = r'^op:6\|rg:([0-9]{1,10})$'

    def __init__(self, rg: str):
        self.rg = rg

    def encapsular(self) -> str:
        return "op:{}|rg:{}".format(Operacoes.LOGIN.value, self.rg)

    @staticmethod
    def desencapsular(mensagem: str) -> OperacaoLogin:
        rg = match(OperacaoLogin.pattern, mensagem).groups()[0]
        return OperacaoLogin(rg=str(rg))


class RespostaSucesso(Protocolo):
    pattern = r'^s:0\|resposta:(.*)$'

    def __init__(self, resposta: str):
        self.resposta = resposta

    def encapsular(self) -> str:
        return "s:{}|resposta:{}".format(Resposta.OK.value, self.resposta)

    @staticmethod
    def desencapsular(mensagem: str) -> RespostaSucesso:
        resposta = match(RespostaSucesso.pattern, mensagem).groups()[0]
        return RespostaSucesso(resposta=str(resposta))


class RespostaErro(Protocolo):
    pattern = r'^s:1\|resposta:(.*)$'

    def __init__(self, resposta: str):
        self.resposta = resposta

    def encapsular(self) -> str:
        return "s:{}|resposta:{}".format(Resposta.ERRO.value, self.resposta)

    @staticmethod
    def desencapsular(mensagem: str) -> RespostaErro:
        resposta = match(RespostaErro.pattern, mensagem).groups()[0]
        return RespostaErro(resposta=str(resposta))
