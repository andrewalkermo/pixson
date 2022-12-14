# PIXSON  
Sistema Distribuído Simples para Manutenção de Contas Bancárias, utilizando arquitetura cliente-servidor, com comunicação via sockets TCP/IP.  
  
  
## Operações  
  
### Operações de Conta  
  
- Login  
- Consulta de Saldo  
- Saque  
- Depósito  
- Transferência  
  
## Requisitos  
  
- Python >= 3.8  
  
## Execução  
  
### Servidor  
  
- Iniciar o servidor: `PYTHONPATH=$(pwd) python3.8 pixson/servidor.py`  
  
Por padrão, o servidor irá iniciar na porta 5000.  
  
### Cliente  
  
- Iniciar o cliente: `PYTHONPATH=$(pwd) python3.8 pixson/cliente.py`  
  
Por padrão, o cliente irá iniciar se conectando ao servidor com o host `localhost` e porta `5000`.  
  
## Funcionamento  
  
### Servidor  
  
#### processamento  
  
Cada conexão TCP/IP com os clientes é tratada em uma thread separada, para permitir que o servidor atenda múltiplos clientes simultaneamente.  
  
#### Armazenamento  
  
O servidor é responsável por gerir as contas bancárias e as operações realizadas por elas. Para isso, ele mantém cada conta num arquivo JSON, com o nome do arquivo sendo o número no RG do usuário.  
  
O acesso a esses arquivos é feito de forma concorrente, utilizando o módulo `threading.Lock` para garantir que apenas uma thread tenha acesso ao arquivo por vez.  
  
Exemplo de arquivo de conta:  
```json
{  
    "nome": "João da Silva",
    "rg": "123456789",
    "saldo": 1000.0
}  
```  
Já existem alguns arquivos de exemplo no diretório `contas/` que podem ser utilizados para testes.  
  
### Cliente  
  
#### Operações  
  
O cliente é responsável por enviar as requisições ao servidor e receber as respostas. Para isso, ele utiliza o módulo `socket` para se conectar ao servidor e enviar as requisições.  
  
### Protocolo  
  
A comunicação entre o cliente e o servidor é por mensagens de texto, cada uma representando uma operação. As classes que representam as mensagens estão no módulo `pixson.recursos.protocolo`, onde cada classe representa uma mensagem.  
  
Exemplo de mensagem de solicitação de transferência de 10.5 da conta 123456789 para a 987654321, no tempo lógico 10:  
  
> t:10|op:4|rg_origem:1111111111|rg_destino:987654321|valor:10.5  
  
### Relógio Lógico  
  
Foi implementado um relógio lógico, baseado no algoritmo de Lamport, para identificar a ordem das operações. O cliente e servidor iniciam com o relógio lógico zerado, e cada operação incrementa o relógio lógico em 1.  
Todas as mensagens enviadas pelo cliente e servidor possuem um carimbo com o valor do relógio lógico atualizado. Quando uma nova mensagem é recebida, o relógio lógico do receptor é atualizado para o maior valor entre o relógio lógico e o carimbo da mensagem recebida.  
  
  
## Exemplo de Execução  
  
Para todos os exemplos a seguir, o servidor e cliente já devem estar em execução.   
  
#### Servidor  
  
```bash  
$ PYTHONPATH=$(pwd) python3.8 pixson/servidor.py  
Servidor iniciado na porta 5000  
Aguardando conexão  
```  
  
#### Cliente  
```bash  
$ PYTHONPATH=$(pwd) python3.8 pixson/cliente.py  
Cliente iniciado  
```  
  
### Login  
  
Realizar login com o RG 1111111111  
  
```bash
Digite o RG associado a conta: 1111111111  
Conectado ao servidor  
Relógio Lógico Atualizado: 1  
Relógio Lógico Atualizado: 4  
Login realizado com sucesso  
```  
  
### Consulta de Saldo  
  
Consultar saldo, digitando a opção 1  
  
```bash
1 - SALDO  
2 - SAQUE  
3 - DEPOSITO  
4 - TRANSFERENCIA  
0 - SAIR  
  
Digite o comando: 1  
Relógio Lógico Atualizado: 5  
Relógio Lógico Atualizado: 8  
Saldo: 10.0  
```  
  
### Saque  
  
Realizar saque, digitando a opção 2 e informando o valor 8.50  
  
```bash  
1 - SALDO  
2 - SAQUE  
3 - DEPOSITO  
4 - TRANSFERENCIA  
0 - SAIR  
  
Digite o comando: 2  
Digite o valor do saque: 8.50  
Relógio Lógico Atualizado: 9  
Relógio Lógico Atualizado: 12  
Saque realizado com sucesso  
```  
  
### Depósito  
  
Realizar depósito, digitando a opção 3 e informando o valor 14  
  
```bash 
1 - SALDO  
2 - SAQUE  
3 - DEPOSITO  
4 - TRANSFERENCIA  
0 - SAIR  
  
Digite o comando: 3  
Digite o valor do deposito: 14  
Relógio Lógico Atualizado: 13  
Relógio Lógico Atualizado: 16  
Depósito realizado com sucesso  
```  
  
### Transferência  
  
Realizar transferência, digitando a opção 4 e informando o RG 2222222222 da conta de destino e o valor 5.5  
  
```bash
1 - SALDO  
2 - SAQUE  
3 - DEPOSITO  
4 - TRANSFERENCIA  
0 - SAIR  
  
Digite o comando: 4  
Digite o RG do destinatário: 2222222222  
Digite o valor da transferência: 5.5  
Relógio Lógico Atualizado: 17  
Relógio Lógico Atualizado: 20  
Transferência realizada com sucesso  
```