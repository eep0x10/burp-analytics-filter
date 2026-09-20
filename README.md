<div align="center">

<img src="docs/assets/banner.png" alt="Burp Analytics Filter — ilustração de marca" width="100%">

# Burp Analytics Filter

### Menos ruído. Mais contexto.

Extensão para marcar requisições de analytics, telemetria e connectivity checks no Proxy History. A marcação permite filtrar visualmente o histórico durante análises autorizadas, sem bloquear o tráfego.

[![Extensão: Jython](https://img.shields.io/badge/Extens%C3%A3o-Jython-34495e?style=flat-square)](analytics_filter.py) [![Licença: MIT](https://img.shields.io/badge/Licen%C3%A7a-MIT-34495e?style=flat-square)](LICENSE)

[Instalação](#instalação) · [Uso](#uso) · [Como validar](#como-validar) · [Código e licença](#código-e-licença)

</div>

> O banner é uma ilustração conceitual de marca criada com IA; não é uma captura da aplicação nem comprovação de um resultado real.

| Identifique | Marque | Concentre |
| :--- | :--- | :--- |
| Compare URLs com os padrões de telemetria. | Aplique destaque cinza e comentário analytics. | Use o filtro visual do histórico sem bloquear tráfego. |

## Instalação

Requer Burp Suite com suporte a extensões Python/Jython e o JAR standalone do Jython configurado no ambiente de extensões.

1. Clone o repositório ou obtenha [analytics_filter.py](analytics_filter.py).
2. No gerenciador de extensões do Burp, adicione uma extensão do tipo **Python**.
3. Selecione o arquivo e confirme a abertura da aba **Analytics Filter**.

Os nomes dos menus variam entre versões do Burp. Esta extensão usa a API clássica `IProxyListener`, não a API Montoya.

## Uso

Requisições que correspondem aos padrões recebem destaque **cinza** e comentário **analytics**. Configure o filtro de cor do Proxy History para ocultá-las quando desejar. A aba da extensão permite editar os padrões e aplicá-los durante a sessão.

| Configuração | Persistência |
| --- | --- |
| Editar e aplicar na aba | Sessão atual. |
| Alterar `DEFAULT_PATTERNS` no código | Próximas cargas da extensão. |

As expressões são compiladas com `re.IGNORECASE` e comparadas com `re.search` na URL. Os padrões cobrem serviços de analytics, monitoramento, marketing e caminhos genéricos de telemetria.

## Como validar

Em um projeto de teste, envie uma URL que corresponda a um padrão e outra que não corresponda. Verifique destaque e comentário, aplique um novo padrão e repita. Confirme que o tráfego continua presente ao remover o filtro visual.

Não há suíte automatizada incluída. Padrões amplos podem classificar tráfego relevante incorretamente; a marcação não comprova que uma requisição é inofensiva. A extensão pode substituir destaque/comentário existentes nos itens correspondentes.

## Código e licença

[Implementação](analytics_filter.py) · [Licença MIT](LICENSE)
