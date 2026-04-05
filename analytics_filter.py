# -*- coding: utf-8 -*-
"""
Analytics Filter — Extensão Burp Suite (Jython)
Oculta passivamente todas as chamadas de analytics/telemetria no Proxy History.

Instalação:
  Extender → Extensions → Add → Extension Type: Python → Select file: analytics_filter.py

Uso:
  - Habilite a extensão. Todas as requisições de analytics serão marcadas com
    highlight "gray" e comment "analytics" no Proxy History.
  - No Proxy History, configure o filtro: Hide items with color: gray
  - A aba "Analytics Filter" mostra contagem e permite editar os padrões em runtime.
"""
from burp import IBurpExtender, IProxyListener, ITab
from javax.swing import (JPanel, JCheckBox, JLabel, JScrollPane, JTextArea,
                         JButton, BoxLayout, BorderFactory, SwingUtilities)
from java.awt import BorderLayout, Font
import re
import threading

# ---------------------------------------------------------------------------
# Padrões de analytics conhecidos (regex, case-insensitive, match na URL)
# ---------------------------------------------------------------------------
DEFAULT_PATTERNS = [
    # Google
    r'google-analytics\.com',
    r'googletagmanager\.com',
    r'analytics\.google\.com',
    r'gtag/js',
    r'app-measurement\.com',
    r'/__utm\.gif',
    r'/collect\?v=\d',           # GA hit endpoint
    r'/g/collect',               # GA4 endpoint

    # Firebase
    r'firebaselogging',
    r'firebaseinstallations',
    r'firebase-settings',
    r'crashlyticsreports-pa',

    # Meta / Facebook
    r'connect\.facebook\.net',
    r'facebook\.com/tr[/?]',
    r'fbevents\.js',

    # Microsoft Clarity
    r'clarity\.ms',

    # Hotjar
    r'hotjar\.com',
    r'static\.hotjar\.com',

    # Mixpanel
    r'mixpanel\.com',
    r'api\.mixpanel\.com',

    # Amplitude
    r'amplitude\.com',
    r'api\.amplitude\.com',
    r'api2\.amplitude\.com',

    # Segment
    r'cdn\.segment\.com',
    r'api\.segment\.io',
    r'segment\.io/v\d+/t',

    # Heap
    r'heap\.io',
    r'heapanalytics\.com',

    # FullStory
    r'fullstory\.com',
    r'rs\.fullstory\.com',

    # LogRocket
    r'logrocket\.com',
    r'r\.lr-ingest\.io',

    # Sentry / Bugsnag
    r'sentry\.io',
    r'ingest\.sentry\.io',
    r'bugsnag\.com',
    r'notify\.bugsnag\.com',

    # New Relic
    r'newrelic\.com',
    r'nr-data\.net',
    r'bam\.nr-data\.net',

    # Datadog
    r'datadoghq\.com',
    r'rum\.browser-intake-datadoghq\.com',

    # AppsFlyer
    r'appsflyer\.com',
    r'launches\.appsflyer\.com',

    # Adjust
    r'adjust\.com',
    r'app\.adjust\.com',

    # Branch.io
    r'branch\.io',
    r'api2\.branch\.io',

    # Braze / Appboy
    r'braze\.com',
    r'iad\.appboy\.com',

    # Snowplow
    r'snowplow',
    r'sp\.js',

    # Intercom
    r'intercom\.io',
    r'api-iam\.intercom\.io',

    # TikTok Pixel
    r'analytics\.tiktok\.com',

    # Twitter / X
    r'analytics\.twitter\.com',
    r'static\.ads-twitter\.com',

    # LinkedIn Insight
    r'snap\.licdn\.com',
    r'px\.ads\.linkedin\.com',

    # Connectivity checks (Android, Chrome, iOS, Windows)
    r'connectivitycheck\.gstatic\.com',
    r'connectivitycheck\.gst\.googleapis\.com',  # dominio novo Android
    r'connectivitycheck\.',                       # qualquer subdomain connectivitycheck
    r'www\.google\.com/gen_204',
    r'www\.google\.com/generate_204',
    r'clients\d+\.google\.com/generate_204',
    r'gstatic\.com/generate_204',
    r'play\.googleapis\.com',                     # era /log apenas — agora pega /generate_204 tambem
    r'/generate_204',                             # qualquer host fazendo connectivity check
    r'/gen_204',                                  # alias curto do connectivity check (www.google.com etc)
    r'captive\.apple\.com',
    r'www\.appleiphonecell\.com',
    r'msftconnecttest\.com',
    r'msftncsi\.com',
    r'detectportal\.firefox\.com',
    r'nmcheck\.gnome\.org',
    r'network-test\.debian\.org',

    # Generic paths que indicam analytics
    r'/telemetry[/?]',
    r'/diagnostics[/?]',
    r'/metrics[/?]',
    r'/perf[/?]',
    r'/rum[/?]',
    r'/_log[/?]',
    r'/beacon[/?]',
    r'/pixel[/?]',
    r'/tracking[/?]',
    r'/events[/?].*event_type=',
    r'/log\?.*timestamp=',
]


