## Instruções rápidas para agentes de IA — ConsultaLab

Objetivo: permitir que um agente de codificação seja imediatamente produtivo neste repositório Django baseado em Cookiecutter.

- Projeto: Cookiecutter Django (app monolítica com vários "apps" dentro de `consultalab/`).
- Entrypoint: `manage.py` (define `DJANGO_SETTINGS_MODULE=config.settings.local`).
- Settings por ambiente: `config/settings/{base.py,local.py,production.py,test.py}` — testes usam `config.settings.test`.

O que ler primeiro
- `config/` — settings, `asgi.py`, `wsgi.py`, `celery_app.py` (ponto central para Celery).
- `manage.py` — contém um `sys.path.append(str(current_path / "consultalab"))` importante para resoluções de import.
- `consultalab/` — contém os apps reais: `users/`, `core/`, `bacen/`, `audit/` etc. (lógica de negócio aqui).
- `pyproject.toml` — configuração de testes, mypy, ruff/djlint; importante para reproduzir fluxo de CI localmente.

Fluxos e comandos práticos (exemplos extraídos do README)
- Rodar servidor local: `python manage.py runserver` (`manage.py` já aponta para `config.settings.local`).
- Criar superuser: `python manage.py createsuperuser`.
- Testes (pytest configurado via `pyproject.toml`):
  - `pytest`  (opções padrão: `--ds=config.settings.test --reuse-db --import-mode=importlib`).
  - Cobertura: `coverage run -m pytest && coverage html`.
- Type checking: `mypy consultalab` (configurado no `pyproject.toml`).
- Celery:
  - Worker: `cd consultalab` then `celery -A config.celery_app worker -l info` (ou execute do root mantendo o mesmo PYTHONPATH).
  - Beat: `celery -A config.celery_app beat`.
- Traduções: `docker compose -f docker-compose.local.yml run --rm django python manage.py makemessages --all --no-location` e `compilemessages` conforme `locale/` README.

Padrões e convenções específicas deste repositório
- Estrutura apps-interna: apps estão dentro de `consultalab/` (não no topo do PYTHONPATH). `manage.py` adiciona essa pasta ao `sys.path` — manter esse comportamento para testes/CLI.
- Settings dependem do módulo `config.settings.*`. Ao inspecionar código, altere/execute sempre com o `DJANGO_SETTINGS_MODULE` adequado (tests -> `config.settings.test`).
- Pytest: `--reuse-db` é esperado (tests são escritos para reusar DB entre runs). Há um marcador `integrations_test` em `pyproject.toml`.
- Lint/format: ruff + djlint configurados em `pyproject.toml` — siga as regras lá (ex.: max_line_length 119, perfil django).
- Internacionalização: traduções vivem em `locale/*`; o container `mailpit` é usado no ambiente Docker para visualizar e-mails.

Pontos de integração a observar (onde mudanças têm impacto cruzado)
- `config/celery_app.py` + `consultalab/*/tasks.py` — alterações em tasks afetam workers/beat e deploys.
- `users/adapters.py` — customizações de autenticação/fluxo (útil para 2FA/allauth work).
- `consultalab/bacen/api.py` e `consultalab/bacen/tasks.py` — integrações externas (serviços/bacen) e pontos para mocks em testes.
- `compose/` e `docker-compose.*.yml` — orquestração local/prod; usar estes arquivos para replicar serviços (DB, Redis, Mailpit, etc.).

Busca orientada (onde procurar mudanças relacionadas)
- Mudanças de settings: `config/settings/*` (+ `manage.py` para efeitos no PYTHONPATH).
- Endpoints / views: `consultalab/*/views.py` e `consultalab/*/urls.py`.
- Modelos e migrações: `consultalab/*/models.py` e `migrations/` dentro dos apps.
- Tarefas assíncronas: procurar `@shared_task`/`@app.task` em `consultalab/*/tasks.py`.

Exemplos rápidos a citar em PRs/commits
- "Testes: execute `pytest -k name`; para rodar localmente use `--ds=config.settings.test` (já presente em pyproject)."
- "Ao adicionar tasks Celery, atualize `config/celery_app.py` se necessário e verifique `compose/*` para broker/worker config."

Notas finais
- Evite supor mudanças no layout do PYTHONPATH: verifique `manage.py` e `pyproject.toml` antes de executar scripts ou importar módulos.
- Documente alterações de infra (compose/docker) sempre que tocar em `compose/` ou `docker-compose.*.yml`.
- Mantenha a consistência com as configurações existentes em `pyproject.toml` para linting, type checking e testes.
