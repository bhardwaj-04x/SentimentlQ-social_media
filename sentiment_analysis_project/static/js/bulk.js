'use strict';

const EMOJI = { positive: '😊', negative: '😠', neutral: '😐' };
let chartInstances = {};

// Line counter
document.getElementById('bulk-input').addEventListener('input', function () {
  const lines = this.value.split('\n').filter(l => l.trim()).length;
  document.getElementById('line-count').textContent = lines + ' line' + (lines !== 1 ? 's' : '');
});

async function analyzeBulk() {
  const raw   = document.getElementById('bulk-input').value.trim();
  const texts = raw.split('\n').map(t => t.trim()).filter(Boolean);
  if (!texts.length) { showToast('Please enter at least one line of text.', 'warning'); return; }
  if (texts.length > 50) { showToast('Maximum 50 lines allowed.', 'warning'); return; }

  showLoader(true);
  try {
    const res  = await fetch('/analyze_bulk', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ texts })
    });
    const data = await res.json();
    if (!res.ok) { showToast(data.error || 'Bulk analysis failed.', 'danger'); return; }
    renderBulk(data);
  } catch {
    showToast('Server error — make sure Flask app is running.', 'danger');
  } finally { showLoader(false); }
}

function clearBulk() {
  document.getElementById('bulk-input').value = '';
  document.getElementById('line-count').textContent = '0 lines';
  document.getElementById('bulk-result').innerHTML = '';
  document.getElementById('bulk-result').classList.add('d-none');
  document.getElementById('bulk-placeholder').classList.remove('d-none');
}

function renderBulk(data) {
  document.getElementById('bulk-placeholder').classList.add('d-none');
  const container = document.getElementById('bulk-result');
  container.classList.remove('d-none');

  const { total, positive: pos, negative: neg, neutral: neu, results } = data;

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
        <canvas id="pie-bulk" height="220"></canvas>
      </div>
      <div class="chart-tile">
        <h6>VADER Compound Scores</h6>
        <canvas id="bar-bulk" height="220"></canvas>
      </div>
    </div>

    <!-- Results list -->
    <div class="siq-card">
      <div class="siq-card-header">
        <i class="bi bi-list-ul me-2"></i>Individual Results (${total} texts)
        <span class="ms-auto owner-mini">Sakshi Puri | 24BET10158</span>
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

  // Destroy old charts
  ['pie-bulk','bar-bulk'].forEach(id => {
    if (chartInstances[id]) { chartInstances[id].destroy(); delete chartInstances[id]; }
  });

  chartInstances['pie-bulk'] = new Chart(document.getElementById('pie-bulk'), {
    type: 'doughnut',
    data: {
      labels: ['Positive','Negative','Neutral'],
      datasets: [{ data:[pos,neg,neu], backgroundColor:['#10b981','#ef4444','#06b6d4'], borderWidth:0, hoverOffset:8 }]
    },
    options: { plugins: { legend: { position:'bottom', labels:{ padding:16, font:{ size:12, weight:'600' } } } }, cutout:'65%' }
  });

  const colors = results.map(r => r.final_sentiment==='positive' ? '#10b981' : r.final_sentiment==='negative' ? '#ef4444' : '#06b6d4');
  chartInstances['bar-bulk'] = new Chart(document.getElementById('bar-bulk'), {
    type: 'bar',
    data: {
      labels: results.map((_,i) => `#${i+1}`),
      datasets: [{ label:'Compound', data: results.map(r => r.vader.compound), backgroundColor: colors, borderRadius: 6, borderSkipped: false }]
    },
    options: {
      plugins: { legend: { display: false } },
      scales: {
        y: { min:-1, max:1, grid:{ color:'#f1f5f9' }, ticks:{ font:{ size:11 } } },
        x: { grid:{ display:false }, ticks:{ font:{ size:11 } } }
      }
    }
  });

  container.scrollIntoView({ behavior:'smooth', block:'start' });
}
