/* Simple hash-based SPA router:
   - navigate() is called from sidebar links and app.js
   - hashchange handles browser back/forward
   - Initial render is triggered by app.js (DOMContentLoaded) */
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