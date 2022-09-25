# web_server

[![Python application](https://github.com/Dosimagem/web_server_backend/actions/workflows/CI.yml/badge.svg)](https://github.com/Dosimagem/web_server_backend/actions/workflows/CI.yml)

Aplicação responsável por receber as requisições dos usuários.

Especificação: [link](https://github.com/Dosimagem/web_server/tree/main/spec)

# Index

  - [1) Status](#1-status)
  - [2) Rotas](#2-rotas)
  - [3) Desenvolvimento](#3-desenvolvimento)
    - [3.1) Setup inicial](#31-setup-inicial)
    - [3.2) Rodando o servido](#32-rodando-o-servido)
    - [3.3) Rodando os teste](#33-rodando-os-teste)
    - [3.4) Área adminstrativa](#34-área-adminstrativa)
  - [4) Banco de dados](#4-banco-de-dados)
    - [4.1) Usando o postgres via docker](#41-usando-o-postgres-via-docker)
    - [4.2) Backup do banco](#42-backup-do-banco)
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

- Isotopos
  - GET api/v1/isotopes/
- Register
  - POST /api/v1/users/register/
  - POST /api/v1/users/login/
- Users
  - GET /api/v1/users/\<uuid:user_id>
  - PATCH /api/v1/users/\<uuid:user_id>
- Order
  - GET /api/v1/users/\<uuid:user_id>/orders/
  - GET /api/v1/users/\<uuid:user_id>/orders/\<uuid:id_order>
- Calibration
  - GET /api/v1/users/\<uuid:user_id>/calibrations/
  - POST /api/v1/users/\<uuid:user_id>/calibrations/
  - DELETE /api/v1/users/\<uuid:user_id>/calibrations/\<uuid:cali_id>
  - PUT /api/v1/users/\<uuid:user_id>/calibrations/\<uuid:cali_id>
  - GET /api/v1/users/\<uuid:user_id>/calibrations/\<uuid:cali_id>
- Analises
  - GET /api/v1/users/\<uuid:user_id>/orders/\<uuid:order_id>/analysis/
  - POST /api/v1/users/\<uuid:user_id>/orders/\<uuid:order_id>/analysis/

Detalhes das rotas: [ROTAS.md](ROTAS.md)


## 3) Desenvolvimento


### 3.1) Setup inicial
---

O setup incicial necessário fazer apenas `uma vez`.

```console
python -m venv .venv --upgrade-deps
source .venv/bin/activate
pip install pip-tools
pip-sync requirements.txt requirements-dev.txt
cp contrib/env-sample .env
```

Para usar o `sqlite` o arquivo `.env` fica assim:

```consolse
DEBUG=True
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
DATABASE_URL=postgres://seu_user_db:seu_password_db@localhost:port/seu_db
```

Os valores `seu_user_db`, `seu_password_db`, `port` e `seu_db` podem ser respectivamente `dosimagem`,  `dosimagem`, `5434`e `dosimagem_db`. Para user o postgres utilizando o `docker` basta olhar aqui: [Usando o postgres via docker](#41-usando-o-postgres-via-docker).

Agora pode-se fazer a migração com o `db` selecionado:

```console
python manage.py migrate
```

Após fazer o camando `migrate` para popular o banco com alguns de usuario e isotopos basta fazer:

```console
python manage.py loaddata contrib/db_initial.json
```

Os usuarios criados serão:

* Super Usuário:
  * email: `admin@admin.com`
  * senha: `admin`

* Usuario comum:
  * email: `user1@email.com`
  * senha: `123456!!`

* Usuario comum:
  * email: `user2@email.com`
  * senha: `123456!!`

Para apenas popular com as informações do `isotopos` basta fazer:

```console
python manage.py loaddata contrib/db_isotope.json
```

---

### 3.2) Rodando o servido de desenvolvimento

---

```console
python manage.py runserver
```

É bom utilizar `DEBUG=True` para que o `django` sirva os arquivos estáticos.

---

### 3.3) Rodando os teste
___

Rodando os testes com o `pytest`

```console
pytest -vv
```

Para ver a cobertura de testes

```
pytest --cov=web_server --cov-report html
```
___

### 3.4) Área adminstrativa

Para acessar usar o `admin` é preciso criar um super usuário, para tal basta usar o comando:

```console
python manage.py createsuperuser
```

A rota para acessar é `/dosimagem/admin/`

---

## 4) Banco de dados

---

### 4.1) Usando o postgres via docker

---

Subir o container

```console
docker-compose -f docker-compose.yml up -d
```

Configurar `DATABASE_URL` no arquivo `.env` para

```
postgres://dosimagem:dosimagem@localhost:5434/dosimagem_db
```
---

### 4.2) Backup do banco:


Todo o banco

```console
./manage.py dumpdata --exclude auth.permission --exclude contenttypes --indent 2 > contrib/db_initial.json
```

Apenas dos `Isotopos` cadastrados

```console
./manage.py ./manage.py dumpdata service.Isotope --indent 2 > contrib/db_isotope.json
```


### 5) Python decouple

---

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

---

### 6) Docker

---

Docker com ambiente de desenvolvimento.

```console
docker-compose -f docker/compose/docker-compose-api-db.yml build
```

Subindo o servidor e o banco de dados

```console
docker-compose -f docker/compose/docker-compose-api-db.yml up
```

O `DATABASE_URL` esta definido dentro do docker compose. Para fazer a migração e a carga inicial basta

```
docker exec -it dosimagem_api python manage.py migrate
docker exec -it dosimagem_api ./manage.py loaddata contrib/db_initial.json
```

---
