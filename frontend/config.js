const API_URL = window.__API_URL__ || (() => {
  const host = window.__API_HOST__ || window.location.hostname;
  const port = window.__API_PORT__ || window.location.port || 5001;
  const proto = window.location.protocol || 'http:';
  return `${proto}//${host}:${port}/api`;
})();

window.API_URL = API_URL;