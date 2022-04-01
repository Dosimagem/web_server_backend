# web_server


## Preparando o Ambiente de desenvolvimento
---

Criando o ambiente virtual e instalando as dependências

```console
python -m venv .venv --upgrade-deps
source .venv/bin/activate
pip install -r requirements.txt
```

## Variaveis de ambiente com o **python-decouple**
---

As variáveis de ambiente tem que ser definidas no arquivo **.env**. Este arquivo não pode ser versionado pois ele armazenará informações sensiveis. Um exemplo de arquivo .env pode ser encontrado na pasta **contrib/env-sample**.

```console
cp contrib/env_sample .env
```
