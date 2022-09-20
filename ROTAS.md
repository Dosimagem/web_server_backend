# Index

  - [1) Rotas de Usuários](#1-rotas-dos-usuários)
    - [1.1) Rota de cadastro](#11-rota-de-cadastro)
    - [1.2) Rota de login](#12-rota-de-login)
    - [1.3) Rota para obter informações do usuário](#13-rota-informações-do-usuario)
    - [1.4) Rota para atualizar informações do usuário](#14-rota-de-atualização-do-usuario)
  - [2) Rotas dos pedidos](#2-rotas-dos-pedidos)
    - [2.1) Rota para listar todas as cotas para aquele usuário](#21-rota-para-listar-todas-os-podidos-para-aquele-usuario)
    - [2.2) Rota para ler uma cota específica daquele usuário](#22-rota-para-ler-uma-cota-especifica-daquele-usuário)
  - [3) Isotopos](#3-isotopos)
    - [3.1) Rota para ler os isótopos cadastrados](#31-rota-para-ler-os-isotopos-cadastrados)
  - [4) Rota das calibrações](#4-rotas-das-calibrações)
    - [4.1) Rota para listar as calibrações](#41-rota-para-listar-calibrações)
    - [4.2) Rota para cadastrar uma calibração](#42-rota-para-cadastra-calibrações)
    - [4.3) Rota para atualizar uma calibração](#43-rota-para-atualizar-uma-calibração)
    - [4.4) Rota para deletar uma calibração](#44-rota-para-deletar-uma-calibração)
    - [4.5) Rota para ler uma calibração](#45-rota-para-ler-uma-calibração)
  - [5) Rota das analises](#5-rota-das-analises)
    - [5.1) Rota para listar as analises](#51-rota-para-listar-as-analises)
    - [5.2) Rota para criar as analises](#52-rota-para-cadastra-analises)


---

## 1) Rotas dos usuários

### 1.1) Rota de cadastro

---

* POST /api/v1/register/

 Rota para registrar um usuário via o método post. Caso o `payload` seja válido e o usuário não exista esta rota irá salvar usuário e gera o `token`. O `email` foi usado como `username`. O código de sucesso é `201`

Exemplo de `curl`:

```console
curl --location --request POST 'localhost:8000/api/v1/users/register/' \
--header 'Content-Type: application/json' \
--data-raw '{
  "email": "user1@email.com",
  "confirmedEmail": "user1@email.com",
  "password1": "123456!!",
  "password2": "123456!!",
  "name": "João Sliva",
  "phone": "11111111",
  "role": "médico",
  "clinic": "Clinica A",
  "email": "user1@email.com",
  "cpf": "93743851121",
  "cnpj": "42438610000111"
}'
'''

Corpo da reposta:

```json
{
  "id": "24d3b887-f903-44ca-bfcf-f8862da91018",
  "token": "12df687b3adda8cdcfd0b9b8a77d32b02b721be5",
  "isStaff": false
}
```

---


### 1.2) Rota de login

---

* POST /api/v1/login/

Rota serve para obter o token de um usuário cadastrado. Caso o `payload` seja válido será retornado o `token`. O código de sucesso é `200`

Exemplo de `curl`:

```console
curl --request POST \
  --url http://localhost:8000/api/v1/login/ \
  --header 'Content-Type: application/json' \
  --data '{
  "username": "user1@email.com",
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

### 1.3) Rota informações do usuário

---

* GET /api/v1/users/\<uuid:user_id>

Rota para obter informação do usuário. É necessário passar o `token` de acesso no `Authorization` na forma `Bearer token` e `uuid` do usuário. O código de sucesso é `200`

Exemplo de `curl`:

```console
curl --request GET \
  --url http://localhost:8000/api/v1/users/24d3b887-f903-44ca-bfcf-f8862da91018/ \
  --header 'Authorization: Bearer 12df687b3adda8cdcfd0b9b8a77d32b02b721be5'
```

Corpo da resposta:

```json
{
  "name": "João Sliva",
  "phone": "11111111",
  "role": "médico",
  "clinic": "Clinica A",
  "email": "user1@email.com",
  "cpf": "93743851121",
  "cnpj": "42438610000111"
}
```

---

### 1.4) Rota de atualização do usuário

---

* PATCH /api/v1/users/\<uuid:user_id>

Rota que atualiza algumas informações do usuário. É necessário passar o `token` de acesso no `Authorization` na forma `Bearer token` e `uuid` do usuário. O código de sucesso é `204`


Exemplo de `curl`:

```console
curl --request PATCH \
  --url http://localhost:8000/api/v1/users/0be5fbc0-079f-4006-8a15-0e0851bb1df4 \
  --header 'Authorization: Bearer a349a7d81c67d88ac60bd7d97cd09e85eb43f929' \
  --header 'Content-Type: application/json' \
  --data '{
  "name": "João Sliva1",
  "phone": "111111111",
  "role": "médico",
  "clinic": "Clinica BA",
  "cnpj": "42438610000111"
}'
```
---

## 2) Rotas dos pedidos

### 2.1) Rota para listar todas os podidos para aquele usuario

---

* GET /api/v1/users/\<uuid:user_id>/order/

Rota para listar a orders do usuário. É necessário passar o `token` de acesso no `Authorization` na forma `Bearer token` e `uuid` do usuário. O código de sucesso é `200`

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
			"statusPayment": "Aguardando pagamento",
			"permission": false,
			"createdAt": "2022-08-30"
		}
	]
}
```

---

### 2.2) Rota para ler uma cota especifica daquele usuário

---

* GET /api/v1/users/\<uuid:user_id>/order/\<uuid:id_order>/

Rota para ler uma order específica do usuário. É necessário passar o `token` de acesso no `Authorization` na forma `Bearer token`, `uuid` do usuário e o `uuid` da cota. O código de sucesso é `200`

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

## 3) Isotopos

---

### 3.1) Rota para ler os isotopos cadastrados

---

* GET /api/v1/isotopes/

Rota para ler os isótopos. O código de sucesso é `200`

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

## 4) Rotas das calibrações

### 4.1) Rota para listar calibrações

---

* GET /api/v1/users/\<uuid:user_id>/calibrations/

Rota para listar as calibrações do usuário. É necessário passar o `token` de acesso no `Authorization` na forma `Bearer token` e `uuid` do usuário. O código de sucesso é `200`

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


### 4.2) Rota para cadastra calibrações

---

* POST /api/v1/users/\<uuid:user_id>/calibrations/

Rota para cadastra as calibrações do usuario. É necessário passar o `token` de acesso no `Authorization` na forma `Bearer token` e `uuid` do usuário. No header `Content-Type` como `multipart/form-data`. O código de sucesso é `201`

Exemplo de `curl`:

```console
curl --location --request POST 'localhost:8000/api/v1/users/0be5fbc0-079f-4006-8a15-0e0851bb1df4/calibrations/' \
--header 'Authorization: Bearer a349a7d81c67d88ac60bd7d97cd09e85eb43f929' \
--form 'isotope="F-18"' \
--form 'calibrationName="Calibração A"' \
--form 'syringeActivity="12"' \
--form 'residualSyringeActivity="0"' \
--form 'measurementDatetime="2016-04-01 01:12:04"' \
--form 'phantomVolume="2"' \
--form 'acquisitionTime="1800"' \
--form 'images=@"/home/henrique/Documents/Dosimagem/cali_2.zip"'
```

Corpo da resposta:

```json
{
  "id": "be4cda38-60a6-42f6-a817-8726594e8580",
  "userId": "0be5fbc0-079f-4006-8a15-0e0851bb1df4",
  "isotope": "F-18",
  "calibrationName": "Calibração B",
  "syringeActivity": 12.0,
  "residualSyringeActivity": 0.0,
  "measurementDatetime": "2016-04-01 01:12:04",
  "phantomVolume": 2.0,
  "acquisitionTime": 1800.0,
  "imagesUrl": "http://localhost:8000/media/1/calibration_1663616709809433.zip"
}
```

---

### 4.3) Rota para atualizar uma calibração

---

* PUT /api/v1/users/\<uuid:user_id>/calibrations/\<uuid:cali_id>

Rota para atualizar uma calibração especifica de um usuário. É necessário passar o `token` de acesso no `Authorization` na forma `Bearer token`, `uuid` do usuário e o `uuid` da calibração. No header `Content-Type` como `multipart/form-data`. O código de sucesso é `204`

Exemplo de `curl`:

```console
curl --location --request PUT 'localhost:8000/api/v1/users/0be5fbc0-079f-4006-8a15-0e0851bb1df4/calibrations/ab1fec6c-633d-4598-be23-a3a374656209' \
--header 'Authorization: Bearer a349a7d81c67d88ac60bd7d97cd09e85eb43f929' \
--form 'isotope="F-18"' \
--form 'calibrationName="Calibração D"' \
--form 'syringeActivity="12"' \
--form 'residualSyringeActivity="0"' \
--form 'measurementDatetime="2016-04-01 01:12:04"' \
--form 'phantomVolume="2"' \
--form 'acquisitionTime="1800"'
```

---

### 4.4) Rota para deletar uma calibração

---

* DELETE /api/v1/users/\<uuid:user_id>/calibrations/\<uuid:cali_id>

Rota para deletar uma calibração especifica de um usuário. É necessário passar o `token` de acesso no `Authorization` na forma `Bearer token`, `uuid` do usuário e o `uuid` da calibração. O código de sucesso é `200`

Exemplo de `curl`:

```console
curl --request DELETE \
  --url http://localhost:8000/api/v1/users/24d3b887-f903-44ca-bfcf-f8862da91018/calibrations/b1b159b5-d5e7-4959-9cbb-3426ba5447fd \
  --header 'Authorization: Bearer 30af7c82372a8d4b3be470ea52967b0921f5ebff'
