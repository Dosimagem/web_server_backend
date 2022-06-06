# web_server

Aplicação responsável por receber as requisições dos usuários.

Especificação: [link](https://github.com/Dosimagem/web_server/tree/main/spec)

### 1) Status

Desenvolvimento das funcionalidades

- Usuários [ OK ]
  - Esqueceu a senha
  - Alteracao de informações do usuario 
- Serviços [ nOK ]


### 2) Informações técnicas

#### 2.1) Rotas

- <domain>/
- <domain>/accounts/signup/
- <domain>/accounts/login/
- <domain>/accounts/logout/
- <domain>/profile/

### 2.2) Docker

```console
docker build --tag django_server:dosimagem .
docker run --name django_server -d -p 8000:8000 django_server:dosimagem
docker start django_server
```

## 3) Desenvolvimento

### 3.1) Inicinando o ambiente de desenvolvimento

```
python -m venv .venv --upgrade-deps
source .venv/bin/active
pip install pip-tools
pip-sync requirements.txt requirements-dev.txt
cp contrib/env-sample .env
python manage.py runserver
```

### 3.1) Tests

```console
python manage.py test users.tests.SignUpFormTests
python manage.py test users.tests.SignupViewsTests
```

### 3.2) Dependências

As dependêcias do projeto foram gerencias usando o **pip-tools** e **pip**.

Criando o ambiente:

```console
python -m venv .venv --upgrade-deps
source .venv/bin/active
pip install pip-tools
```

Intalando as dependências de desenvolvimento:

```console
pip-sync requirements.txt requirements-dev.txt
```

Atualizando a lista de dependências com o **pip-tools**:

```console
pip-compile --generate-hashes requirements.in
pip-compile --generate-hashes requirements-dev.in
```

### 3.3) Python-decouple

A lib python-decouple serve para gerenciar diferentes ambientes. Primiro ela procura as variaveis de ambiente no arquivo .env, caso não encontre ela procura na varicaveis de ambiente do sistema.

Um exemplo .env pode ser encontrado na pasta contrib.

```console
SECRET_KEY=Sua chave secreta aqui!
DEBUG=False
ALLOWED_HOSTS=127.0.0.1,localhost
```
