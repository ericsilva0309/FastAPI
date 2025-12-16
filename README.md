# Fast Zero — Documentação Técnica

> **Resumo:** Fast Zero é uma API REST construída com **FastAPI**, **SQLAlchemy (async)** e **PostgreSQL**, orquestrada com **Docker** e gerida com **Poetry**. Esta documentação é voltada para desenvolvedores e engenheiros responsáveis por manutenção, deploy e evolução do projeto.

---

## Índice

- [Fast Zero — Documentação Técnica](#fast-zero--documentação-técnica)
  - [Índice](#índice)
  - [Visão geral](#visão-geral)
  - [Pré-requisitos](#pré-requisitos)
  - [Quickstart — executar localmente](#quickstart--executar-localmente)
    - [Com Docker (recomendado)](#com-docker-recomendado)
    - [Sem Docker (dev)](#sem-docker-dev)
  - [Gerenciamento de dependências (Poetry)](#gerenciamento-de-dependências-poetry)
  - [Configuração do VS Code (Pylance)](#configuração-do-vs-code-pylance)
  - [Variáveis de ambiente](#variáveis-de-ambiente)
  - [Docker \& Docker Compose](#docker--docker-compose)
  - [Migrações de banco (Alembic) — async app / sync migrations](#migrações-de-banco-alembic--async-app--sync-migrations)
    - [Contexto](#contexto)
    - [Implementação (migrations/env.py)](#implementação-migrationsenvpy)
  - [Testes e `task` (Taskfile)](#testes-e-task-taskfile)
    - [Estratégia de testes](#estratégia-de-testes)
  - [CI: GitHub Actions](#ci-github-actions)
  - [Arquitetura do código — responsabilidades](#arquitetura-do-código--responsabilidades)
  - [Fluxo de execução (Request Lifecycle)](#fluxo-de-execução-request-lifecycle)
    - [Diagrama (Mermaid) — fluxo de requisição](#diagrama-mermaid--fluxo-de-requisição)
  - [Como adicionar uma nova feature (passo a passo)](#como-adicionar-uma-nova-feature-passo-a-passo)
  - [Comandos úteis / FAQ / Troubleshooting](#comandos-úteis--faq--troubleshooting)
  - [Contribuição e boas práticas](#contribuição-e-boas-práticas)
  - [Apêndice — comandos rápidos](#apêndice--comandos-rápidos)
  - [Diagramas adicionais (opcionais)](#diagramas-adicionais-opcionais)
    - [Arquitetura em camadas](#arquitetura-em-camadas)
    - [Sequência (async runtime vs migrations)](#sequência-async-runtime-vs-migrations)

---

## Visão geral

Fast Zero é uma API concebida com as seguintes premissas:

- arquitetura modular e testável;  
- separação clara entre lógica de negócio, persistência e rotas;  
- uso de SQLAlchemy em modo assíncrono para alta concorrência;  
- Alembic para versionamento de schema, rodando em modo síncrono (por compatibilidade);  
- infraestrutura conteinerizada para facilitar deploy e replicação do ambiente.

---

## Pré-requisitos

- Git  
- Docker e Docker Compose  
- Python (recomendado 3.11)  
- Poetry (ou `pipx` para instalar Poetry)  
- gh (opcional — GitHub CLI)  
- Editor recomendado: VS Code com extensão Python + Pylance

---

## Quickstart — executar localmente

### Com Docker (recomendado)
1. Copie `.env.example` → `.env` e ajuste valores.  
2. Build & up:
```bash
docker compose up --build
````

O `entrypoint.sh` do container irá:

* aguardar o Postgres (healthcheck/retry)
* rodar `alembic upgrade head`
* iniciar `uvicorn`

### Sem Docker (dev)

```bash
poetry install
poetry run alembic upgrade head
poetry run uvicorn fast_zero.app:app --reload --host 0.0.0.0 --port 8000
```

---

## Gerenciamento de dependências (Poetry)

* Instalar dependências:

```bash
poetry install
```

* Adicionar dependência de runtime:

```bash
poetry add <package>
```

* Adicionar dependência de desenvolvimento:

```bash
poetry add --dev <package>
```

**Nota:** o projeto usa `asyncpg` para runtime (driver assíncrono) e `psycopg`/`psycopg2-binary` para migrações (Alembic). Garanta ambos listados no `pyproject.toml`.

---

## Configuração do VS Code (Pylance)

Problema comum: `Import "fastapi" could not be resolved`.

**Solução:**

1. Descubra o ambiente do Poetry:

```bash
poetry env info --path
```

2. No VS Code: `Ctrl+Shift+P` → `Python: Select Interpreter` → selecione o caminho retornado.
3. (Opcional) criar env in-project:

```bash
poetry config virtualenvs.in-project true
poetry install
```

4. Reinicie o VS Code.

---

## Variáveis de ambiente

Principais variáveis (não versionar):

* `DATABASE_URL` — ex.: `postgresql+asyncpg://user:pass@host:5432/db`
* `SECRET_KEY`
* `ALGORITHM`
* `ACCESS_TOKEN_EXPIRE_MINUTES`

Exemplo `.env`:

```env
DATABASE_URL=postgresql+asyncpg://app_user:app_password@localhost:5432/app_db
SECRET_KEY=troque_por_uma_chave_secreta
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

GitHub Actions — configurar secrets: `Settings → Secrets and variables → Actions` ou `gh secret set -f .env`.

---

## Docker & Docker Compose

Use a composição fornecida. Rebuild após alterações em dependências:

```bash
docker compose build --no-cache
```

Recomenda-se usar `python:3.11-slim` na imagem base para estabilidade no ecossistema async/psycopg/uvloop.

---

## Migrações de banco (Alembic) — async app / sync migrations

### Contexto

* App usa `postgresql+asyncpg` (asyncpg)
* Migrações com Alembic devem usar driver síncrono (`psycopg`) para evitar `MissingGreenlet`

### Implementação (migrations/env.py)

Converta URL async → sync antes de criar engine:

```python
database_url = Settings().DATABASE_URL.replace(
    "postgresql+asyncpg", "postgresql+psycopg"
)
config.set_main_option("sqlalchemy.url", database_url)
```

Instale driver síncrono:

```bash
poetry add psycopg
# ou
poetry add psycopg2-binary
```

---

## Testes e `task` (Taskfile)

Comandos:

* `task test`  (recomendado)
* `poetry run task test`
* `poetry run pytest`

Execução interativa:

```bash
python -i tests/conftest.py
# no REPL:
UserFactory()
```

### Estratégia de testes

* **Unitários (`tests/unit/`)**: isolam regras de negócio, sem banco real (usar mocks).
* **Integração (`tests/integration/`)**: endpoints + banco real (via docker-compose ou service no CI).
* Fixtures e factories ficam em `tests/conftest.py`.

---

## CI: GitHub Actions

Pipeline padrão:

* checkout
* setup python (3.11 recomendado)
* instalar poetry
* poetry install
* executar migrations
* rodar testes

Melhorias: cache de dependências, separar lint/unit/integration, usar service postgres com healthcheck.

---

## Arquitetura do código — responsabilidades

* `fast_zero/app.py` — cria app, registra routers, middlewares, eventos.
* `fast_zero/settings.py` — `pydantic.BaseSettings`, leitura de `.env`.
* `fast_zero/database.py` — `create_async_engine`, `AsyncSession`, `get_session`.
* `fast_zero/models.py` — modelos e `table_registry.metadata` (usado pelo Alembic).
* `fast_zero/routers/*` — organização por domínio (auth, users, todos).
* `tests/` — `unit/` e `integration/`.

---

## Fluxo de execução (Request Lifecycle)

1. **Recepção** — Uvicorn recebe a requisição HTTP e repassa ao FastAPI (instância em `app.py`).
2. **Roteamento** — FastAPI seleciona o router correto em `fast_zero/routers/*`.
3. **Dependências** — Dependências como `get_session()` (AsyncSession) são injetadas via `Depends`.
4. **Processamento** — A lógica de aplicação (services, validações) processa a requisição.
5. **Persistência** — Operações de banco são realizadas com `await` usando SQLAlchemy Async (`asyncpg`).
6. **Resposta** — Resultado é serializado em JSON e retornado ao cliente.

### Diagrama (Mermaid) — fluxo de requisição

```mermaid
flowchart LR
  Client["Client (browser / client)"] -->|HTTP Request| Uvicorn["Uvicorn"]
  Uvicorn --> FastAPI["FastAPI (app)"]
  FastAPI --> Router["Router (fast_zero/routers/*)"]
  Router --> Handler["Handler / Controller"]
  Handler -->|Depends|get_session["get_session() (AsyncSession)"]
  Handler --> Service["Service / Business Logic"]
  Service --> Repo["Repository / ORM (SQLAlchemy Async)"]
  Repo -->|asyncpg| Postgres["PostgreSQL"]
  Postgres --> Repo
  Repo --> Service
  Service --> Handler
  Handler --> Router
  Router --> FastAPI
  FastAPI -->|HTTP Response| Client
```

---

## Como adicionar uma nova feature (passo a passo)

1. **Defina o modelo** em `fast_zero/models.py`.
2. **Crie/atualize schemas** (Pydantic) em `fast_zero/schemas.py` ou similar.
3. **Crie um router** em `fast_zero/routers/novo_recurso.py`.
4. **Registre o router** em `fast_zero/app.py`.
5. **Gere a migração**:

```bash
poetry run alembic revision --autogenerate -m "add novo_recurso"
```

6. **Aplique a migração**:

```bash
poetry run alembic upgrade head
```

7. **Implemente testes** em `tests/unit/` e (se necessário) `tests/integration/`.
8. **Rode a suíte de testes** e verifique lint/format:

```bash
task test
poetry run ruff check .
poetry run black --check .
```

9. **Abra PR** com descrição do que mudou e testes adicionados.

---

## Comandos úteis / FAQ / Troubleshooting

* `No module named 'asyncpg'` → `poetry add asyncpg` + rebuild Docker.
* `MissingGreenlet` → Alembic usando URL async; converta no `env.py`.
* Container sobe mas Alembic falha → use `set -e` no `entrypoint.sh` e healthchecks no DB.
* VS Code não reconhece imports → selecione interpreter do Poetry (ver seção VS Code).
* Erro de permissão no `entrypoint.sh` → `chmod +x entrypoint.sh`.

---

## Contribuição e boas práticas

* Faça PRs pequenas e relacionadas a uma única responsabilidade.
* Configure `pre-commit` (black, ruff, isort).
* Sempre atualize e commite `poetry.lock` ao mudar dependências.
* Não comite `.env` com segredos — use `Secrets` no GitHub.

---

## Apêndice — comandos rápidos

```bash
poetry install
poetry add asyncpg
poetry add psycopg
poetry run alembic upgrade head
poetry run pytest
poetry run uvicorn fast_zero.app:app --reload
docker compose up --build
```

---

## Diagramas adicionais (opcionais)

### Arquitetura em camadas

```mermaid
graph LR
  Client --> API["FastAPI (routers)"]
  API --> Service["Services (business)"]
  Service --> Repo["Repository (ORM)"]
  Repo --> DB["PostgreSQL (asyncpg)"]
  CI["GitHub Actions"] -->|runs| Tests["Tests"]
  CI -->|builds| DockerImage["Docker Image"]
```

### Sequência (async runtime vs migrations)

```mermaid
sequenceDiagram
  participant API as FastAPI (async)
  participant DB as PostgreSQL (asyncpg)
  participant Alembic as Alembic (sync)

  API->>DB: query (await, asyncpg)
  DB-->>API: result
  Alembic->>DB: migration (psycopg, sync)
  DB-->>Alembic: ack
```

---