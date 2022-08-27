# web_server

[![Python application](https://github.com/Dosimagem/web_server_backend/actions/workflows/CI.yml/badge.svg)](https://github.com/Dosimagem/web_server_backend/actions/workflows/CI.yml)

Aplicação responsável por receber as requisições dos usuários.

Especificação: [link](https://github.com/Dosimagem/web_server/tree/main/spec)

# Index

  - [1) Status](#1-status)
  - [2) Rotas](#2-rotas)
    - [2.1) Rota de cadastro](#21-rota-de-cadastro)
    - [2.2) Rota de login](#22-rota-de-login)
  - [3) Desenvolvimento](#3-desenvolvimento)
    - [3.1) Setup inicial](#31-setup-inicial)
    - [3.2) Rodando o servido](#32-rodando-o-servido)
    - [3.3) Rodando os teste](#32-rodando-os-teste)
  - [4) Banco de dados](#4-banco-de-dados)
    - [4.1) Usando o postgres via docker](#41-usando-o-postgres-via-docker)
  - [5) Python decouple](#5-python-decouple)
  - [6) Docker](#6-docker)

# 1) Status

Desenvolvimento das funcionalidades

- Usuários [ OK ]
  - Esqueceu a senha
  - Alteracao de informações do usuario
- Serviços [ nOK ]


# 2) Rotas

Rotas disponiveis

- POST /api/v1/register/
- POST /api/v1/login

---

### 2.1) Rota de cadastro

---

* endpoint /api/v1/register/ - POST

 Rota para registrar um usuario via o método post. Caso o `payload` seja válido e o usuario não exista esta rota ira salvar usuario e gera o `token`. O `email` foi usado como `username`. Exemplo de requisição:

```json
{
  "name": "João Sliva",
  "email": "test1@email.com",
  "confirm_email": "test1@email.com",
  "password1": "123456!!",
  "password2": "123456!!",
  "phone": "12323234",
  "institution": "UFRJ",
  "role": "Medico"
}
```

> Reposta:

```json
{
  "id": 5,
  "token": "6af2689dc22bc175a2e3eeea5cf7cf93fb3f6c83",
  "is_staff": false
}
```

---


### 2.2) Rota de login

---

* /api/v2/login/ - POST

Rota serve para obter o token de um usuario cadastrado. Caso o `payload` seja valido será retornado o `token`. Exemplo de requisição:

```json
{
  "id": 3,
  "token": "d80052eb1154fdf07d5bf148a916c4fd849c11cb",
  "is_staff": false
}
```
---

## 3) Desenvolvimento


### 3.1) Setup inicial
---

O setup incicial necessário fazer apenas `uma vez`.

```console
python -m venv .venv --upgrade-deps
source .venv/bin/activate
pip install -r requirements.txt
cp contrib/env-sample .env
```

Para usar o `sqlite` o arquivo `.env` fica assim:

```consolse
DEBUG=False
SECRET_KEY=Sua chave secreta aqui!
ALLOWED_HOSTS=127.0.0.1,localhost
INTERNAL_IPS=127.0.0.1,localhost

#Config email

EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EMAIL_HOST=localhost
EMAIL_PORT=25
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
EMAIL_USE_TLS=True

#CORS
CORS_ALLOWED_ORIGINS=http://localhost:3000,127.0.0.1:3000
```

Para usar o `postgres` o arquivo `.env` fica assim basta adicionar a variável `DATABASE_URL`:

```console
DATABASE_URL=postgres://seu_user_db:seu_password_db@localhost:5432/seu_db
```

Agora pode-se fazer a migração com o `db` selecionado:

```console
python manage.py migrate
```

---

### 3.2) Rodando o servido de desenvolvimento

---

```console
python manage.py runserver
```

---

### 3.2) Rodando os teste

---

Rodando os testes com o `pytest`

```console
pytest -vv
```

Para ver a cobertura de testes

```
pytest --cov=web_server --cov-report html
```


---

## 4) Banco de dados

---

### 4.1) Usando o postgres via docker

---

Subir o container

```consolse
docker-compose -f docker-compose.yml up -d
```

Configurar `DATABASE_URL` no arquivo `.env` para

```
postgres://api:apirest@localhost:5434/api
```
---


### 5) Python decouple

A lib `python-decouple` serve para gerenciar diferentes ambientes. Primiro ela procura as variaveis de ambiente no arquivo `.env`, caso não encontre ela procura na varicaveis de `ambiente do sistema` isso possibilida uma grande flexibilidade de configurações.

Um exemplo .env pode ser encontrado na pasta contrib.

```console
DEBUG=False
SECRET_KEY=Sua chave secreta aqui!
ALLOWED_HOSTS=127.0.0.1,localhost
INTERNAL_IPS=127.0.0.1,localhost

#Config email

EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EMAIL_HOST=localhost
EMAIL_PORT=25
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
EMAIL_USE_TLS=True

#CORS
CORS_ALLOWED_ORIGINS=http://localhost:3000,127.0.0.1:3000
```

### 6) Docker

```console
docker build --tag django_server:dosimagem .
docker run --name django_server -d -p 8000:8000 django_server:dosimagem
docker start django_server
```