class BurpExtender(IBurpExtender, IProxyListener, ITab):

    EXTENSION_NAME = "Analytics Filter"

    def registerExtenderCallbacks(self, callbacks):
        self._callbacks = callbacks
        self._helpers = callbacks.getHelpers()
        callbacks.setExtensionName(self.EXTENSION_NAME)

        self._enabled = True
        self._hidden_count = 0
        self._lock = threading.Lock()
        self._ui_ready = False
        self._patterns = list(DEFAULT_PATTERNS)
        self._compiled = self._compile(self._patterns)

        self._build_ui()
        self._ui_ready = True
        callbacks.addSuiteTab(self)
        callbacks.registerProxyListener(self)

        print("[Analytics Filter] Carregado — %d padroes ativos" % len(self._compiled))
        print("[Analytics Filter] Dica: no Proxy History, filtre por Color = gray para ocultar")

    # ------------------------------------------------------------------
    # IProxyListener
    # ------------------------------------------------------------------

    def processProxyMessage(self, messageIsRequest, message):
        if not self._enabled or not messageIsRequest:
            return

        info = self._helpers.analyzeRequest(message.getMessageInfo())
        url = str(info.getUrl())

        if self._is_analytics(url):
            mi = message.getMessageInfo()
            mi.setHighlight("gray")
            mi.setComment("analytics")
            with self._lock:
                self._hidden_count += 1
                count = self._hidden_count
            if self._ui_ready:
                SwingUtilities.invokeLater(lambda: self._lbl_count.setText("Ocultados: %d" % count))

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _is_analytics(self, url):
        for regex in self._compiled:
            if regex.search(url):
                return True
        return False

    def _compile(self, patterns):
        compiled = []
        for p in patterns:
            p = p.strip()
            if not p:
                continue
            try:
                compiled.append(re.compile(p, re.IGNORECASE))
            except Exception as e:
                print("[Analytics Filter] Padrao invalido ignorado: %s (%s)" % (p, e))
        return compiled

    # ------------------------------------------------------------------
    # UI
    # ------------------------------------------------------------------

    def _build_ui(self):
        self._panel = JPanel(BorderLayout())

        # --- Barra superior ---
        top = JPanel()
        top.setLayout(BoxLayout(top, BoxLayout.X_AXIS))
        top.setBorder(BorderFactory.createEmptyBorder(10, 14, 10, 14))

        self._chk_enabled = JCheckBox("Ativo", True)
        self._chk_enabled.addActionListener(lambda e: self._on_toggle())
        top.add(self._chk_enabled)

        top.add(JLabel("     "))
        self._lbl_count = JLabel("Ocultados: 0")
        top.add(self._lbl_count)

        top.add(JLabel("     |     "))
        top.add(JLabel(u"Proxy History \u2192 filtrar Color = gray"))

        top.add(JLabel("     "))
        btn_reset = JButton("Resetar contagem")
        btn_reset.addActionListener(lambda e: self._on_reset())
        top.add(btn_reset)

        self._panel.add(top, BorderLayout.NORTH)

        # --- Área de padrões ---
        self._txt = JTextArea("\n".join(DEFAULT_PATTERNS))
        self._txt.setFont(Font("Monospaced", Font.PLAIN, 12))
        scroll = JScrollPane(self._txt)
        scroll.setBorder(BorderFactory.createTitledBorder(
            "Padroes regex (um por linha — match na URL completa, case-insensitive)"))

        btn_apply = JButton("Aplicar padroes")
        btn_apply.addActionListener(lambda e: self._on_apply())

        btn_panel = JPanel()
        btn_panel.add(btn_apply)

        center = JPanel(BorderLayout())
        center.setBorder(BorderFactory.createEmptyBorder(0, 14, 14, 14))
        center.add(scroll, BorderLayout.CENTER)
        center.add(btn_panel, BorderLayout.SOUTH)

        self._panel.add(center, BorderLayout.CENTER)

    def _on_toggle(self):
        self._enabled = self._chk_enabled.isSelected()
        print("[Analytics Filter] %s" % ("Ativado" if self._enabled else "Desativado"))

    def _on_reset(self):
        with self._lock:
            self._hidden_count = 0
        self._lbl_count.setText("Ocultados: 0")

    def _on_apply(self):
        lines = self._txt.getText().strip().split("\n")
        self._patterns = [l.strip() for l in lines if l.strip()]
        self._compiled = self._compile(self._patterns)
        print("[Analytics Filter] %d padroes recarregados" % len(self._compiled))

    # ------------------------------------------------------------------
    # ITab
    # ------------------------------------------------------------------

    def getTabCaption(self):
        return self.EXTENSION_NAME

    def getUiComponent(self):
        return self._panel
