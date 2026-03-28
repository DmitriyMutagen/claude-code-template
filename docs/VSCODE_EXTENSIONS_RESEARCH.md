Братан, вот полный разбор. Исследовал все категории, отсеял шлак, оставил только то, что реально работает с твоим стеком.

---

# VS Code Extensions -- Ultimate Stack для Claude Code + Python/TS разработчика

## Краткий вывод

Тебе нужно **20 расширений**, не больше. Половину ты уже мог установить. Ключевое: Claude Code уже встроен в VS Code через официальное расширение Anthropic, GitHub Copilot с ним НЕ конфликтует (они работают в разных слоях). Ruff заменяет Black + isort + Flake8 + pyupgrade, так что Python-стек упрощается до 1 расширения.

---

## TOP-20 Ranked List

### Tier 1: MUST HAVE (ставить немедленно)

| # | Extension | Что делает | Почему для нас | Downloads |
|---|-----------|------------|----------------|-----------|
| **1** | **Claude Code** (anthropic.claude-code) | Нативная интеграция Claude Code CLI в VS Code | Твой основной AI-инструмент, MCP поддержка, checkpoints, diff viewing | 2M+ |
| **2** | **Python** (ms-python.python) | IntelliSense, debugging, venvs, Jupyter | База для всего Python-стека | 120M+ |
| **3** | **Pylance** (ms-python.vscode-pylance) | Быстрый language server (Pyright) | Типизация Pydantic/FastAPI, автокомплит SQLAlchemy | 90M+ |
| **4** | **Ruff** (charliermarsh.ruff) | Linter + formatter (заменяет Black, isort, Flake8) | В 100x быстрее аналогов, уже в pre-commit | 15M+ |
| **5** | **Error Lens** (usernamehw.errorlens) | Показывает ошибки inline прямо в строке кода | Мгновенный фидбек без hover, критично для FastAPI/TS | 10M+ |
| **6** | **GitLens** (eamodio.gitlens) | Git blame inline, commit graph, branch management | 80% ускорение Git-workflow, AI commit messages | 40M+ |
| **7** | **ESLint** (dbaeumer.vscode-eslint) | Linting для JS/TS | Обязателен для Next.js/React | 35M+ |
| **8** | **Prettier** (esbenp.prettier-vscode) | Автоформатирование JS/TS/CSS/JSON | Format-on-save для фронтенд-стека | 45M+ |
| **9** | **Docker** (ms-azuretools.vscode-docker) | Dockerfile/Compose syntax, container management | Docker Compose управление прямо из VS Code | 25M+ |
| **10** | **Playwright Test** (ms-playwright.playwright) | Run/debug E2E тестов, trace viewer, codegen | Твой основной E2E инструмент, нативная интеграция | 3M+ |

### Tier 2: NICE TO HAVE (ставить при первой необходимости)

| # | Extension | Что делает | Почему для нас | Downloads |
|---|-----------|------------|----------------|-----------|
| **11** | **PostgreSQL** (ms-ossdata.vscode-postgresql) | IntelliSense для SQL, schema visualization, Docker PG | Запросы к b2b_intelligence прямо из VS Code | 2M+ |
| **12** | **Tailwind CSS IntelliSense** (bradlc.vscode-tailwindcss) | Автокомплит Tailwind классов | Если используешь Tailwind в Next.js | 12M+ |
| **13** | **Pretty TypeScript Errors** (yoavbls.pretty-ts-errors) | Читаемые TS ошибки вместо криптографии | TypeScript ошибки станут понятными | 4M+ |
| **14** | **Todo Tree** (Gruntfuggly.todo-tree) | Дерево всех TODO/FIXME/HACK в проекте | Видеть весь техдолг на одном экране | 7M+ |
| **15** | **GitHub Pull Requests** (GitHub.vscode-pull-request-github) | PR review прямо в VS Code | Создание/ревью PR без браузера | 15M+ |
| **16** | **Markdown Preview Mermaid** (bierner.markdown-mermaid) | Рендер Mermaid диаграмм в Markdown | Твои архитектурные диаграммы видны прямо в превью | 2M+ |
| **17** | **REST Client** (humao.rest-client) | HTTP запросы прямо из .http файлов | Тестирование FastAPI endpoints без Postman | 8M+ |
| **18** | **OpenAPI Editor** (42Crunch.vscode-openapi) | Редактирование/превью OpenAPI spec | FastAPI генерирует OpenAPI, удобно проверять | 1.5M+ |
| **19** | **Remote - SSH** (ms-vscode-remote.remote-ssh) | Разработка на удалённом сервере | Подключение к VPS 94.198.219.232 для отладки | 20M+ |
| **20** | **Import Cost** (wix.vscode-import-cost) | Показывает размер импортируемых пакетов inline | Контроль bundle size в Next.js | 5M+ |

---

## Что ПРОПУСТИТЬ (и почему)

| Extension | Почему SKIP |
|-----------|------------|
| **GitHub Copilot** | У тебя Claude Code как primary AI. Copilot -- оверлэп. Если хочешь inline-автокомплит -- можно поставить, конфликтов нет, но это $10/мес за дубликат |
| **Cody (Sourcegraph)** | Оверлэп с Claude Code |
| **Continue / Cline / Roo Code** | Оверлэп с Claude Code. Anthropic рекомендует отключать при проблемах |
| **Black Formatter** | Ruff заменяет полностью |
| **isort** | Ruff заменяет |
| **Pylint / Flake8** | Ruff заменяет |
| **SonarLint** | Тяжёлый, медленный. Ruff + ESLint + Semgrep в CI достаточно |
| **Kubernetes** | У тебя нет K8s, только Docker Compose |
| **Jupyter** | Ставь только если реально используешь notebooks |
| **Better Comments** | Todo Tree покрывает 90% задач |

