const API_URL = window.__API_URL__ || (() => {
  const hostname = window.location.hostname;
  
  if (hostname === 'localhost' || hostname === '127.0.0.1') {
      return `http://${hostname}:5001/api`;
  }

  return '/api';
})();

window.API_URL = API_URL;
