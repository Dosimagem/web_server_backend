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
    - [2.5) Rota para ler uma cota especifica daquele usuario](#25-rota-para-deletar-uma-cota-específica-daquele-usuário)
    - [2.6) Rota para ler os isotopos cadastrados](#26-rota-para-deletar-uma-cota-específica-daquele-usuário)
    - [2.7) Rota para lista as calibrações](#27-rota-para-listar-calibrações)
    - [2.8) Rota para cadastra uma calibração](#28-rota-para-cadastra-calibrações)
    - [2.9) Rota para atualizar uma calibração](#29-rota-para-atualizar-uma-calibração)
    - [2.10) Rota para deletar uma calibração](#210-rota-para-deletar-uma-calibração)
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

- Register
  - POST /api/v1/register/
  - POST /api/v1/login/
- Users
  - GET /api/v1/users/\<uuid:user_id>/
- Order
  - GET /api/v1/users/\<uuid:user_id>/order/
  - GET /api/v1/users/\<uuid:user_id>/order/\<uuid:id_order>/
- Calibration
  - GET /api/v1/users/\<uuid:user_id>/
  - POST /api/v1/users/\<uuid:user_id>/
  - DELETE /api/v1/users/\<uuid:user_id>/calibration/\<uuid:cali_id>
  - PUT /api/v1/users/\<uuid:user_id>/calibration/\<uuid:cali_id>

---

### 2.1) Rota de cadastro

---

* POST /api/v1/register/

 Rota para registrar um usuario via o método post. Caso o `payload` seja válido e o usuario não exista esta rota ira salvar usuario e gera o `token`. O `email` foi usado como `username`. O código de sucesso é `201`

Corpo da requisição:

```json
{
  "name": "João Silva",
  "email": "user1@user.com",
  "confirmEmail": "user1@user.com",
  "password1": "123456!!",
  "password2": "123456!!",
  "phone": "2222-2222",
  "institution": "UFRJ",
  "role": "Medico"
}
```

Corpo da reposta:

```json
{
  "id": "24d3b887-f903-44ca-bfcf-f8862da91018",
  "token": "12df687b3adda8cdcfd0b9b8a77d32b02b721be5",
  "isStaff": false
}
```

---


### 2.2) Rota de login

---

* POST /api/v1/login/

Rota serve para obter o token de um usuario cadastrado. Caso o `payload` seja valido será retornado o `token`. O código de sucesso é `200`

Corpo da requisição:

```json
{
  "username": "user1@user.com",
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
  "id": "24d3b887-f903-44ca-bfcf-f8862da91018",
  "token": "30af7c82372a8d4b3be470ea52967b0921f5ebff",
  "isStaff": false
}
```

---

### 2.3) Rota informações do usuario

---

* GET /api/v1/users/\<uuid:user_id>/

Rota para obter informação do usuario. É necessário passar o `token` de acesso no `Authorization` na forma `Bearer token` e `uuid` do usuário. O código de sucesso é `200`

Exemplo de `curl`:

```console
curl --request GET \
  --url http://localhost:8000/api/v1/users/24d3b887-f903-44ca-bfcf-f8862da91018/ \
  --header 'Authorization: Bearer 12df687b3adda8cdcfd0b9b8a77d32b02b721be5'
```

Corpo da resposta:

```json
{
  "name": "João Silva",
  "phone": "2222-2222",
  "role": "medico",
  "institution": "Ufrj",
  "email": "user1@user.com"
}
```

---

### 2.4) Rota para listar todas as cotas para aquele usuario

---

* GET /api/v1/users/\<uuid:user_id>/order/

Rota para listar a orders do usuario. É necessário passar o `token` de acesso no `Authorization` na forma `Bearer token` e `uuid` do usuário. O código de sucesso é `200`

Exemplo de `curl`:

```console
curl --request GET \
  --url http://localhost:8000/api/v1/users/24d3b887-f903-44ca-bfcf-f8862da91018/orders/ \
  --header 'Authorization: Bearer 12df687b3adda8cdcfd0b9b8a77d32b02b721be5'
```

Corpo da resposta:

```json
{
	"orders": [
		{
			"id": "49c1d8e7-e44b-4680-8fe7-42432df8f1d1",
			"userId": "24d3b887-f903-44ca-bfcf-f8862da91018",
			"quantityOfAnalyzes": 15,
			"remainingOfAnalyzes": 15,
			"price": 30000.0,
			"serviceName": "Dosimetria Clinica",
			"statusPayment": "Confirmado",
			"permission": true,
			"createdAt": "2022-08-30"
		},
		{
			"id": "23923dc1-b5bd-4e88-98c7-50292d69672a",
			"userId": "24d3b887-f903-44ca-bfcf-f8862da91018",
			"quantityOfAnalyzes": 5,
			"remainingOfAnalyzes": 5,
			"price": 10000.0,
			"serviceName": "Dosimetria Clinica",
			"statusPayment": "Analise",
			"permission": false,
			"createdAt": "2022-08-30"
		}
	]
}
```

---

### 2.5) Rota para ler uma cota especifica daquele usuario

---

* GET /api/v1/users/\<uuid:user_id>/order/\<uuid:id_order>/

Rota para ler uma order específica do usuario. É necessário passar o `token` de acesso no `Authorization` na forma `Bearer token`, `uuid` do usuário e o `uuid` da cota. O código de sucesso é `200`

Exemplo de `curl`:

```console
curl --request GET \
  --url http://localhost:8000/api/v1/users/24d3b887-f903-44ca-bfcf-f8862da91018/orders/23923dc1-b5bd-4e88-98c7-50292d69672a/ \
  --header 'Authorization: Bearer 12df687b3adda8cdcfd0b9b8a77d32b02b721be5'
```

Corpo da resposta:

```json
{
	"id": "23923dc1-b5bd-4e88-98c7-50292d69672a",
	"userId": "24d3b887-f903-44ca-bfcf-f8862da91018",
	"quantityOfAnalyzes": 5,
	"remainingOfAnalyzes": 5,
	"price": 10000.0,
	"serviceName": "Dosimetria Clinica",
	"statusPayment": "Analise",
	"permission": false,
	"createdAt": "2022-08-30"
}
```

---

### 2.6) Rota para ler os isotopos cadastrados

---

* GET /api/v1/isotopes/

Rota para ler os isotopos. O código de sucesso é `200`

Exemplo de `curl`:

```console
curl --request GET --url http://localhost:8000/api/v1/isotopes/
```

Corpo da resposta:

```json
{
  "count": "6",
  "isotopes": [
    "Lu-177",
    "Cu-64",
    "Cu-67",
    "F-18",
    "G1-68",
    "Ho-166"
  ]
}
```

---

### 2.7) Rota para listar calibrações

---

* GET /api/v1/users/\<uuid:user_id>/calibration/

Rota para listar as calibrações do usuario. É necessário passar o `token` de acesso no `Authorization` na forma `Bearer token` e `uuid` do usuário. O código de sucesso é `201`

Exemplo de `curl`:

```console
curl --request GET \
  --url http://localhost:8000/api/v1/users/24d3b887-f903-44ca-bfcf-f8862da91018/calibrations/ \
  --header 'Authorization: Bearer 30af7c82372a8d4b3be470ea52967b0921f5ebff'
```

Corpo da resposta:

```json
{
  "count": 2,
  "row": [
    {
      "id": "b707c70e-518f-4d33-bcd5-9da9491bbab6",
      "userId": "24d3b887-f903-44ca-bfcf-f8862da91018",
      "isotope": "Cu-64",
      "calibrationName": "Calibração B",
      "syringeActivity": 10.0,
      "residualSyringeActivity": 5.0,
      "measurementDatetime": "01/04/2016 - 01:12:04",
      "phantomVolume": 2.0,
      "acquisitionTime": "11:12:02"
    },
    {
      "id": "1400b576-1221-4304-835c-30a0512307db",
      "userId": "24d3b887-f903-44ca-bfcf-f8862da91018",
      "isotope": "F-18",
      "calibrationName": "Calibração A",
      "syringeActivity": 12.0,
      "residualSyringeActivity": 5.0,
      "measurementDatetime": "01/04/2016 - 01:12:04",
      "phantomVolume": 2.0,
      "acquisitionTime": "11:12:02"
    }
  ]
}
```

---


### 2.8) Rota para cadastra calibrações

---

* POST /api/v1/users/\<uuid:user_id>/calibration/

Rota para cadastra as calibrações do usuario. É necessário passar o `token` de acesso no `Authorization` na forma `Bearer token` e `uuid` do usuário. No header `Content-Type` como `multipart/form-data`. O código de sucesso é `201`

Exemplo de `curl`:

```console
curl --request POST \
  --url http://localhost:8000/api/v1/users/24d3b887-f903-44ca-bfcf-f8862da91018/calibrations/ \
  --header 'Authorization: Bearer 30af7c82372a8d4b3be470ea52967b0921f5ebff' \
  --header 'Content-Type: multipart/form-data' \
  --form isotope=F-18 \
  --form 'calibrationName=Calibração A' \
  --form syringeActivity=12 \
  --form residualSyringeActivity=5 \
  --form 'measurementDatetime=2016-04-01 01:12:04' \
  --form phantomVolume=2 \
  --form acquisitionTime=11:12:02
```

Corpo da resposta:

```json
{
  "id": "1400b576-1221-4304-835c-30a0512307db",
  "userId": "24d3b887-f903-44ca-bfcf-f8862da91018",
  "isotope": "F-18",
  "calibrationName": "Calibração A",
  "syringeActivity": 12.0,
  "residualSyringeActivity": 5.0,
  "measurementDatetime": "01/04/2016 - 01:12:04",
  "phantomVolume": 2.0,
  "acquisitionTime": "11:12:02"
}
```

---

### 2.9) Rota para atualizar uma calibração

---

* PUT /api/v1/users/\<uuid:user_id>/calibration/\<uuid:cali_id>

Rota para atualizar as calibrações do usuario. É necessário passar o `token` de acesso no `Authorization` na forma `Bearer token`, `uuid` do usuário e o `uuid` da calibração. No header `Content-Type` como `multipart/form-data`. O código de sucesso é `204`

Exemplo de `curl`:

```console
curl --request PUT \
  --url http://localhost:8000/api/v1/users/24d3b887-f903-44ca-bfcf-f8862da91018/calibrations/b707c70e-518f-4d33-bcd5-9da9491bbab6 \
  --header 'Authorization: Bearer 30af7c82372a8d4b3be470ea52967b0921f5ebff' \
  --header 'Content-Type: multipart/form-data' \
  --form isotope=Cu-64 \
  --form 'calibrationName=Calibração C' \
  --form syringeActivity=10 \
  --form residualSyringeActivity=5 \
  --form 'measurementDatetime=2016-04-01 01:12:04' \
  --form phantomVolume=2 \
  --form acquisitionTime=11:12:02
```

---

### 2.10) Rota para deletar uma calibração

---

* DELETE /api/v1/users/\<uuid:user_id>/calibration/

Rota para deletar uma do usuario. É necessário passar o `token` de acesso no `Authorization` na forma `Bearer token`, `uuid` do usuário e o `uuid` da calibração. O código de sucesso é `204`

Exemplo de `curl`:

```console
curl --request DELETE \
  --url http://localhost:8000/api/v1/users/24d3b887-f903-44ca-bfcf-f8862da91018/calibrations/b1b159b5-d5e7-4959-9cbb-3426ba5447fd \
  --header 'Authorization: Bearer 30af7c82372a8d4b3be470ea52967b0921f5ebff'
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

Após fazer o camando `migrate` para popular o banco com alguns dados basta:

```console
python manage.py loaddata contrib/db_initial.json
```

Os usuarios criados serão:

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
