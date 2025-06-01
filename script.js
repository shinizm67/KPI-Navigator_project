/* ==================================================
   JS完全保存版 Part 1
   対象: カレンダーセクション (年月日セレクター・Flatpickr)
   関連HTML: <div class="calendar-and-date">
   更新日: 2025-06-01
================================================== */

// 現在日付初期化
let currentDate = new Date();

// 年月日セレクタ取得
const yearSelect = document.getElementById('year-select');
const monthSelect = document.getElementById('month-select');
const daySelect = document.getElementById('day-select');

// ▼ 年初期化：過去10年分の選択肢生成
const currentYear = new Date().getFullYear();
for (let y = currentYear; y >= currentYear - 10; y--) {
  const option = document.createElement('option');
  option.value = y;
  option.textContent = `${y}年`;
  yearSelect.appendChild(option);
}

// ▼ 月初期化：1月〜12月
for (let m = 1; m <= 12; m++) {
  const option = document.createElement('option');
  option.value = m;
  option.textContent = `${m}月`;
  monthSelect.appendChild(option);
}

// ▼ 日の選択肢更新（年・月に応じて）
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

// ▼ 選択肢に currentDate を反映
function updateSelectUI() {
  const y = currentDate.getFullYear();
  const m = currentDate.getMonth() + 1;
  const d = currentDate.getDate();

  yearSelect.value = y;
  monthSelect.value = m;
  updateDayOptions(y, m);
  daySelect.value = d;
}

// ▼ ▲▼ボタン操作で日付変更
function changeDate(type, delta) {
  if (type === 'year') {
    currentDate.setFullYear(currentDate.getFullYear() + delta);
  } else if (type === 'month') {
    currentDate.setMonth(currentDate.getMonth() + delta);
  } else if (type === 'day') {
    currentDate.setDate(currentDate.getDate() + delta);
  }
  updateSelectUI();
}

// ▼ 年月日セレクター変更時の更新処理
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

// ▼ 今日ボタン
function goToToday() {
  currentDate = new Date();
  updateSelectUI();
}

// ▼ 初期化 (ページロード時)
document.addEventListener('DOMContentLoaded', () => {
  updateSelectUI();

  flatpickr("#calendar-input", {
    defaultDate: currentDate,
    onChange: function(selectedDates) {
      currentDate = selectedDates[0];
      updateSelectUI();
    }
  });

  document.querySelector('.calendar-icon').addEventListener('click', () => {
    document.querySelector('#calendar-input')._flatpickr.open();
  });
});
