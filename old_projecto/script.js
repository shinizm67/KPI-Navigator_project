// script.js

document.addEventListener('DOMContentLoaded', () => {
  // ▼ 日付変数とセレクター
  let currentDate = new Date();
  const yearSelect = document.getElementById('year-select');
  const monthSelect = document.getElementById('month-select');
  const daySelect = document.getElementById('day-select');
  const container = document.getElementById('kpi-body');

  // ▼ 年月日選択肢の初期化
  const currentYear = new Date().getFullYear();
  for (let y = currentYear; y >= currentYear - 10; y--) {
    const option = document.createElement('option');
    option.value = y;
    option.textContent = `${y}年`;
    yearSelect.appendChild(option);
  }

  for (let m = 1; m <= 12; m++) {
    const option = document.createElement('option');
    option.value = m;
    option.textContent = `${m}月`;
    monthSelect.appendChild(option);
  }

  function updateDayOptions(year, month) {
    daySelect.innerHTML = '';
    const lastDay = new Date(year, month, 0).getDate();
    for (let d = 1; d <= lastDay; d++) {
      const option = document.createElement('option');
      option.value = d;
      option.textContent = `${d}日`;
      daySelect.appendChild(option);
    }
  }

  function updateSelectUI() {
    const y = currentDate.getFullYear();
    const m = currentDate.getMonth() + 1;
    const d = currentDate.getDate();
    yearSelect.value = y;
    monthSelect.value = m;
    updateDayOptions(y, m);
    daySelect.value = d;
    scrollToKPIBarByDate(currentDate); // ★ 追加：現在の日付にスクロール
  }

  yearSelect.addEventListener('change', () => {
    currentDate.setFullYear(Number(yearSelect.value));
    updateDayOptions(currentDate.getFullYear(), currentDate.getMonth() + 1);
    updateSelectUI();
  });

  monthSelect.addEventListener('change', () => {
    currentDate.setMonth(Number(monthSelect.value) - 1);
    updateDayOptions(currentDate.getFullYear(), currentDate.getMonth() + 1);
    updateSelectUI();
  });

  daySelect.addEventListener('change', () => {
    currentDate.setDate(Number(daySelect.value));
    updateSelectUI();
  });

  flatpickr("#calendar-input", {
    defaultDate: currentDate,
    onChange: function (selectedDates) {
      currentDate = selectedDates[0];
      updateSelectUI();
    }
  });

  document.querySelector('.calendar-icon').addEventListener('click', () => {
    document.querySelector('#calendar-input')._flatpickr.open();
  });

  // ▼ KPIバー生成ロジック
  function createDailyKPIBar(entry) {
    const bar = document.createElement('div');
    bar.className = 'kpi-bar';

    const date = entry.date;
    const weekday = entry.weekday;
    const target = entry.target_sales || 0;
    const forecast = entry.forecast_sales || 0;
    const gap = entry.gap || 0;
    const action = entry.action || '';

    bar.id = `kpi-${date}`; // ★ 追加：id属性を日付ベースで付与

    bar.innerHTML = `
      <div class="kpi-date">${date} (${weekday})</div>
      <div class="kpi-target">🎯 目標: &yen;${target.toLocaleString()}</div>
      <div class="kpi-forecast">📊 実績: &yen;${forecast.toLocaleString()}</div>
      <div class="kpi-gap">⚠️ 差額: &yen;${gap.toLocaleString()}</div>
      <div class="kpi-action">💡 ${action}</div>
    `;
    return bar;
  }

  // ▼ データ取得＆描画
  fetch('./api/get_daily_kpi.php')
    .then(response => response.json())
    .then(data => {
      container.innerHTML = '';
      data.forEach(entry => {
        const bar = createDailyKPIBar(entry);
        container.appendChild(bar);
      });
    })
    .catch(error => {
      console.error('KPIデータ取得エラー:', error);
    });

  // ▼ 特定日付のKPIバーにスクロールしてハイライト
  function scrollToKPIBarByDate(dateObj) {
    const yyyy = dateObj.getFullYear();
    const mm = String(dateObj.getMonth() + 1).padStart(2, '0');
    const dd = String(dateObj.getDate()).padStart(2, '0');
    const targetId = `kpi-${yyyy}-${mm}-${dd}`;
    const targetElement = document.getElementById(targetId);

    document.querySelectorAll('.kpi-bar.highlight').forEach(el => {
      el.classList.remove('highlight');
    });

    if (targetElement) {
      targetElement.classList.add('highlight');
      targetElement.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
  }

  // 初期表示
  updateSelectUI();
});


