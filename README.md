# web_server

Aplicação responsável por receber as requisições dos usuários.

Especificação: [link](https://github.com/Dosimagem/web_server/tree/main/spec)

### 1) Status

Desenvolvimento das funcionalidades

- Usuários [ OK ]
- Serviços [ nOK ]


### 2) Informações técnicas

#### 2.1) Rotas

- <domain>/
- <domain>/accounts/signup/
- <domain>/accounts/login/
- <domain>/accounts/logout/
- <domain>/auth-example/

### 2.2) Docker

```console
docker build --tag django_server:dosimagem .
docker run --name django_server -d -p 8000:8000 django_server:dosimagem
docker start django_server
```

## 3) Desenvolvimento

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
```

Intalando as dependências de desenvolvimento:

```console
pip install -r requeriments-dev.txt
```

Atualizando a lista de dependências com o **pip-tools**:

```console
pip-compile --generate-hashes requirements.in
pip-compile --generate-hashes requirements-dev.in
```