---

## Конфликты с Claude Code CLI

**Хорошая новость**: прямых конфликтов нет. Claude Code работает в терминале/своей панели, другие расширения -- в IDE слое. Но:

1. **Другие AI-агенты** (Cline, Continue, Roo Code) -- могут перехватывать diff view или terminal. Anthropic рекомендует отключать если есть проблемы
2. **GitHub Copilot** -- работает параллельно без проблем. Claude Code даже может быть agent внутри Copilot Pro+
3. **Chat history** -- если используешь несколько AI-расширений, история может путаться между ними

---

## Команда установки всех 20

```bash
# Tier 1: MUST HAVE
code --install-extension anthropic.claude-code
code --install-extension ms-python.python
code --install-extension ms-python.vscode-pylance
code --install-extension charliermarsh.ruff
code --install-extension usernamehw.errorlens
code --install-extension eamodio.gitlens
code --install-extension dbaeumer.vscode-eslint
code --install-extension esbenp.prettier-vscode
code --install-extension ms-azuretools.vscode-docker
code --install-extension ms-playwright.playwright

# Tier 2: NICE TO HAVE
code --install-extension ms-ossdata.vscode-postgresql
code --install-extension bradlc.vscode-tailwindcss
code --install-extension yoavbls.pretty-ts-errors
code --install-extension Gruntfuggly.todo-tree
code --install-extension GitHub.vscode-pull-request-github
code --install-extension bierner.markdown-mermaid
code --install-extension humao.rest-client
code --install-extension 42Crunch.vscode-openapi
code --install-extension ms-vscode-remote.remote-ssh
code --install-extension wix.vscode-import-cost
```

---

## Рекомендуемые настройки settings.json

```jsonc
{
  // Ruff как единственный Python formatter/linter
  "[python]": {
    "editor.defaultFormatter": "charliermarsh.ruff",
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
      "source.organizeImports": "explicit"
    }
  },
  // Prettier для JS/TS
  "[typescript]": { "editor.defaultFormatter": "esbenp.prettier-vscode" },
  "[typescriptreact]": { "editor.defaultFormatter": "esbenp.prettier-vscode" },
  "[json]": { "editor.defaultFormatter": "esbenp.prettier-vscode" },
  // Error Lens — не слишком навязчиво
  "errorLens.enabledDiagnosticLevels": ["error", "warning"],
  "errorLens.delay": 500,
  // GitLens — чистый blame без шума
  "gitlens.codeLens.enabled": false,
  "gitlens.currentLine.enabled": true,
  // Todo Tree
  "todo-tree.general.tags": ["TODO", "FIXME", "HACK", "BUG", "XXX"]
}
```

---

## Рекомендации к действию

1. **Сейчас**: установи Tier 1 (10 расширений) одной командой -- это 2 минуты
2. **Не ставь Copilot** пока Claude Code покрывает твои нужды. Сэкономишь $10/мес и не будешь путаться между двумя AI
3. **PostgreSQL extension от Microsoft** -- свежая (2025), реально крутая, с IntelliSense для SQL и визуализацией схемы. Заменяет SQLTools
4. **Ruff убивает 4 расширения** (Black, isort, Flake8, pyupgrade) -- если стоят старые, удали их

---

Sources:
- [The Best VS Code Extensions for 2026 - Builder.io](https://www.builder.io/blog/best-vs-code-extensions-2026)
- [Claude Code in VS Code - Official Docs](https://code.claude.com/docs/en/vs-code)
- [Claude Code for VS Code - Marketplace](https://marketplace.visualstudio.com/items?itemName=anthropic.claude-code)
- [10 Best VS Code Extensions for Python (2026)](https://towardsthecloud.com/blog/best-vscode-extensions-python)
- [Ruff Extension - VS Code Marketplace](https://marketplace.visualstudio.com/items?itemName=charliermarsh.ruff)
- [GitLens - VS Code Marketplace](https://marketplace.visualstudio.com/items?itemName=eamodio.gitlens)
- [Microsoft PostgreSQL Extension for VS Code](https://techcommunity.microsoft.com/blog/adforpostgresql/announcing-a-new-ide-for-postgresql-in-vs-code-from-microsoft/4414648)
- [Playwright Test for VS Code - Marketplace](https://marketplace.visualstudio.com/items?itemName=ms-playwright.playwright)
- [Error Lens - VS Code Marketplace](https://marketplace.visualstudio.com/items?itemName=usernamehw.errorlens)
- [Todo Tree - VS Code Marketplace](https://marketplace.visualstudio.com/items?itemName=Gruntfuggly.todo-tree)
- [OpenAPI (Swagger) Editor - Marketplace](https://marketplace.visualstudio.com/items?itemName=42Crunch.vscode-openapi)
- [Markdown Preview Mermaid - Marketplace](https://marketplace.visualstudio.com/items?itemName=bierner.markdown-mermaid)
- [Pretty TypeScript Errors - DEV Community](https://dev.to/best_codes/7-best-vs-code-extensions-for-faster-development-2026-edition-4gk0)
- [Claude Code vs GitHub Copilot - Codegen](https://codegen.com/blog/claude-code-vs-github-copilot/)
- [Using Claude Code with GitHub Copilot](https://anderssv.medium.com/using-claude-code-with-github-copilot-a-guide-42904ea6dce0)
- [Top Agentic AI Tools for VS Code](https://visualstudiomagazine.com/articles/2025/10/07/top-agentic-ai-tools-for-vs-code-according-to-installs.aspx)
