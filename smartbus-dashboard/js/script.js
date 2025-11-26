(function () {
  const POLL_INTERVAL = 3000;

  function getApiUrl() {
    return window.API_URL || window.__API_URL__ || (() => {
      const h = window.__API_HOST__ || window.location.hostname;
      const p = window.__API_PORT__ || window.location.port || 5001;
      return `${window.location.protocol}//${h}:${p}/api`;
    })();
  }

  const API = getApiUrl();

  function createWidget() {
    if (document.getElementById('smartbus-iot-widget')) return;
    const w = document.createElement('div');
    w.id = 'smartbus-iot-widget';
    w.style.position = 'fixed';
    w.style.right = '16px';
    w.style.top = '80px';
    w.style.zIndex = '9999';
    w.style.background = 'rgba(26,31,56,0.95)';
    w.style.color = '#fff';
    w.style.padding = '12px 16px';
    w.style.borderRadius = '12px';
    w.style.boxShadow = '0 6px 18px rgba(0,0,0,0.3)';
    w.style.minWidth = '220px';
    w.style.fontFamily = 'Arial, sans-serif';
    w.innerHTML = `
      <div style="font-weight:700; margin-bottom:8px">IoT — Leituras (ao vivo)</div>
      <div style="font-size:14px; line-height:1.4">
        <div>Temp: <span id="sb-temp">–</span> °C</div>
        <div>Umid: <span id="sb-umid">–</span> %</div>
        <div>Ar: <span id="sb-ar">–</span></div>
        <div>LED: <span id="sb-led">–</span></div>
        <div>Faces: <span id="sb-faces">–</span></div>
        <div style="margin-top:6px; font-size:11px; opacity:0.85">Atual: <span id="sb-atual">–</span></div>
      </div>
    `;
    document.body.appendChild(w);
  }

  function safeText(id, txt) {
    const el = document.getElementById(id);
    if (el) el.textContent = txt;
  }

  async function fetchThresholds() {
    try {
      const r = await fetch(`${API}/thresholds`);
      if (!r.ok) return null;
      return await r.json();
    } catch (e) {
      return null;
    }
  }

  function colorForAr(value, thresholds) {
    // thresholds may be null — fallback simple ranges
    const v = Number(value || 0);
    const good = thresholds?.ar_bom ?? 500;
    const mod = thresholds?.ar_moderado ?? 1500;
    if (v <= good) return '#10b981'; // green
    if (v <= mod) return '#f59e0b';  // amber
    return '#ef4444';               // red
  }

  async function updateOnce() {
    try {
      const [tRes, lRes] = await Promise.all([
        fetchThresholds(),
        fetch(`${API}/leituras?limite=1`)
      ]);
      let leituras = null;
      if (lRes && lRes.ok) {
        const json = await lRes.json();
        // aceita formatos {leituras: [...]} ou lista direta
        leituras = Array.isArray(json.leituras) ? json.leituras : (Array.isArray(json) ? json : []);
      } else {
        leituras = [];
      }

      const last = leituras && leituras.length ? leituras[0] : null;

      createWidget();

      if (last) {
        safeText('sb-temp', (last.temperatura !== undefined) ? Number(last.temperatura).toFixed(1) : '–');
        safeText('sb-umid', (last.umidade !== undefined) ? Number(last.umidade).toFixed(1) : '–');
        safeText('sb-ar', last.qualidadeAr ?? (last.qualidade_ar ?? '–'));
        safeText('sb-led', last.led_ativo ? 'Ligado' : 'Desligado');
        safeText('sb-faces', String(last.faces_detectadas ?? last.rostos ?? '0'));
        safeText('sb-atual', new Date(last.timestamp || Date.now()).toLocaleTimeString());
        // colorize background border by air quality
        const widget = document.getElementById('smartbus-iot-widget');
        const color = colorForAr(last.qualidadeAr ?? last.qualidade_ar, tRes);
        if (widget) widget.style.border = `3px solid ${color}`;
      } else {
        safeText('sb-temp', '–');
        safeText('sb-umid', '–');
        safeText('sb-ar', '–');
        safeText('sb-led', '–');
        safeText('sb-faces', '–');
        safeText('sb-atual', new Date().toLocaleTimeString());
      }
    } catch (err) {
      // não poluir console demais
      console.debug('smartbus widget fetch error', err);
    }
  }

  // aguarda API_URL caso config.js carregue assíncrono
  function waitForApiReady(timeout = 3000) {
    return new Promise(resolve => {
      const start = Date.now();
      (function check() {
        if (window.API_URL || window.__API_URL__) return resolve();
        if (Date.now() - start > timeout) return resolve();
        setTimeout(check, 100);
      })();
    });
  }

  (async function main() {
    await waitForApiReady(2000);
    // primeira atualização imediata
    updateOnce();
    setInterval(updateOnce, POLL_INTERVAL);
  })();
})();