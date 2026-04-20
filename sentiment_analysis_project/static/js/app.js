'use strict';

const EMOJI   = { positive: '😊', negative: '😠', neutral: '😐' };
const SAMPLES = {
  pos: "I absolutely love this product! The quality exceeded all my expectations. Best purchase I've made all year — highly recommend to everyone!",
  neg: "Completely terrible experience. The customer service was rude and unhelpful. Product broke after one day and they refused to refund. Total waste of money.",
  neu: "The package arrived today. The product looks as described in the listing. Delivery took the expected amount of time. No issues to report."
};

// Char counter
document.getElementById('single-input').addEventListener('input', function () {
  document.getElementById('char-count').textContent = this.value.length;
});

function loadSample(type) {
  const ta = document.getElementById('single-input');
  ta.value = SAMPLES[type];
  document.getElementById('char-count').textContent = ta.value.length;
  ta.focus();
}

function showLoader(show) {
  document.getElementById('loader').classList.toggle('d-none', !show);
}

function sentClass(s) {
  return s === 'positive' ? 'pos' : s === 'negative' ? 'neg' : 'neu';
}

// ══════════════════════════════════════
// SINGLE ANALYSIS
// ══════════════════════════════════════
async function analyzeSingle() {
  const text = document.getElementById('single-input').value.trim();
  if (!text) { showToast('Please enter some text first.', 'warning'); return; }
  if (text.length > 5000) { showToast('Text is too long — keep it under 5000 characters.', 'danger'); return; }

  showLoader(true);
  try {
    const res  = await fetch('/analyze', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text })
    });
    const data = await res.json();
    if (!res.ok) { showToast(data.error || 'Analysis failed.', 'danger'); return; }
    renderSingleResult(data);
  } catch (e) {
    showToast('Server error — make sure the Flask app is running.', 'danger');
  } finally {
    showLoader(false);
  }
}

function clearSingle() {
  document.getElementById('single-input').value = '';
  document.getElementById('char-count').textContent = '0';
  document.getElementById('single-result').innerHTML   = '';
  document.getElementById('single-result').classList.add('d-none');
  document.getElementById('single-placeholder').classList.remove('d-none');
}

