Fast API com Dunossauro

---

# Problema comum: VS Code não reconhece imports (ex: *Import "fastapi" could not be resolved*)

Ao clonar o projeto, alguns usuários podem ver erros como:

```
Import "fastapi" could not be resolved
Pylance: reportMissingImports
```

Mesmo após rodar:

```
poetry install
```

Isso acontece porque o **VS Code não está usando o ambiente virtual criado pelo Poetry**.

## Como resolver

1. **Instale as dependências normalmente**:

   ```sh
   poetry install
   ```

2. **Descubra onde está o ambiente virtual** criado pelo Poetry:

   ```sh
   poetry env info --path
   ```

3. No VS Code, abra o comando:

   ```
   Ctrl + Shift + P → Python: Select Interpreter
   ```

   E selecione o caminho retornado no passo 2.

4. **Reinicie o VS Code** e os erros de import devem desaparecer.

---

## Dica opcional (recomendada)

Para facilitar, você pode configurar o Poetry para criar o ambiente virtual **dentro do projeto**.

Execute apenas uma vez:

```sh
poetry config virtualenvs.in-project true
```

Depois reinstale:

```sh
poetry install
```

Isso criará uma pasta `.venv/` dentro do projeto, que o VS Code detecta automaticamente.

---

## Por que isso acontece?

O Pylance (extensão do VS Code) nem sempre sabe qual Python deve usar.
Quando ele usa o Python global (fora do Poetry), os imports parecem “desaparecer”.

Selecionar o interpretador correto resolve 100% dos casos.

---

se eu quiser testar um test em especifico, eu entro na pasta utilizando o comando de interatividade do python 'python -i tests/conftest.py', dentro dele eu chamo a função 'UserFactory()'




docker run -e POSTGRES_USER=app_user -e POSTGRES_DB=app_db -e POSTGRES_PASSWORD=app_password --name app_database -p 5432:5432 postgres

docker build -t "fast_zero" .


eu adicionei as variasveis de ambiente no proprio github manualmente, daria pra fazer com gh: gh secret set -f .env
voce vai no repositório e lica em settings depois em secrets and variables, actions e new repository secret