```

Corpo da resposta:

```json
{
    "id": "98b165ba-8744-48d4-bcde-a8fcfe15d3f1",
    "message": "Calibração deletada com sucesso!"
}
```

---

### 4.5) Rota para ler uma calibração

---

* GET /api/v1/users/\<uuid:user_id>/calibrations/\<uuid:cali_id>

Rota para ler uma calibração especifica de um usuário. É necessário passar o `token` de acesso no `Authorization` na forma `Bearer token`, `uuid` do usuário e o `uuid` da calibração. O código de sucesso é `200`

Exemplo de `curl`:

```console
curl --request GET \
  --url http://localhost:8000/api/v1/users/0be5fbc0-079f-4006-8a15-0e0851bb1df4/calibrations/0f7cabd2-97fc-4115-85e4-0cb05174ce2b \
  --header 'Authorization: Bearer a349a7d81c67d88ac60bd7d97cd09e85eb43f929'
```

Corpo da resposta:

```json
{
    "id": "98b165ba-8744-48d4-bcde-a8fcfe15d3f1",
    "userId": "0be5fbc0-079f-4006-8a15-0e0851bb1df4",
    "isotope": "Lu-177",
    "calibrationName": "Clinica A",
    "syringeActivity": 10.0,
    "residualSyringeActivity": 20.0,
    "measurementDatetime": "2022-09-03 05:45:10",
    "phantomVolume": 16.0,
    "acquisitionTime": 28.0,
    "imagesUrl": "http://localhost:8000/media/1/calibration_1663616284855262.zip"
}
```

---

## 5) Rota das analises

### 5.1) Rota para listar as analises

---

* GET api/v1/users/\<uuid:user_id>/orders/\<uuid:order_id>/analysis/

Rota para listar as analises de um pedido. É necessário passar o `token` de acesso no `Authorization` na forma `Bearer token`, `uuid` do usuário e `uuid` do pedido. O código de sucesso é `200`

Exemplo de `curl`:

```console
curl --location --request GET 'localhost:8000/api/v1/users/0be5fbc0-079f-4006-8a15-0e0851bb1df4/orders/e003ce6f-b8ee-4cb6-b210-e30cd07c06de/analysis/' \
--header 'Authorization: Bearer a349a7d81c67d88ac60bd7d97cd09e85eb43f929'
```

Corpo da resposta:

```json
{
    "count": 2,
    "row": [
        {
            "id": "4ce2af32-090b-4c9f-acc4-08b74365b8d0",
            "userId": "0be5fbc0-079f-4006-8a15-0e0851bb1df4",
            "orderId": "e003ce6f-b8ee-4cb6-b210-e30cd07c06de",
            "calibrationId": "ab1fec6c-633d-4598-be23-a3a374656209",
            "status": "Analisando informações",
            "images": "/media/ct_spec_2.zip",
            "active": true,
            "serviceName": "Dosimetria Preclinica",
            "createdAt": "2022-09-19 20:16:39",
            "modifiedAt": "2022-09-19 20:16:39"
        },
        {
            "id": "6336bb0f-55cd-4143-9082-fabadf0d5f18",
            "userId": "0be5fbc0-079f-4006-8a15-0e0851bb1df4",
            "orderId": "e003ce6f-b8ee-4cb6-b210-e30cd07c06de",
            "calibrationId": "ab1fec6c-633d-4598-be23-a3a374656209",
            "status": "Analisando informações",
            "images": "/media/ct_spec_2_zuenpVE.zip",
            "active": true,
            "serviceName": "Dosimetria Preclinica",
            "createdAt": "2022-09-19 20:25:06",
            "modifiedAt": "2022-09-19 20:25:06"
        }
    ]
}
```

---


### 5.2) Rota para cadastra analises

---

* POST /api/v1/users/\<uuid:user_id>/calibrations/

Rota para cadastra uma analises em  uma pedido. É necessário passar o `token` de acesso no `Authorization` na forma `Bearer token` , `uuid` do usuário e `uuid` do pedido. No header `Content-Type` como `multipart/form-data`. O código de sucesso é `201`

Exemplo de `curl`:

```console
curl --location --request POST 'localhost:8000/api/v1/users/0be5fbc0-079f-4006-8a15-0e0851bb1df4/orders/e003ce6f-b8ee-4cb6-b210-e30cd07c06de/analysis/' \
--header 'Authorization: Bearer a349a7d81c67d88ac60bd7d97cd09e85eb43f929' \
--form 'calibrationId="ab1fec6c-633d-4598-be23-a3a374656209"' \
--form 'images=@"/home/henrique/Documents/Dosimagem/ct_spec_2.zip"'
```

Corpo da resposta:

```json
{
  "id": "8c275854-102b-4853-8daf-df048eb90296",
  "userId": "0be5fbc0-079f-4006-8a15-0e0851bb1df4",
  "orderId": "3898a7e6-34ed-4788-ad25-afae38c19f7d",
  "calibrationId": "ab1fec6c-633d-4598-be23-a3a374656209",
  "status": "Analisando informações",
  "images": "/media/ct_spec_2_oMzqgwC.zip",
  "active": true,
  "serviceName": "Dosimetria Clinica",
  "createdAt": "2022-09-19 20:48:26",
  "modifiedAt": "2022-09-19 20:48:26"
}
```

---