function renderSingleResult(d) {
  const s   = d.final_sentiment;
  const sc  = sentClass(s);
  const sub = Math.round(d.textblob.subjectivity * 100);

  document.getElementById('single-placeholder').classList.add('d-none');
  const container = document.getElementById('single-result');
  container.classList.remove('d-none');

  container.innerHTML = `
    <div class="siq-card">
      <!-- Result hero -->
      <div class="result-hero ${s}">
        <div class="result-emoji-big">${EMOJI[s]}</div>
        <div>
          <div class="result-label-big">${s} Sentiment</div>
          <div class="result-sublabel">Ensemble: VADER + TextBlob + ML Model</div>
        </div>
      </div>

      <!-- 3-model grid -->
      <div class="model-grid">
        <div class="model-tile">
          <div class="model-tile-label">VADER</div>
          <div class="model-tile-value">${d.vader.compound}</div>
          <div class="model-tile-sent sent-chip-${sentClass(d.vader.label)}">${d.vader.label}</div>
        </div>
        <div class="model-tile">
          <div class="model-tile-label">TextBlob</div>
          <div class="model-tile-value">${d.textblob.polarity}</div>
          <div class="model-tile-sent sent-chip-${sentClass(d.textblob.label)}">${d.textblob.label}</div>
        </div>
        <div class="model-tile">
          <div class="model-tile-label">ML Model</div>
          <div class="model-tile-value">${d.ml_model.confidence}%</div>
          <div class="model-tile-sent sent-chip-${sentClass(d.ml_model.label)}">${d.ml_model.label}</div>
        </div>
      </div>

      <!-- Score bars -->
      <div class="score-section">
        <h6>VADER Score Breakdown</h6>
        ${scoreBar('Positive', d.vader.positive, 'pos')}
        ${scoreBar('Negative', d.vader.negative, 'neg')}
        ${scoreBar('Neutral',  d.vader.neutral,  'neu')}
      </div>

      <!-- Subjectivity meter -->
      <div class="sub-meter-row">
        <h6>Subjectivity Meter</h6>
        <div class="sub-track">
          <div class="sub-marker" id="sub-marker" style="left:0%"></div>
        </div>
        <div class="sub-labels">
          <span>Objective</span>
          <span>${sub}% Subjective</span>
          <span>Subjective</span>
        </div>
      </div>

      ${d.keywords.length ? `
      <!-- Keywords -->
      <div class="kw-section">
        <h6>Key Words Detected</h6>
        <div class="kw-chips">
          ${d.keywords.map(k => `<span class="kw-chip">${k.word}</span>`).join('')}
        </div>
      </div>` : ''}

      <!-- Footer stats -->
      <div class="result-footer">
        <span class="result-footer-stat"><strong>${d.word_count}</strong> words</span>
        <span class="result-footer-stat"><strong>${d.char_count}</strong> characters</span>
        <span class="result-footer-stat">TextBlob polarity: <strong>${d.textblob.polarity}</strong></span>
        <span class="result-footer-stat">ML confidence: <strong>${d.ml_model.confidence}%</strong></span>
      </div>
    </div>
  `;

  // Animate bars + subjectivity marker
  setTimeout(() => {
    document.querySelectorAll('.score-fill').forEach(b => { b.style.width = b.dataset.w + '%'; });
    const marker = document.getElementById('sub-marker');
    if (marker) marker.style.left = sub + '%';
  }, 60);

  container.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function scoreBar(label, val, type) {
  return `<div class="score-row">
    <div class="score-lbl">${label}</div>
    <div class="score-track"><div class="score-fill fill-${type}" data-w="${val}" style="width:0%"></div></div>
    <div class="score-val">${val}%</div>
  </div>`;
}

// ══════════════════════════════════════
// BULK ANALYSIS
// ══════════════════════════════════════
async function analyzeBulk() {
  const raw   = document.getElementById('bulk-input').value.trim();
  const texts = raw.split('\n').map(t => t.trim()).filter(Boolean);
  if (!texts.length) { showToast('Please enter at least one line of text.', 'warning'); return; }

  showLoader(true);
  try {
    const res  = await fetch('/analyze_bulk', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ texts })
    });
    const data = await res.json();
    if (!res.ok) { showToast(data.error || 'Bulk analysis failed.', 'danger'); return; }
    renderBulkResult(data, 'bulk-result', 'bulk-placeholder');
  } catch (e) {
    showToast('Server error — make sure the Flask app is running.', 'danger');
  } finally {
    showLoader(false);
  }
}

// ══════════════════════════════════════
// DEMO
// ══════════════════════════════════════
async function runDemo() {
  // Switch to demo tab
  const demoTab = document.querySelector('[data-bs-target="#tab-demo"]');
  if (demoTab) bootstrap.Tab.getOrCreateInstance(demoTab).show();

  showLoader(true);
  try {
    const res  = await fetch('/demo');
    const data = await res.json();
    renderBulkResult(data, 'demo-result', null);
  } catch (e) {
    showToast('Server error — make sure the Flask app is running.', 'danger');
  } finally {
    showLoader(false);
  }
}

// ══════════════════════════════════════
// SHARED BULK RENDER
// ══════════════════════════════════════
let chartInstances = {};

