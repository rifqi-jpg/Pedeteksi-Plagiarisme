// Copyright (c) 2026 Rifqi Rabbani. All rights reserved.

// Tab switching
document.querySelectorAll('.tab-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    const tab = btn.dataset.tab;
    const panel = tab.startsWith('ref') ? 'ref' : 'test';
    const prefix = panel;

    btn.parentElement.querySelectorAll('.tab-btn').forEach(b => {
      b.classList.remove('active-tab', 'bg-indigo-600/30', 'text-white');
      b.classList.add('text-slate-400', 'hover:text-white');
    });
    btn.classList.add('active-tab', 'bg-indigo-600/30', 'text-white');
    btn.classList.remove('text-slate-400');

    const textPanel = document.getElementById(`${prefix}-text-panel`);
    const filePanel = document.getElementById(`${prefix}-file-panel`);
    if (tab.endsWith('-text')) {
      textPanel.classList.remove('hidden');
      filePanel.classList.add('hidden');
    } else {
      textPanel.classList.add('hidden');
      filePanel.classList.remove('hidden');
    }
  });
});

// Init tab styles
document.querySelectorAll('.active-tab').forEach(btn => {
  btn.classList.add('bg-indigo-600/30', 'text-white');
});

// Drag & drop setup
function setupDropZone(zoneId, inputId, labelId) {
  const zone = document.getElementById(zoneId);
  const input = document.getElementById(inputId);
  const label = document.getElementById(labelId);

  zone.addEventListener('click', () => input.click());

  zone.addEventListener('dragover', e => {
    e.preventDefault();
    zone.classList.add('dragover');
  });
  zone.addEventListener('dragleave', () => zone.classList.remove('dragover'));
  zone.addEventListener('drop', e => {
    e.preventDefault();
    zone.classList.remove('dragover');
    if (e.dataTransfer.files.length) {
      input.files = e.dataTransfer.files;
      showFileName(input, label);
    }
  });

  input.addEventListener('change', () => showFileName(input, label));
}

function showFileName(input, label) {
  if (input.files.length) {
    label.textContent = `✓ ${input.files[0].name}`;
    label.classList.remove('hidden');
  }
}

setupDropZone('refDropZone', 'referenceFile', 'refFileName');
setupDropZone('testDropZone', 'testFile', 'testFileName');

// Form submit
const form = document.getElementById('analyzeForm');
const submitBtn = document.getElementById('submitBtn');
const btnText = document.getElementById('btnText');
const btnSpinner = document.getElementById('btnSpinner');
const errorMsg = document.getElementById('errorMsg');
const resultSection = document.getElementById('resultSection');

form.addEventListener('submit', async e => {
  e.preventDefault();
  errorMsg.classList.add('hidden');
  resultSection.classList.add('hidden');

  btnText.textContent = 'Menganalisis...';
  btnSpinner.classList.remove('hidden');
  submitBtn.disabled = true;

  const formData = new FormData(form);

  try {
    const res = await fetch('/api/analyze', { method: 'POST', body: formData });
    const json = await res.json();

    if (!res.ok) {
      throw new Error(json.detail || 'Gagal menganalisis dokumen.');
    }

    displayResult(json.data);
  } catch (err) {
    errorMsg.textContent = err.message;
    errorMsg.classList.remove('hidden');
  } finally {
    btnText.textContent = 'Mulai Analisis Plagiarisme';
    btnSpinner.classList.add('hidden');
    submitBtn.disabled = false;
  }
});

function displayResult(data) {
  const pct = data.similarity_percentage;
  document.getElementById('scorePercent').textContent = `${pct}%`;
  document.getElementById('resultMessage').textContent = data.message;
  document.getElementById('refLength').textContent = `${data.reference_length.toLocaleString()} karakter`;
  document.getElementById('testLength').textContent = `${data.test_length.toLocaleString()} karakter`;

  const badge = document.getElementById('resultBadge');
  badge.textContent = data.label;

  const colors = {
    high: { badge: 'bg-red-500/20 text-red-300 border border-red-500/30', stroke: '#ef4444' },
    medium: { badge: 'bg-amber-500/20 text-amber-300 border border-amber-500/30', stroke: '#f59e0b' },
    low: { badge: 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30', stroke: '#10b981' },
  };
  const c = colors[data.level] || colors.low;
  badge.className = `inline-block px-4 py-1.5 rounded-full text-sm font-medium mb-3 ${c.badge}`;

  const circle = document.getElementById('gaugeCircle');
  const circumference = 326.73;
  const offset = circumference - (pct / 100) * circumference;
  circle.setAttribute('stroke', c.stroke);
  circle.setAttribute('stroke-dashoffset', offset);

  resultSection.classList.remove('hidden');
  resultSection.scrollIntoView({ behavior: 'smooth', block: 'center' });
}
