const BASE = '.';

const statusEl = document.getElementById('status');
const metaEl = document.getElementById('meta');
const container = document.getElementById('projects-container');
const selector = document.getElementById('date-selector');

function setStatus(msg) {
  statusEl.textContent = msg;
  statusEl.style.display = 'block';
}

function clearStatus() {
  statusEl.style.display = 'none';
}

function renderProjects(data) {
  container.innerHTML = '';
  metaEl.innerHTML = '';

  if (!data || !data.projects || data.projects.length === 0) {
    container.innerHTML = '<div class="no-data">今日暫無 AI 相關專案資料</div>';
    return;
  }

  metaEl.textContent = `${data.date}  ·  共 ${data.total_count} 個 AI 相關專案  ·  更新於 ${formatTime(data.generated_at)}`;

  data.projects.forEach((p, i) => {
    const card = document.createElement('div');
    card.className = 'project-card';

    const langBadge = p.language
      ? `<span class="badge-lang">${escape(p.language)}</span>`
      : '';

    const starsBadge = p.stars_today
      ? `<span class="badge-stars">⭐ +${p.stars_today.toLocaleString()}</span>`
      : '';

    const summary = p.summary_zh
      ? `<p class="project-summary">${escape(p.summary_zh)}</p>`
      : '';

    const desc = p.description && !p.summary_zh
      ? `<p class="project-desc">${escape(p.description)}</p>`
      : '';

    card.innerHTML = `
      <div class="card-header">
        <div class="project-name">
          <span style="color:var(--muted);margin-right:6px">#${i + 1}</span>
          <a href="${p.url}" target="_blank" rel="noopener">${escape(p.name)}</a>
        </div>
        <div class="card-badges">${langBadge}${starsBadge}</div>
      </div>
      ${summary}${desc}
    `;
    container.appendChild(card);
  });
}

function escape(str) {
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

function formatTime(iso) {
  if (!iso) return '';
  try {
    return new Date(iso).toLocaleString('zh-TW', { timeZone: 'Asia/Taipei' });
  } catch {
    return iso;
  }
}

function loadNews(url) {
  setStatus('載入中...');
  container.innerHTML = '';
  metaEl.innerHTML = '';

  fetch(url)
    .then(r => {
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      return r.json();
    })
    .then(data => {
      clearStatus();
      renderProjects(data);
    })
    .catch(err => {
      setStatus(`載入失敗：${err.message}`);
    });
}

// 載入歷史日期清單
fetch(`${BASE}/data/index.json`)
  .then(r => r.json())
  .then(idx => {
    const dates = idx.dates || [];
    selector.innerHTML = '<option value="">今日最新</option>';
    dates.forEach(date => {
      const opt = document.createElement('option');
      opt.value = date;
      opt.textContent = date;
      selector.appendChild(opt);
    });
  })
  .catch(() => {
    // index.json 不存在時靜默忽略
  });

// 預設載入當日資料
loadNews(`${BASE}/data/news.json`);

// 切換日期
selector.addEventListener('change', e => {
  const date = e.target.value;
  if (!date) {
    loadNews(`${BASE}/data/news.json`);
  } else {
    loadNews(`${BASE}/data/archive/${date}.json`);
  }
});
