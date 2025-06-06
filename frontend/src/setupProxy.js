const { createProxyMiddleware } = require('http-proxy-middleware');

module.exports = function(app) {
  app.use(
    '/api', // Proxy requests starting with /api
    createProxyMiddleware({
      target: 'http://127.0.0.1:5000', // Your backend server
      changeOrigin: true,
    })
  );
};