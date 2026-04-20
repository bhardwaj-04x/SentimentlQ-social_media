'use strict';
// Shared helpers used on every page

function showLoader(show) {
  document.getElementById('loader').classList.toggle('d-none', !show);
}

function showToast(msg, type = 'info') {
  const d = document.createElement('div');
  d.className = `alert alert-${type} position-fixed shadow-lg`;
  d.style.cssText = 'bottom:24px;right:24px;z-index:99999;max-width:340px;border-radius:14px;font-size:.88rem;font-weight:500';
  d.textContent = msg;
  document.body.appendChild(d);
  setTimeout(() => d.remove(), 3500);
}

function escHtml(s) {
  return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

function pct(v, t) { return t ? Math.round((v / t) * 100) : 0; }

function sentClass(s) {
  return s === 'positive' ? 'pos' : s === 'negative' ? 'neg' : 'neu';
}

// Bootstrap tooltips
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('[data-bs-toggle="tooltip"]')
    .forEach(el => new bootstrap.Tooltip(el));
});

// Slide-in toast animation
const _style = document.createElement('style');
_style.textContent = '@keyframes slideIn{from{transform:translateX(120%);opacity:0}to{transform:translateX(0);opacity:1}}';
document.head.appendChild(_style);