function renderBulkResult(data, containerId, placeholderId) {
  if (placeholderId) {
    const ph = document.getElementById(placeholderId);
    if (ph) ph.classList.add('d-none');
  }

  const container = document.getElementById(containerId);
  container.classList.remove('d-none');

  const { total, positive: pos, negative: neg, neutral: neu, results } = data;
  const uid = containerId; // unique suffix for chart canvas ids

  container.innerHTML = `
    <!-- Summary tiles -->
    <div class="summary-grid mb-4">
      <div class="summary-tile s-total">
        <div class="summary-tile-num">${total}</div>
        <div class="summary-tile-lbl">Total Texts</div>
      </div>
      <div class="summary-tile s-positive">
        <div class="summary-tile-num">${pos}</div>
        <div class="summary-tile-lbl">Positive (${pct(pos,total)}%)</div>
      </div>
      <div class="summary-tile s-negative">
        <div class="summary-tile-num">${neg}</div>
        <div class="summary-tile-lbl">Negative (${pct(neg,total)}%)</div>
      </div>
      <div class="summary-tile s-neutral">
        <div class="summary-tile-num">${neu}</div>
        <div class="summary-tile-lbl">Neutral (${pct(neu,total)}%)</div>
      </div>
    </div>

    <!-- Charts -->
    <div class="chart-pair mb-4">
      <div class="chart-tile">
        <h6>Sentiment Distribution</h6>
        <canvas id="pie-${uid}" height="220"></canvas>
      </div>
      <div class="chart-tile">
        <h6>VADER Compound Scores</h6>
        <canvas id="bar-${uid}" height="220"></canvas>
      </div>
    </div>

    <!-- Individual results -->
    <div class="siq-card">
      <div class="siq-card-header">
        <i class="bi bi-list-ul me-2"></i>Individual Results (${total} texts)
      </div>
      <div class="siq-card-body">
        <div class="bulk-list">
          ${results.map((r, i) => `
            <div class="bulk-item">
              <div class="bulk-num">#${i+1}</div>
              <div class="bulk-dot dot-${sentClass(r.final_sentiment)}"></div>
              <div class="bulk-text">${escHtml(r.text.substring(0,110))}${r.text.length>110?'...':''}</div>
              <span class="bulk-chip chip-${sentClass(r.final_sentiment)}">${r.final_sentiment}</span>
              <span class="bulk-conf">${r.ml_model.confidence}%</span>
            </div>
          `).join('')}
        </div>
      </div>
    </div>
  `;

  // Destroy old charts if they exist
  ['pie-'+uid, 'bar-'+uid].forEach(id => {
    if (chartInstances[id]) { chartInstances[id].destroy(); delete chartInstances[id]; }
  });

  // Pie chart
  chartInstances['pie-'+uid] = new Chart(document.getElementById('pie-'+uid), {
    type: 'doughnut',
    data: {
      labels: ['Positive', 'Negative', 'Neutral'],
      datasets: [{
        data: [pos, neg, neu],
        backgroundColor: ['#10b981', '#ef4444', '#06b6d4'],
        borderWidth: 0, hoverOffset: 8
      }]
    },
    options: {
      plugins: {
        legend: { position: 'bottom', labels: { padding: 16, font: { size: 12, weight: '600' } } }
      },
      cutout: '65%'
    }
  });

  // Bar chart
  const compounds = results.map(r => r.vader.compound);
  const colors    = results.map(r =>
    r.final_sentiment === 'positive' ? '#10b981' :
    r.final_sentiment === 'negative' ? '#ef4444' : '#06b6d4'
  );
  chartInstances['bar-'+uid] = new Chart(document.getElementById('bar-'+uid), {
    type: 'bar',
    data: {
      labels: results.map((_, i) => `#${i+1}`),
      datasets: [{
        label: 'Compound', data: compounds,
        backgroundColor: colors, borderRadius: 6, borderSkipped: false
      }]
    },
    options: {
      plugins: { legend: { display: false } },
      scales: {
        y: { min: -1, max: 1, grid: { color: '#f1f5f9' }, ticks: { font: { size: 11 } } },
        x: { grid: { display: false }, ticks: { font: { size: 11 } } }
      }
    }
  });

  container.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// ══════════════════════════════════════
// HELPERS
// ══════════════════════════════════════
function pct(val, total) { return total ? Math.round((val / total) * 100) : 0; }

function escHtml(str) {
  return str.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

function showToast(msg, type = 'info') {
  const div = document.createElement('div');
  div.className = `alert alert-${type} position-fixed shadow-lg`;
  div.style.cssText = 'bottom:24px;right:24px;z-index:9999;max-width:340px;border-radius:14px;font-size:.88rem;font-weight:500;animation:slideIn .3s ease';
  div.textContent = msg;
  document.body.appendChild(div);
  setTimeout(() => div.remove(), 3500);
}

// Add slideIn animation
const style = document.createElement('style');
style.textContent = '@keyframes slideIn{from{transform:translateX(120%);opacity:0}to{transform:translateX(0);opacity:1}}';
document.head.appendChild(style);
