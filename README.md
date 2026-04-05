# Burp Suite Analytics Filter

Extensão Burp Suite (Jython) que detecta e marca automaticamente chamadas de analytics, telemetria e connectivity checks no Proxy History — eliminando o ruído de SDKs de terceiros durante pentests mobile e web.

## Como funciona

A extensão registra um `IProxyListener` e, para cada requisição que passar pelo proxy, verifica a URL contra uma lista de regex. Se bater, a requisição recebe:

- **Highlight:** cinza (`gray`)
- **Comment:** `analytics`

No Proxy History, basta filtrar por `Color = gray` para esconder todo o ruído automaticamente.

## Instalação

1. Burp Suite → **Extender → Extensions → Add**
2. Extension Type: **Python**
3. Selecionar o arquivo `analytics_filter.py`
4. Confirmar que a aba **"Analytics Filter"** apareceu na barra superior

> **Requisito:** Jython standalone JAR configurado em Extender → Options → Python Environment.

## Uso

Após carregar a extensão:

1. **No Proxy History:** clique no ícone de filtro → marque **"Hide items with color"** → selecione **Gray**
2. Todo tráfego de analytics/telemetria some da view
3. A aba **Analytics Filter** exibe o contador de requisições ocultadas e permite editar os padrões em runtime (botão "Aplicar padrões")

![Analytics Filter tab](docs/tab-screenshot.png)

## Padrões incluídos por padrão

| Categoria | Exemplos |
|-----------|---------|
| Connectivity checks | `connectivitycheck.gstatic.com`, `www.google.com/gen_204`, `/generate_204` |
| Google Analytics / Firebase | `google-analytics.com`, `firebaselogging`, `app-measurement.com` |
| Meta / Facebook | `connect.facebook.net`, `facebook.com/tr` |
| Amplitude / Mixpanel / Segment | `amplitude.com`, `mixpanel.com`, `api.segment.io` |
| AppsFlyer / Adjust / Branch | `appsflyer.com`, `adjust.com`, `branch.io` |
| Sentry / Bugsnag / New Relic | `sentry.io`, `bugsnag.com`, `nr-data.net` |
| Datadog / Dynatrace | `datadoghq.com`, `live.dynatrace.com` |
| Marketing Cloud (Salesforce) | `marketingcloudapis.com`, `exacttarget.com` |
| Braze / Hotjar / FullStory | `braze.com`, `hotjar.com`, `fullstory.com` |
| Paths genéricos | `/telemetry/`, `/beacon/`, `/pixel/`, `/tracking/` |

## Adicionando padrões personalizados

**Runtime (sem reiniciar):**
- Aba Analytics Filter → editar a caixa de texto → clicar **"Aplicar padrões"**

**Permanente:**
- Editar a lista `DEFAULT_PATTERNS` em `analytics_filter.py` antes de carregar a extensão

Os padrões são regex Python (case-insensitive, `re.search` na URL completa).

## Contexto de uso — pentest mobile

Durante pentests mobile o histórico do Burp enche de ruído de SDKs:

```
8672  connectivitycheck.gstatic.com  GET  /generate_204  → analytics (gray)
8671  www.google.com                 GET  /gen_204        → analytics (gray)
8670  firebaselogging.googleapis.com POST /v1/...         → analytics (gray)
8669  appsflyer.com                  POST /inappevent     → analytics (gray)
8510  api.target-app.com             POST /auth/login     → ALVO ← fácil de achar
```

Sem o filtro, achar a requisição de autenticação do alvo no meio de centenas de SDKs custa tempo e contexto.

## Licença

MIT — use, modifique e distribua livremente.
