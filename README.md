# web_server

Aplicação responsável por receber as requisições dos usuários.

Especificação: [link](https://github.com/Dosimagem/web_server/tree/main/spec)

### Status

Desenvolvimento das funcionalidades

- Usuários [ nOK ]
- Serviços [ nOK ]


### Informações técnicas

#### Rotas

- <domain>/
- <domain>/accounts/signup/
- <domain>/accounts/login/
- <domain>/accounts/logout/
- <domain>/auth-example/

### Docker

```
docker build --tag django_server:dosimagem .
docker run --name django_server -d -p 8000:8000 django_server:dosimagem 
docker start django_server
```