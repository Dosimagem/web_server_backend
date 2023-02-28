# Index

- [Index](#index)
- [1) Rotas](#1-rotas)
- [2) Desenvolvimento](#2-desenvolvimento)
  - [2.1) Setup inicial](#21-setup-inicial)
  - [2.2) Rodando o servidor de desenvolvimento](#22-rodando-o-servidor-de-desenvolvimento)
  - [2.3) Rodando os teste](#23-rodando-os-teste)
  - [2.4) Área adminstrativa](#24-área-adminstrativa)
- [3) Banco de dados](#3-banco-de-dados)
  - [3.1) Usando o postgres via docker](#31-usando-o-postgres-via-docker)
  - [3.2) Backup do banco:](#32-backup-do-banco)
- [4) Python decouple](#4-python-decouple)
- [5) Docker](#5-docker)
  - [5.1) Simulando um ambiente de produção](#51-simulando-um-ambiente-de-produção)
  - [5.2) Docker em desenvolvimento](#52-docker-em-desenvolvimento)
- [6) Verificação de email](#6-verificação-de-email)


# 1) Rotas

[Documentação da API](https://documenter.getpostman.com/view/18852890/2s83Kad2KE)


# 2) Desenvolvimento


## 2.1) Setup inicial
---

O setup incicial necessário fazer apenas `uma vez`.

```console
make init
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

Após fazer o camando `migrate` para popular o banco os isotopos e benefícios basta fazer:

```console
python manage.py loaddata benefits
python manage.py loaddata isotopes
```

ou

```console
make docker_loaddata
```

---

## 2.2) Rodando o servidor de desenvolvimento

---

```console
python manage.py runserver
```

É bom utilizar `DEBUG=True` para que o `django` sirva os arquivos estáticos.

---

## 2.3) Rodando os teste
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

## 2.4) Área adminstrativa

Para acessar usar o `admin` é preciso criar um super usuário, para tal basta usar o comando:

```console
make create_admin
```

A rota para acessar é `/dosimagem/admin/`

---

# 3) Banco de dados

---

## 3.1) Usando o postgres via docker

---

Subir o container

```console
make db_up
```

Configurar `DATABASE_URL` no arquivo `.env` para

```
postgres://dosimagem:dosimagem@localhost:5434/dosimagem_db
```

---

## 3.2) Backup do banco:


Todo o banco

```console
./manage.py dumpdata --exclude auth.permission --exclude contenttypes --indent 2 > db_initial.json
```

Apenas dos `Isotopos` cadastrados.

```console
./manage.py ./manage.py dumpdata isotopo.Isotope --indent 2 > isotope.json
```


# 4) Python decouple

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

# 5) Docker

---

## 5.1) Simulando um ambiente de produção


Para subir a `api` completa simulando o ambiente de produção com `nginx`, `gunicorn` e `postgres` basta fazer.


```console
make docker_build_and_up_prod
```

A `api` estará dispnivel em `localhost:80`.

Para criar apenas uma nova `dosimagem_api` atualizada.

```console
make docker_build_prod
```

Caso haja certaza que aa imagem está atualizada base o comando:

```console
make docker_up_prod
```

O conteiner `django` para `prod` tem apenas as depencias de desenvolvimento.

Para fazer as migrações:

```console
make docker_migrate
```

Para criar o usuário root bastas fazer:

```console
make docker_create_admin
```

## 5.2) Docker em desenvolvimento

Pode-se também executar a versão de desenvolvimento para tal basta:

```console
make docker_build_prod
```

Com este comando você irá subir dois os conteiners, o `django` e o `postgres`. O conteiner `django` para `dev` usa o servidor de desenvolvimente e não o `gunicorn` e também possiu as dependencias de desenvolvimento.

Para rodar o teste

```console
make docker_pytest
```

---

### 6) Verificação de email

Quando um usuario é cadastrado um `email` será enviado para o novo usuário. Neste email teremos um link para o `front-end` na forma:

> http://front_end_dominio/users/<uuid_user>/email-confirm/?token=<token_jwt>

Para validar o `email` o frontend precisa mandar uma solicitaão para a rota do `backend`:

> localhost:8000/api/v1/users/9591876e-bf1e-4802-a57d-fe80edb0c864/email/verify/

Com o payload:

```json
{
  "token": "token_jwt"
}
```

Se tudo ocorrer como esperado o email será verificado. O `Token JWT` tem uma validade de `24 horas` e só pode ser usado uma `unica vez`.
