# web_server

[![Python application](https://github.com/Dosimagem/web_server_backend/actions/workflows/CI.yml/badge.svg)](https://github.com/Dosimagem/web_server_backend/actions/workflows/CI.yml)

Aplicação responsável por receber as requisições dos usuários.

Especificação: [link](https://github.com/Dosimagem/web_server/tree/main/spec)

# Index

  - [1) Status](#1-status)
  - [2) Rotas](#2-rotas)
    - [2.1) Rota de cadastro](#21-rota-de-cadastro)
    - [2.2) Rota de login](#22-rota-de-login)
    - [2.3) Rota para obter informações do usuário](#23-rota-informações-do-usuario)
    - [2.4) Rota para listar todas as cotas para aquele usuário](#24-rota-para-listar-todas-as-cotas-para-aquele-usuario)
    - [2.5) Rota para ler uma cota especifica daquele usuario](#25-rota-para-ler-uma-cota-especifica-daquele-usuario)
    - [2.6) Rota para atualizar uma cota específica daquele usuário](#26-rota-para-atualizar-uma-cota-específica-daquele-usuário)
    - [2.7) Rota para deletar uma cota específica daquele usuário](#27-rota-para-deletar-uma-cota-específica-daquele-usuário)
  - [3) Desenvolvimento](#3-desenvolvimento)
    - [3.1) Setup inicial](#31-setup-inicial)
    - [3.2) Rodando o servido](#32-rodando-o-servido)
    - [3.3) Rodando os teste](#33-rodando-os-teste)
    - [3.4) Área adminstrativa](#34-área-adminstrativa)
  - [4) Banco de dados](#4-banco-de-dados)
    - [4.1) Usando o postgres via docker](#41-usando-o-postgres-via-docker)
    - [4.2) Backup de todo o banco](#42-backup-de-todo-o-banco)
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
- POST /api/v1/login/
- GET /api/v1/users/\<uuid:user_id>/
- GET /api/v2/users/\<uuid:user_id>/quota/
- GET /api/v2/users/\<uuid:user_id>/quota/\<uuid:id_cota>/
- PATCH /api/v2/users/\<uuid:user_id>/quota/\<uuid:id_cota>/
- DELETE /api/v2/users/\<uuid:user_id>/quota/\<uuid:id_cota>/

---

### 2.1) Rota de cadastro

---

* POST /api/v1/register/

 Rota para registrar um usuario via o método post. Caso o `payload` seja válido e o usuario não exista esta rota ira salvar usuario e gera o `token`. O `email` foi usado como `username`. O código de sucesso é `201`

Corpo da requisição:

```json
{
  "name": "João Silva",
  "email": "test1@email.com",
  "confirm_email": "test1@email.com",
  "password1": "123456!!",
  "password2": "123456!!",
  "phone": "12323234",
  "institution": "UFRJ",
  "role": "Medico"
}
```

Corpo da reposta:

```json
{
  "id": "c8023f13-b259-4f50-809d-c969b2509ab6",
  "token": "6af2689dc22bc175a2e3eeea5cf7cf93fb3f6c83",
  "is_staff": false
}
```

---


### 2.2) Rota de login

---

* POST /api/v2/login/

Rota serve para obter o token de um usuario cadastrado. Caso o `payload` seja valido será retornado o `token`. O código de sucesso é `200`

Corpo da requisição:

```json
{
  "username": "test1@email.com",
  "password": "123456!!",
}
```

Exemplo de `curl`:

```console
curl --request POST \
  --url http://localhost:8000/api/v1/login/ \
  --header 'Content-Type: application/json' \
  --data '{
  "username": "test1@email.com",
  "password": "123456!!"
}'
```

Corpo da resposta:

```json
{
  "id": "6e6f86cc-644a-442e-80d6-471dba2dfc75",
  "token": "0323d4b041be5306f8b488ccc798cb5349e5fc73",
  "is_staff": false
}
```

---

### 2.3) Rota informações do usuario

---

* GET /api/v2/users/\<uuid:user_id>/

Rota para obter informação do usuario. É necessário passar o `token` de acesso no `Authorization` na forma `Bearer token` e `uuid` do usuário. O código de sucesso é `200`

Exemplo de `curl`:

```console
curl --request GET \
  --url http://localhost:8000/api/v1/users/6e6f86cc-644a-442e-80d6-471dba2dfc75/ \
  --header 'Authorization: Bearer 0323d4b041be5306f8b488ccc798cb5349e5fc73'
```

Corpo da resposta:

```json
{
  "name": "João Silva",
  "phone": "12323234",
  "role": "medico",
  "institution": "Ufrj",
  "email": "test1@email.com
}
```

---

### 2.4) Rota para listar todas as cotas para aquele usuario

---

* GET /api/v2/users/\<uuid:user_id>/quota/

Rota para listar a quotas do usuario. É necessário passar o `token` de acesso no `Authorization` na forma `Bearer token` e `uuid` do usuário. O código de sucesso é `200`

Exemplo de `curl`:

```console
curl --request GET \
  --url http://localhost:8000/api/v1/users/6e6f86cc-644a-442e-80d6-471dba2dfc75/quotas \
  --header 'Authorization: Bearer 0323d4b041be5306f8b488ccc798cb5349e5fc73'
```

Corpo da resposta:

```json
{
  "quotas": [
    {
      "id": "8f5462eb-2bfe-4007-8346-5346b2b547f2",
      "user_id": "6e6f86cc-644a-442e-80d6-471dba2dfc75",
      "amount": 10,
      "price": 30000.0,
      "service_type": "Dosimetria Clinica",
      "status_payment": "Confirmado",
      "created_at": "2022-08-30"
    },
    {
      "id": "d0d00117-04e7-42a7-9620-6beac2dabe8e",
      "user_id": "6e6f86cc-644a-442e-80d6-471dba2dfc75",
      "amount": 5,
      "price": 10000.0,
      "service_type": "Dosimetria Preclinica",
      "status_payment": "Analise",
      "created_at": "2022-08-30"
    }
  ]
}
```

---

### 2.5) Rota para ler uma cota especifica daquele usuario

---

* GET /api/v2/users/\<uuid:user_id>/quota/\<uuid:id_cota>/

Rota para ler uma quota específica do usuario. É necessário passar o `token` de acesso no `Authorization` na forma `Bearer token`, `uuid` do usuário e o `uuid` da cota. O código de sucesso é `200`

Exemplo de `curl`:

```console
curl --request GET \
  --url http://localhost:8000/api/v1/users/6e6f86cc-644a-442e-80d6-471dba2dfc75/quotas/8f5462eb-2bfe-4007-8346-5346b2b547f2/ \
  --header 'Authorization: Bearer 0323d4b041be5306f8b488ccc798cb5349e5fc73'
```

Corpo da resposta:

```json
{
  "id": "8f5462eb-2bfe-4007-8346-5346b2b547f2",
  "user_id": "6e6f86cc-644a-442e-80d6-471dba2dfc75",
  "amount": 10,
  "price": 30000.0,
  "service_type": "Dosimetria Clinica",
  "status_payment": "Confirmado",
  "created_at": "2022-08-30"
}
```

---

### 2.6) Rota para atualizar uma cota específica daquele usuário

---

* PATCH /api/v2/users/\<uuid:user_id>/quota/\<uuid:id_cota>

Rota para ler uma quota específica do usuario. É necessário passar o `token` de acesso no `Authorization` na forma `Bearer token`, `uuid` do usuário, o `uuid` da cota e o o `json`. Apenas é possivel fazer atualização no campo `amount`. O código de sucesso é `204`

Corpo da requisição:

```json
{
  "amount": 9,
}
```

Exemplo de `curl`:

```console
curl --request PATCH \
  --url http://localhost:8000/api/v1/users/66927692-b45b-4b85-89d3-71f1a8322fd5/quotas/56192a59-7719-4434-a6b5-210c69a541b0/ \
  --header 'Authorization: Bearer  89e411defaf79102c83085abb834b7583dfdb499' \
  --header 'Content-Type: application/json' \
  --data '{
	"amount": "9"
}'
```

Corpo da resposta:

```json
{
  "id": "8f5462eb-2bfe-4007-8346-5346b2b547f2",
  "user_id": "6e6f86cc-644a-442e-80d6-471dba2dfc75",
  "amount": 10,
  "price": 30000.0,
  "service_type": "Dosimetria Clinica",
  "status_payment": "Confirmado",
  "created_at": "2022-08-30"
}
```
---
### 2.7) Rota para deletar uma cota específica daquele usuário
---
* DELETE /api/v2/users/\<uuid:user_id>/quota/\<uuid:id_cota>

Rota para deletar uma quota específica do usuario. É necessário passar o `token` de acesso no `Authorization` na forma `Bearer token`, `uuid` do usuário e o `uuid` da cota. O código de sucesso é `204`


Exemplo de `curl`:

```console
curl --request DELETE \
  --url http://localhost:8000/api/v1/users/66927692-b45b-4b85-89d3-71f1a8322fd5/quotas/56192a59-7719-4434-a6b5-210c69a541b0/ \
  --header 'Authorization: Bearer  89e411defaf79102c83085abb834b7583dfdb499'
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
DATABASE_URL=postgres://seu_user_db:seu_password_db@localhost:5432/seu_db
```

Agora pode-se fazer a migração com o `db` selecionado:

```console
python manage.py migrate
```

Apos fazer o camando `migrate` para popular o banco com alguns dados basta:

```
python manage.py loaddata contib/db_initial.json
```

Os usuarios criado serão:

* Super Usuário:
  * email: `admin@admin.com`
  * senha: `admin`

* Usuario comum:
  * email: `user1@user.com`
  * senha: `123456!!`

* Usuario comum:
  * email: `user2@user.com`
  * senha: `123456@@`
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
postgres://api:apirest@localhost:5434/api
```
---

### 4.2) Backup de todo o banco:


```console
./manage.py dumpdata --exclude auth.permission --exclude contenttypes --indent 2 > db.json
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

```console
docker build --tag django_server:dosimagem .
docker run --name django_server -d -p 8000:8000 django_server:dosimagem
docker start django_server
```

---