/**
 * Profile location catalogs (Country / State / City).
 * Display is locale-specific; known countries save as canonical ISO codes.
 * Free text is always allowed. Structured so a Geo API can replace catalogs later.
 */
(function (global) {
  'use strict';

  /* KPI-PROFILE-LOCATION-DATALIST */

  var COUNTRY_CODES = ['JP', 'US', 'GB', 'DE', 'FR', 'TW', 'KR', 'CN', 'AU', 'CA', 'SG'];

  var COUNTRY_LABELS = {
    ja: {
      JP: '日本',
      US: 'アメリカ合衆国',
      GB: 'イギリス',
      DE: 'ドイツ',
      FR: 'フランス',
      TW: '台湾',
      KR: '韓国',
      CN: '中国',
      AU: 'オーストラリア',
      CA: 'カナダ',
      SG: 'シンガポール'
    },
    en: {
      JP: 'Japan',
      US: 'United States',
      GB: 'United Kingdom',
      DE: 'Germany',
      FR: 'France',
      TW: 'Taiwan',
      KR: 'South Korea',
      CN: 'China',
      AU: 'Australia',
      CA: 'Canada',
      SG: 'Singapore'
    },
    'zh-tw': {
      JP: '日本',
      US: '美國',
      GB: '英國',
      DE: '德國',
      FR: '法國',
      TW: '台灣',
      KR: '韓國',
      CN: '中國',
      AU: '澳洲',
      CA: '加拿大',
      SG: '新加坡'
    }
  };

  var COUNTRY_ALIASES = {
    jp: 'JP',
    japan: 'JP',
    '日本': 'JP',
    '日本国': 'JP',
    us: 'US',
    usa: 'US',
    america: 'US',
    'united states': 'US',
    'united states of america': 'US',
    'アメリカ': 'US',
    'アメリカ合衆国': 'US',
    gb: 'GB',
    uk: 'GB',
    britain: 'GB',
    'united kingdom': 'GB',
    'great britain': 'GB',
    'イギリス': 'GB',
    '英国': 'GB',
    '英國': 'GB',
    de: 'DE',
    germany: 'DE',
    'ドイツ': 'DE',
    'ドイツ連邦共和国': 'DE',
    '德國': 'DE',
    fr: 'FR',
    france: 'FR',
    'フランス': 'FR',
    '法國': 'FR',
    tw: 'TW',
    taiwan: 'TW',
    '台湾': 'TW',
    '台灣': 'TW',
    '臺灣': 'TW',
    kr: 'KR',
    korea: 'KR',
    'south korea': 'KR',
    '韓国': 'KR',
    '韓國': 'KR',
    '韩国': 'KR',
    cn: 'CN',
    china: 'CN',
    '中国': 'CN',
    '中國': 'CN',
    au: 'AU',
    australia: 'AU',
    'オーストラリア': 'AU',
    '澳洲': 'AU',
    ca: 'CA',
    canada: 'CA',
    'カナダ': 'CA',
    '加拿大': 'CA',
    sg: 'SG',
    singapore: 'SG',
    'シンガポール': 'SG',
    '新加坡': 'SG'
  };

  var JP_PREFECTURES = [
    { id: 'hokkaido', ja: '北海道', en: 'Hokkaido', zh: '北海道' },
    { id: 'aomori', ja: '青森県', en: 'Aomori', zh: '青森縣' },
    { id: 'iwate', ja: '岩手県', en: 'Iwate', zh: '岩手縣' },
    { id: 'miyagi', ja: '宮城県', en: 'Miyagi', zh: '宮城縣' },
    { id: 'akita', ja: '秋田県', en: 'Akita', zh: '秋田縣' },
    { id: 'yamagata', ja: '山形県', en: 'Yamagata', zh: '山形縣' },
    { id: 'fukushima', ja: '福島県', en: 'Fukushima', zh: '福島縣' },
    { id: 'ibaraki', ja: '茨城県', en: 'Ibaraki', zh: '茨城縣' },
    { id: 'tochigi', ja: '栃木県', en: 'Tochigi', zh: '栃木縣' },
    { id: 'gunma', ja: '群馬県', en: 'Gunma', zh: '群馬縣' },
    { id: 'saitama', ja: '埼玉県', en: 'Saitama', zh: '埼玉縣' },
    { id: 'chiba', ja: '千葉県', en: 'Chiba', zh: '千葉縣' },
    { id: 'tokyo', ja: '東京都', en: 'Tokyo', zh: '東京都' },
    { id: 'kanagawa', ja: '神奈川県', en: 'Kanagawa', zh: '神奈川縣' },
    { id: 'niigata', ja: '新潟県', en: 'Niigata', zh: '新潟縣' },
    { id: 'toyama', ja: '富山県', en: 'Toyama', zh: '富山縣' },
    { id: 'ishikawa', ja: '石川県', en: 'Ishikawa', zh: '石川縣' },
    { id: 'fukui', ja: '福井県', en: 'Fukui', zh: '福井縣' },
    { id: 'yamanashi', ja: '山梨県', en: 'Yamanashi', zh: '山梨縣' },
    { id: 'nagano', ja: '長野県', en: 'Nagano', zh: '長野縣' },
    { id: 'gifu', ja: '岐阜県', en: 'Gifu', zh: '岐阜縣' },
    { id: 'shizuoka', ja: '静岡県', en: 'Shizuoka', zh: '靜岡縣' },
    { id: 'aichi', ja: '愛知県', en: 'Aichi', zh: '愛知縣' },
    { id: 'mie', ja: '三重県', en: 'Mie', zh: '三重縣' },
    { id: 'shiga', ja: '滋賀県', en: 'Shiga', zh: '滋賀縣' },
    { id: 'kyoto', ja: '京都府', en: 'Kyoto', zh: '京都府' },
    { id: 'osaka', ja: '大阪府', en: 'Osaka', zh: '大阪府' },
    { id: 'hyogo', ja: '兵庫県', en: 'Hyogo', zh: '兵庫縣' },
    { id: 'nara', ja: '奈良県', en: 'Nara', zh: '奈良縣' },
    { id: 'wakayama', ja: '和歌山県', en: 'Wakayama', zh: '和歌山縣' },
    { id: 'tottori', ja: '鳥取県', en: 'Tottori', zh: '鳥取縣' },
    { id: 'shimane', ja: '島根県', en: 'Shimane', zh: '島根縣' },
    { id: 'okayama', ja: '岡山県', en: 'Okayama', zh: '岡山縣' },
    { id: 'hiroshima', ja: '広島県', en: 'Hiroshima', zh: '廣島縣' },
    { id: 'yamaguchi', ja: '山口県', en: 'Yamaguchi', zh: '山口縣' },
    { id: 'tokushima', ja: '徳島県', en: 'Tokushima', zh: '德島縣' },
    { id: 'kagawa', ja: '香川県', en: 'Kagawa', zh: '香川縣' },
    { id: 'ehime', ja: '愛媛県', en: 'Ehime', zh: '愛媛縣' },
    { id: 'kochi', ja: '高知県', en: 'Kochi', zh: '高知縣' },
    { id: 'fukuoka', ja: '福岡県', en: 'Fukuoka', zh: '福岡縣' },
    { id: 'saga', ja: '佐賀県', en: 'Saga', zh: '佐賀縣' },
    { id: 'nagasaki', ja: '長崎県', en: 'Nagasaki', zh: '長崎縣' },
    { id: 'kumamoto', ja: '熊本県', en: 'Kumamoto', zh: '熊本縣' },
    { id: 'oita', ja: '大分県', en: 'Oita', zh: '大分縣' },
    { id: 'miyazaki', ja: '宮崎県', en: 'Miyazaki', zh: '宮崎縣' },
    { id: 'kagoshima', ja: '鹿児島県', en: 'Kagoshima', zh: '鹿兒島縣' },
    { id: 'okinawa', ja: '沖縄県', en: 'Okinawa', zh: '沖繩縣' }
  ];

  var OTHER_STATES = {
    US: [
      { id: 'ca', ja: 'カリフォルニア州', en: 'California', zh: '加利福尼亞州' },
      { id: 'ny', ja: 'ニューヨーク州', en: 'New York', zh: '紐約州' },
      { id: 'tx', ja: 'テキサス州', en: 'Texas', zh: '德克薩斯州' },
      { id: 'wa', ja: 'ワシントン州', en: 'Washington', zh: '華盛頓州' },
      { id: 'fl', ja: 'フロリダ州', en: 'Florida', zh: '佛羅里達州' },
      { id: 'il', ja: 'イリノイ州', en: 'Illinois', zh: '伊利諾州' },
      { id: 'hi', ja: 'ハワイ州', en: 'Hawaii', zh: '夏威夷州' },
      { id: 'ma', ja: 'マサチューセッツ州', en: 'Massachusetts', zh: '麻薩諸塞州' },
      { id: 'nv', ja: 'ネバダ州', en: 'Nevada', zh: '內華達州' },
      { id: 'pa', ja: 'ペンシルベニア州', en: 'Pennsylvania', zh: '賓夕法尼亞州' }
    ],
    GB: [
      { id: 'england', ja: 'イングランド', en: 'England', zh: '英格蘭' },
      { id: 'scotland', ja: 'スコットランド', en: 'Scotland', zh: '蘇格蘭' },
      { id: 'wales', ja: 'ウェールズ', en: 'Wales', zh: '威爾斯' },
      { id: 'ni', ja: '北アイルランド', en: 'Northern Ireland', zh: '北愛爾蘭' }
    ],
    DE: [
      { id: 'by', ja: 'バイエルン州', en: 'Bavaria', zh: '巴伐利亞邦' },
      { id: 'nw', ja: 'ノルトライン＝ヴェストファーレン州', en: 'North Rhine-Westphalia', zh: '北萊茵－西發利亞邦' },
      { id: 'be', ja: 'ベルリン', en: 'Berlin', zh: '柏林' }
    ],
    FR: [
      { id: 'idf', ja: 'イル＝ド＝フランス', en: 'Île-de-France', zh: '法蘭西島' },
      { id: 'paca', ja: 'プロヴァンス＝アルプ＝コートダジュール', en: "Provence-Alpes-Côte d'Azur", zh: '普羅旺斯－阿爾卑斯－藍色海岸' }
    ],
    TW: [
      { id: 'taipei', ja: '台北市', en: 'Taipei', zh: '臺北市' },
      { id: 'new_taipei', ja: '新北市', en: 'New Taipei', zh: '新北市' },
      { id: 'taoyuan', ja: '桃園市', en: 'Taoyuan', zh: '桃園市' },
      { id: 'taichung', ja: '台中市', en: 'Taichung', zh: '臺中市' },
      { id: 'tainan', ja: '台南市', en: 'Tainan', zh: '臺南市' },
      { id: 'kaohsiung', ja: '高雄市', en: 'Kaohsiung', zh: '高雄市' }
    ],
    KR: [
      { id: 'seoul', ja: 'ソウル特別市', en: 'Seoul', zh: '首爾特別市' },
      { id: 'busan', ja: '釜山広域市', en: 'Busan', zh: '釜山廣域市' }
    ],
    AU: [
      { id: 'au_nsw', ja: 'ニューサウスウェールズ州', en: 'New South Wales', zh: '新南威爾斯州' },
      { id: 'au_vic', ja: 'ビクトリア州', en: 'Victoria', zh: '維多利亞州' },
      { id: 'au_qld', ja: 'クイーンズランド州', en: 'Queensland', zh: '昆士蘭州' },
      { id: 'au_wa', ja: '西オーストラリア州', en: 'Western Australia', zh: '西澳州' }
    ],
    CA: [
      { id: 'on', ja: 'オンタリオ州', en: 'Ontario', zh: '安大略省' },
      { id: 'qc', ja: 'ケベック州', en: 'Quebec', zh: '魁北克省' },
      { id: 'bc', ja: 'ブリティッシュコロンビア州', en: 'British Columbia', zh: '卑詩省' }
    ]
  };

  var CITIES = {
    tokyo: [
      { id: 'tokyo_city', ja: '東京', en: 'Tokyo', zh: '東京' },
      { id: 'hachioji', ja: '八王子市', en: 'Hachioji', zh: '八王子市' }
    ],
    kanagawa: [
      { id: 'yokohama', ja: '横浜市', en: 'Yokohama', zh: '橫濱市' },
      { id: 'kawasaki', ja: '川崎市', en: 'Kawasaki', zh: '川崎市' },
      { id: 'sagamihara', ja: '相模原市', en: 'Sagamihara', zh: '相模原市' },
      { id: 'fujisawa', ja: '藤沢市', en: 'Fujisawa', zh: '藤澤市' },
      { id: 'kamakura', ja: '鎌倉市', en: 'Kamakura', zh: '鎌倉市' }
    ],
    osaka: [
      { id: 'osaka_city', ja: '大阪市', en: 'Osaka', zh: '大阪市' },
      { id: 'sakai', ja: '堺市', en: 'Sakai', zh: '堺市' }
    ],
    hyogo: [
      { id: 'kobe', ja: '神戸市', en: 'Kobe', zh: '神戶市' }
    ],
    kyoto: [
      { id: 'kyoto_city', ja: '京都市', en: 'Kyoto', zh: '京都市' }
    ],
    fukuoka: [
      { id: 'fukuoka_city', ja: '福岡市', en: 'Fukuoka', zh: '福岡市' }
    ],
    hokkaido: [
      { id: 'sapporo', ja: '札幌市', en: 'Sapporo', zh: '札幌市' }
    ],
    aichi: [
      { id: 'nagoya', ja: '名古屋市', en: 'Nagoya', zh: '名古屋市' }
    ],
    ca: [
      { id: 'los_angeles', ja: 'ロサンゼルス', en: 'Los Angeles', zh: '洛杉磯' },
      { id: 'san_francisco', ja: 'サンフランシスコ', en: 'San Francisco', zh: '舊金山' }
    ],
    ny: [
      { id: 'new_york', ja: 'ニューヨーク市', en: 'New York City', zh: '紐約市' },
      { id: 'buffalo', ja: 'バッファロー', en: 'Buffalo', zh: '水牛城' }
    ],
    tx: [
      { id: 'houston', ja: 'ヒューストン', en: 'Houston', zh: '休士頓' },
      { id: 'dallas', ja: 'ダラス', en: 'Dallas', zh: '達拉斯' }
    ],
    wa: [
      { id: 'seattle', ja: 'シアトル', en: 'Seattle', zh: '西雅圖' }
    ],
    england: [
      { id: 'london', ja: 'ロンドン', en: 'London', zh: '倫敦' },
      { id: 'manchester', ja: 'マンチェスター', en: 'Manchester', zh: '曼徹斯特' }
    ],
    scotland: [
      { id: 'edinburgh', ja: 'エディンバラ', en: 'Edinburgh', zh: '愛丁堡' },
      { id: 'glasgow', ja: 'グラスゴー', en: 'Glasgow', zh: '格拉斯哥' }
    ],
    wales: [
      { id: 'cardiff', ja: 'カーディフ', en: 'Cardiff', zh: '卡迪夫' }
    ],
    by: [
      { id: 'munich', ja: 'ミュンヘン', en: 'Munich', zh: '慕尼黑' }
    ],
    nw: [
      { id: 'cologne', ja: 'ケルン', en: 'Cologne', zh: '科隆' },
      { id: 'dusseldorf', ja: 'デュッセルドルフ', en: 'Düsseldorf', zh: '杜塞道夫' }
    ],
    idf: [
      { id: 'paris', ja: 'パリ', en: 'Paris', zh: '巴黎' }
    ],
    paca: [
      { id: 'marseille', ja: 'マルセイユ', en: 'Marseille', zh: '馬賽' },
      { id: 'nice', ja: 'ニース', en: 'Nice', zh: '尼斯' }
    ],
    taipei: [
      { id: 'taipei_city', ja: '台北', en: 'Taipei', zh: '臺北' }
    ]
  };

  var TZ_TOKYO = 'Asia/Tokyo (JST, UTC+9)';
  var TIMEZONE_BY_STATE = {
    ca: 'America/Los_Angeles (PST/PDT, UTC-8/-7)',
    wa: 'America/Los_Angeles (PST/PDT, UTC-8/-7)',
    ny: 'America/New_York (EST/EDT, UTC-5/-4)',
    fl: 'America/New_York (EST/EDT, UTC-5/-4)',
    ma: 'America/New_York (EST/EDT, UTC-5/-4)',
    pa: 'America/New_York (EST/EDT, UTC-5/-4)',
    tx: 'America/Chicago (CST/CDT, UTC-6/-5)',
    il: 'America/Chicago (CST/CDT, UTC-6/-5)',
    hi: 'Pacific/Honolulu (HST, UTC-10)',
    nv: 'America/Los_Angeles (PST/PDT, UTC-8/-7)',
    england: 'Europe/London (GMT/BST, UTC+0/+1)',
    scotland: 'Europe/London (GMT/BST, UTC+0/+1)',
    wales: 'Europe/London (GMT/BST, UTC+0/+1)',
    ni: 'Europe/London (GMT/BST, UTC+0/+1)',
    by: 'Europe/Berlin (CET/CEST, UTC+1/+2)',
    nw: 'Europe/Berlin (CET/CEST, UTC+1/+2)',
    be: 'Europe/Berlin (CET/CEST, UTC+1/+2)',
    idf: 'Europe/Paris (CET/CEST, UTC+1/+2)',
    paca: 'Europe/Paris (CET/CEST, UTC+1/+2)',
    taipei: 'Asia/Taipei (CST, UTC+8)',
    new_taipei: 'Asia/Taipei (CST, UTC+8)',
    taoyuan: 'Asia/Taipei (CST, UTC+8)',
    taichung: 'Asia/Taipei (CST, UTC+8)',
    tainan: 'Asia/Taipei (CST, UTC+8)',
    kaohsiung: 'Asia/Taipei (CST, UTC+8)',
    seoul: 'Asia/Seoul (KST, UTC+9)',
    busan: 'Asia/Seoul (KST, UTC+9)',
    au_nsw: 'Australia/Sydney (AEST/AEDT, UTC+10/+11)',
    au_vic: 'Australia/Sydney (AEST/AEDT, UTC+10/+11)',
    au_qld: 'Australia/Brisbane (AEST, UTC+10)',
    au_wa: 'Australia/Perth (AWST, UTC+8)',
    on: 'America/Toronto (EST/EDT, UTC-5/-4)',
    qc: 'America/Toronto (EST/EDT, UTC-5/-4)',
    bc: 'America/Vancouver (PST/PDT, UTC-8/-7)'
  };

  var PROMPT_EXACT = {
    '先に業種を選択してください': 1,
    '請先選擇業態': 1,
    '国を選択するか、自由に入力してください': 1,
    '都道府県を選択するか、自由に入力してください': 1,
    '市区町村を選択するか、自由に入力してください': 1,
    'Choose a country or enter your own': 1,
    'Choose a state / prefecture or enter your own': 1,
    'Choose a city / town or enter your own': 1,
    '請選擇國家，或自行輸入': 1,
    '請選擇縣市／州，或自行輸入': 1,
    '請選擇城市／地區，或自行輸入': 1
  };

  function localeOf(locale) {
    var s = String(locale || '').toLowerCase();
    if (s.indexOf('ja') === 0) return 'ja';
    if (s.indexOf('zh') === 0) return 'zh-tw';
    return 'en';
  }

  function localeFromDocument() {
    var lang = '';
    try {
      lang = (global.document && document.documentElement && document.documentElement.lang) || '';
    } catch (_e) {}
    return localeOf(lang);
  }

  function labelOf(rec, locale) {
    var loc = localeOf(locale);
    if (loc === 'ja') return rec.ja;
    if (loc === 'zh-tw') return rec.zh;
    return rec.en;
  }

  function fold(v) {
    return String(v == null ? '' : v).trim().toLowerCase().replace(/\s+/g, ' ');
  }

  function isPrompt(v) {
    var s = String(v == null ? '' : v).trim();
    if (!s) return true;
    if (PROMPT_EXACT[s]) return true;
    var n = s.replace(/^[—–-]\s*|\s*[—–-]$/g, '').trim().toLowerCase();
    return (
      n === 'select' ||
      n === 'select country first' ||
      n === 'select state first' ||
      n === 'select industry first' ||
      n === 'select a business type first' ||
      n === 'please select' ||
      n === '請選擇' ||
      n === '請先選擇國家' ||
      n === '請先選擇縣市 / 州' ||
      n === '請先選擇縣市／州'
    );
  }

  function toCanonicalCountry(raw) {
    if (isPrompt(raw)) return '';
    var s = String(raw || '').trim();
    if (!s) return '';
    var upper = s.toUpperCase();
    if (COUNTRY_LABELS.en[upper] || COUNTRY_LABELS.ja[upper]) return upper === 'UK' ? 'GB' : upper;
    var aliased = COUNTRY_ALIASES[fold(s)];
    if (aliased) return aliased;
    var locKeys = ['ja', 'en', 'zh-tw'];
    for (var i = 0; i < locKeys.length; i++) {
      var map = COUNTRY_LABELS[locKeys[i]];
      for (var code in map) {
        if (Object.prototype.hasOwnProperty.call(map, code) && map[code] === s) return code;
      }
    }
    return '';
  }

  function saveCountry(raw) {
    if (isPrompt(raw)) return '';
    var s = String(raw || '').trim();
    if (!s) return '';
    return toCanonicalCountry(s) || s;
  }

  function displayCountry(raw, locale) {
    if (isPrompt(raw)) return '';
    var s = String(raw || '').trim();
    if (!s) return '';
    var code = toCanonicalCountry(s);
    if (!code) return s;
    var map = COUNTRY_LABELS[localeOf(locale)] || COUNTRY_LABELS.en;
    return map[code] || s;
  }

  function countryLabels(locale) {
    var map = COUNTRY_LABELS[localeOf(locale)] || COUNTRY_LABELS.en;
    return COUNTRY_CODES.map(function (code) {
      return map[code];
    });
  }

  function allStates() {
    var out = JP_PREFECTURES.slice();
    Object.keys(OTHER_STATES).forEach(function (code) {
      out = out.concat(OTHER_STATES[code]);
    });
    return out;
  }

  function recMatch(rec, raw) {
    var f = fold(raw);
    if (!f) return false;
    if (fold(rec.id) === f) return true;
    if (fold(rec.ja) === f || fold(rec.en) === f || fold(rec.zh) === f) return true;
    if (rec.id === 'tokyo' && (f === '東京' || f === 'tokyo')) return true;
    if (rec.id === 'osaka' && (f === '大阪' || f === 'osaka')) return true;
    if (rec.id === 'kyoto' && (f === '京都' || f === 'kyoto')) return true;
    if (rec.id === 'fukuoka' && (f === '福岡' || f === 'fukuoka')) return true;
    return false;
  }

  function findState(raw) {
    if (isPrompt(raw)) return null;
    var s = String(raw || '').trim();
    if (!s) return null;
    var all = allStates();
    for (var i = 0; i < all.length; i++) {
      if (recMatch(all[i], s)) return all[i];
    }
    return null;
  }

  function statesForCountry(countryRaw, locale) {
    var code = toCanonicalCountry(countryRaw);
    var loc = localeOf(locale);
    if (code === 'JP') {
      return JP_PREFECTURES.map(function (rec) {
        return labelOf(rec, loc);
      });
    }
    var list = OTHER_STATES[code] || [];
    return list.map(function (rec) {
      return labelOf(rec, loc);
    });
  }

  function displayState(raw, locale) {
    if (isPrompt(raw)) return '';
    var s = String(raw || '').trim();
    if (!s) return '';
    var rec = findState(s);
    return rec ? labelOf(rec, locale) : s;
  }

  function allCities() {
    var out = [];
    Object.keys(CITIES).forEach(function (key) {
      out = out.concat(CITIES[key]);
    });
    return out;
  }

  function findCity(raw) {
    if (isPrompt(raw)) return null;
    var s = String(raw || '').trim();
    if (!s) return null;
    var all = allCities();
    for (var i = 0; i < all.length; i++) {
      if (recMatch(all[i], s)) return all[i];
    }
    return null;
  }

  function citiesForState(stateRaw, locale) {
    var rec = findState(stateRaw);
    var loc = localeOf(locale);
    if (!rec || !CITIES[rec.id]) return [];
    return CITIES[rec.id].map(function (city) {
      return labelOf(city, loc);
    });
  }

  function displayCity(raw, locale) {
    if (isPrompt(raw)) return '';
    var s = String(raw || '').trim();
    if (!s) return '';
    var rec = findCity(s);
    return rec ? labelOf(rec, locale) : s;
  }

  function timezoneFor(stateRaw) {
    var rec = findState(stateRaw);
    if (!rec) return '';
    if (TIMEZONE_BY_STATE[rec.id]) return TIMEZONE_BY_STATE[rec.id];
    for (var i = 0; i < JP_PREFECTURES.length; i++) {
      if (JP_PREFECTURES[i].id === rec.id) return TZ_TOKYO;
    }
    return '';
  }

  function saveText(raw) {
    if (isPrompt(raw)) return '';
    return String(raw || '').trim();
  }

  function fillDatalist(idOrEl, labels) {
    var list = typeof idOrEl === 'string'
      ? (global.document ? document.getElementById(idOrEl) : null)
      : idOrEl;
    if (!list) return;
    list.innerHTML = '';
    (labels || []).forEach(function (label) {
      var opt = document.createElement('option');
      opt.value = label;
      list.appendChild(opt);
    });
  }

  global.KpiProfileLocation = {
    COUNTRY_CODES: COUNTRY_CODES,
    JP_PREFECTURES: JP_PREFECTURES,
    localeFromDocument: localeFromDocument,
    localeOf: localeOf,
    isPrompt: isPrompt,
    toCanonicalCountry: toCanonicalCountry,
    saveCountry: saveCountry,
    saveText: saveText,
    displayCountry: displayCountry,
    displayState: displayState,
    displayCity: displayCity,
    countryLabels: countryLabels,
    stateLabels: statesForCountry,
    cityLabels: citiesForState,
    timezoneFor: timezoneFor,
    fillDatalist: fillDatalist,
    findState: findState,
    findCity: findCity
  };
})(typeof window !== 'undefined' ? window : this);
