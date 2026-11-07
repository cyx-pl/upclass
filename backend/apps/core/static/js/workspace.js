/* Shared responsive navigation, with keyboard focus kept inside the mobile drawer. */
(() => {
  'use strict';
  const sidebar = document.getElementById('workspaceSidebar');
  if (!sidebar) return;
  const toggle = document.querySelector('.workspace-menu-button');
  const backdrop = document.querySelector('.workspace-backdrop');
  const mobile = window.matchMedia('(max-width: 1000px)');
  let previousOverflow = '';
  function setOpen(open, restoreFocus = true) {
    const wasOpen = document.body.classList.contains('workspace-menu-open');
    document.body.classList.toggle('workspace-menu-open', open);
    if (toggle) toggle.setAttribute('aria-expanded', String(open));
    if (backdrop) backdrop.hidden = !open;
    if (open && !wasOpen) {
      previousOverflow = document.body.style.overflow;
      document.body.style.overflow = 'hidden';
      sidebar.querySelector('a, button').focus();
    } else if (!open && wasOpen) {
      document.body.style.overflow = previousOverflow;
      if (restoreFocus && toggle) toggle.focus();
    }
  }
  if (toggle) toggle.addEventListener('click', () => setOpen(!document.body.classList.contains('workspace-menu-open')));
  document.querySelectorAll('[data-workspace-close]').forEach(el => el.addEventListener('click', () => setOpen(false)));
  mobile.addEventListener('change', () => setOpen(false, false));
  document.addEventListener('keydown', event => {
    if (!document.body.classList.contains('workspace-menu-open')) return;
    if (event.key === 'Escape') { event.preventDefault(); setOpen(false); }
    if (event.key === 'Tab') {
      const elements = [...sidebar.querySelectorAll('a, button, summary')].filter(el => el.getClientRects().length);
      const first = elements[0], last = elements[elements.length - 1];
      if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last.focus(); }
      else if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first.focus(); }
    }
  });
  const current = window.location.pathname;
  const links = [...sidebar.querySelectorAll('a.workspace-link')];
  let selected = links.find(link => new URL(link.href).pathname === current);
  if (!selected) selected = links.filter(link => {
    const path = new URL(link.href).pathname;
    return path !== '/admin/' && current.startsWith(path);
  }).sort((a, b) => b.pathname.length - a.pathname.length)[0];
  if (selected) {
    selected.setAttribute('aria-current', 'page');
    const group = selected.closest('details');
    if (group) group.open = true;
  }
  // Let wide tables scroll inside the content area rather than widening the page.
  document.querySelectorAll('#main-content table').forEach(table => {
    if (table.closest('.workspace-table-scroll, .table-responsive, .calendar-scroll')) return;
    const wrap = document.createElement('div');
    wrap.className = 'workspace-table-scroll';
    wrap.tabIndex = 0;
    wrap.setAttribute('role', 'region');
    wrap.setAttribute('aria-label', table.getAttribute('aria-label') || 'Tabela');
    table.before(wrap); wrap.appendChild(table);
  });
})();
