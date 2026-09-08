const fallbackTrends = [
  {name: 'Oversized blazers', source: 'Silhouette · 2,841 signals', value: '+142%', width: 92},
  {name: 'Washed denim', source: 'Texture · 1,906 signals', value: '+86%', width: 71},
  {name: 'Butter yellow', source: 'Color · 1,284 signals', value: '+64%', width: 56},
  {name: 'Utility pockets', source: 'Detail · 948 signals', value: '+41%', width: 40}
];

let trends = fallbackTrends;
const trendList = document.querySelector('#trendList');
function renderTrends(items = trends) {
  trendList.innerHTML = items.map((trend, index) => `
    <div class="trend-row">
      <span class="rank">0${index + 1}</span>
      <div><span class="trend-name">${trend.name}</span><span class="trend-source">${trend.source}</span></div>
      <div class="trend-bar"><div class="trend-fill" style="width:${trend.width}%"></div></div>
      <span class="trend-value"><b>↗</b> ${trend.value}</span>
    </div>`).join('');
}

renderTrends();

async function loadOverview() {
  try {
    const response = await fetch('/api/overview');
    if (!response.ok) throw new Error(`API returned ${response.status}`);
    const overview = await response.json();
    trends = overview.signals.map((signal) => ({
      name: signal.name,
      source: `${signal.category} · ${signal.count.toLocaleString()} signals`,
      value: `+${signal.velocity}%`,
      width: signal.width,
    }));
    renderTrends();
    document.querySelector('.metric-card strong').textContent = `+${overview.metrics.trend_velocity}%`;
    document.querySelectorAll('.metric-card strong')[2].innerHTML = `${overview.metrics.prediction_confidence}<span class="percent">%</span>`;
    document.querySelector('.confidence-badge').textContent = `${overview.metrics.prediction_confidence}% confidence`;
    document.querySelector('.forecast-hero h3').innerHTML = overview.forecast.name.replace(' ', '<br>');
    document.querySelector('.forecast-date b').textContent = overview.forecast.peak_date;
    document.querySelector('.forecast-foot b').textContent = overview.forecast.region;
  } catch (error) {
    console.info('Using static preview data:', error.message);
  }
}

loadOverview();
document.querySelector('#showAll').addEventListener('click', (event) => {
  event.currentTarget.textContent = event.currentTarget.textContent.includes('all') ? 'Showing top signals  ↑' : 'View all 12 signals  →';
  renderTrends(event.currentTarget.textContent.includes('Showing') ? [...trends, {name: 'Sheer layering', source: 'Construction · 721 signals', value: '+29%', width: 31}] : trends);
});

document.querySelector('#exportBtn').addEventListener('click', (event) => {
  event.currentTarget.textContent = '✓ Brief ready';
  event.currentTarget.style.background = '#79ae69';
  window.setTimeout(() => { event.currentTarget.textContent = '↥ Export brief'; event.currentTarget.style.background = ''; }, 2200);
});