/* Simple hash-based SPA router */
function navigate(view, params) {
  currentView = view;
  window.location.hash = view;
  render(view, params);
}

window.addEventListener('hashchange', () => {
  const view = window.location.hash.slice(1) || 'dashboard';
  currentView = view;
  render(view);
});

window.addEventListener('DOMContentLoaded', () => {
  const view = window.location.hash.slice(1) || 'login';
  currentView = view;
  render(view);
});