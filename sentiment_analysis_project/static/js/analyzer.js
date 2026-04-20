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

// Ctrl+Enter shortcut
document.getElementById('single-input').addEventListener('keydown', e => {
  if (e.ctrlKey && e.key === 'Enter') analyzeSingle();
});

function loadSample(type) {
  const ta = document.getElementById('single-input');
  ta.value = SAMPLES[type];
  document.getElementById('char-count').textContent = ta.value.length;
}

async function analyzeSingle() {
  const text = document.getElementById('single-input').value.trim();
  if (!text) { showToast('Please enter some text first.', 'warning'); return; }
  if (text.length > 5000) { showToast('Text too long (max 5000 chars).', 'danger'); return; }

  showLoader(true);
  try {
    const res  = await fetch('/analyze', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text })
    });
    const data = await res.json();
    if (!res.ok) { showToast(data.error || 'Analysis failed.', 'danger'); return; }
    renderResult(data);
  } catch {
    showToast('Server error — make sure Flask app is running.', 'danger');
  } finally { showLoader(false); }
}

function clearSingle() {
  document.getElementById('single-input').value = '';
  document.getElementById('char-count').textContent = '0';
  document.getElementById('single-result').innerHTML = '';
  document.getElementById('single-result').classList.add('d-none');
  document.getElementById('single-placeholder').classList.remove('d-none');
}

function scoreBar(label, val, type) {
  return `<div class="score-row">
    <div class="score-lbl">${label}</div>
    <div class="score-track"><div class="score-fill fill-${type}" data-w="${val}" style="width:0%"></div></div>
    <div class="score-val">${val}%</div>
  </div>`;
}

function renderResult(d) {
  const s   = d.final_sentiment;
  const sub = Math.round(d.textblob.subjectivity * 100);

  document.getElementById('single-placeholder').classList.add('d-none');
  const container = document.getElementById('single-result');
  container.classList.remove('d-none');

  container.innerHTML = `
    <div class="siq-card">
      <div class="result-hero ${s}">
        <div class="result-emoji-big">${EMOJI[s]}</div>
        <div style="flex:1">
          <div class="result-label-big">${s} Sentiment</div>
          <div class="result-sublabel">Ensemble: VADER + TextBlob + ML Model</div>
          <div class="result-owner-tag">
            <i class="bi bi-person-badge-fill me-1"></i>${d.author || 'Sakshi Puri'}
            &nbsp;|&nbsp;
            <i class="bi bi-fingerprint me-1"></i>UID: ${d.uid || '24BET10158'}
          </div>
        </div>
      </div>

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
          <div class="model-tile-label">ML Confidence</div>
          <div class="model-tile-value">${d.ml_model.confidence}%</div>
          <div class="model-tile-sent sent-chip-${sentClass(d.ml_model.label)}">${d.ml_model.label}</div>
        </div>
      </div>

      <div class="score-section">
        <h6>VADER Score Breakdown</h6>
        ${scoreBar('Positive', d.vader.positive, 'pos')}
        ${scoreBar('Negative', d.vader.negative, 'neg')}
        ${scoreBar('Neutral',  d.vader.neutral,  'neu')}
      </div>

      <div class="sub-meter-row">
        <h6>Subjectivity Meter</h6>
        <div class="sub-track"><div class="sub-marker" id="sub-marker" style="left:0%"></div></div>
        <div class="sub-labels"><span>Objective</span><span>${sub}%</span><span>Subjective</span></div>
      </div>

      ${d.keywords.length ? `
      <div class="kw-section">
        <h6>Key Words Detected</h6>
        <div class="kw-chips">${d.keywords.map(k => `<span class="kw-chip">${k.word}</span>`).join('')}</div>
      </div>` : ''}

      <div class="result-footer">
        <div class="d-flex gap-4 flex-wrap">
          <span class="result-footer-stat"><strong>${d.word_count}</strong> words</span>
          <span class="result-footer-stat"><strong>${d.char_count}</strong> characters</span>
          <span class="result-footer-stat">TextBlob polarity: <strong>${d.textblob.polarity}</strong></span>
          <span class="result-footer-stat">Subjectivity: <strong>${sub}%</strong></span>
        </div>
        <div class="result-footer-owner">
          <i class="bi bi-person-badge-fill me-1"></i>Sakshi Puri &nbsp;|&nbsp;
          <i class="bi bi-fingerprint me-1"></i>UID: 24BET10158
        </div>
      </div>
    </div>
  `;

  setTimeout(() => {
    document.querySelectorAll('.score-fill').forEach(b => { b.style.width = b.dataset.w + '%'; });
    const marker = document.getElementById('sub-marker');
    if (marker) marker.style.left = sub + '%';
  }, 60);

  container.scrollIntoView({ behavior: 'smooth', block: 'start' });
}
