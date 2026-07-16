/* Nexus Client Portal — Hash-based SPA Router */
let currentView = 'login';

function navigate(view) {
  currentView = view;
  window.location.hash = view;
  render(view);
}

window.addEventListener('hashchange', () => {
  const view = window.location.hash.slice(1) || 'login';
  currentView = view;
  render(view);
});

(function init() {
  const view = window.location.hash.slice(1) || 'login';
  currentView = view;
  render(view);
})();