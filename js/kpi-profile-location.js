/**
 * Profile location catalogs (Country / State / City).
 * Display is locale-specific; known countries save as canonical ISO codes.
 * Free text is always allowed. Structured so a Geo API can replace catalogs later.
 */
(function (global) {
  'use strict';

  /* KPI-PROFILE-LOCATION-DATALIST */

  var COUNTRY_CODES = [
    'JP', 'US', 'GB', 'CA', 'AU', 'NZ', 'IE', 'SG', 'TW', 'HK', 'KR', 'CN',
    'DE', 'FR', 'IT', 'ES', 'NL', 'BE', 'CH', 'AT', 'SE', 'NO', 'DK', 'FI', 'PT',
    'AE', 'IN', 'ZA'
  ];

  var COUNTRY_LABELS = {
    ja: {
      JP: '日本', US: 'アメリカ合衆国', GB: 'イギリス', CA: 'カナダ', AU: 'オーストラリア',
      NZ: 'ニュージーランド', IE: 'アイルランド', SG: 'シンガポール', TW: '台湾', HK: '香港',
      KR: '韓国', CN: '中国', DE: 'ドイツ', FR: 'フランス', IT: 'イタリア', ES: 'スペイン',
      NL: 'オランダ', BE: 'ベルギー', CH: 'スイス', AT: 'オーストリア', SE: 'スウェーデン',
      NO: 'ノルウェー', DK: 'デンマーク', FI: 'フィンランド', PT: 'ポルトガル',
      AE: 'アラブ首長国連邦', IN: 'インド', ZA: '南アフリカ'
    },
    en: {
      JP: 'Japan', US: 'United States', GB: 'United Kingdom', CA: 'Canada', AU: 'Australia',
      NZ: 'New Zealand', IE: 'Ireland', SG: 'Singapore', TW: 'Taiwan', HK: 'Hong Kong',
      KR: 'South Korea', CN: 'China', DE: 'Germany', FR: 'France', IT: 'Italy', ES: 'Spain',
      NL: 'Netherlands', BE: 'Belgium', CH: 'Switzerland', AT: 'Austria', SE: 'Sweden',
      NO: 'Norway', DK: 'Denmark', FI: 'Finland', PT: 'Portugal',
      AE: 'United Arab Emirates', IN: 'India', ZA: 'South Africa'
    },
    'zh-tw': {
      JP: '日本', US: '美國', GB: '英國', CA: '加拿大', AU: '澳洲',
      NZ: '紐西蘭', IE: '愛爾蘭', SG: '新加坡', TW: '台灣', HK: '香港',
      KR: '韓國', CN: '中國', DE: '德國', FR: '法國', IT: '義大利', ES: '西班牙',
      NL: '荷蘭', BE: '比利時', CH: '瑞士', AT: '奧地利', SE: '瑞典',
      NO: '挪威', DK: '丹麥', FI: '芬蘭', PT: '葡萄牙',
      AE: '阿拉伯聯合大公國', IN: '印度', ZA: '南非'
    }
  };

  var COUNTRY_ALIASES = {
    jp: 'JP', japan: 'JP', '日本': 'JP', '日本国': 'JP',
    us: 'US', usa: 'US', america: 'US', 'united states': 'US', 'united states of america': 'US',
    'アメリカ': 'US', 'アメリカ合衆国': 'US', '美國': 'US',
    gb: 'GB', uk: 'GB', britain: 'GB', 'united kingdom': 'GB', 'great britain': 'GB',
    'イギリス': 'GB', '英国': 'GB', '英國': 'GB',
    ca: 'CA', canada: 'CA', 'カナダ': 'CA', '加拿大': 'CA',
    au: 'AU', australia: 'AU', 'オーストラリア': 'AU', '澳洲': 'AU',
    nz: 'NZ', 'new zealand': 'NZ', 'ニュージーランド': 'NZ', '紐西蘭': 'NZ',
    ie: 'IE', ireland: 'IE', 'アイルランド': 'IE', '愛爾蘭': 'IE',
    sg: 'SG', singapore: 'SG', 'シンガポール': 'SG', '新加坡': 'SG',
    tw: 'TW', taiwan: 'TW', '台湾': 'TW', '台灣': 'TW', '臺灣': 'TW',
    hk: 'HK', 'hong kong': 'HK', '香港': 'HK',
    kr: 'KR', korea: 'KR', 'south korea': 'KR', '韓国': 'KR', '韓國': 'KR', '韩国': 'KR',
    cn: 'CN', china: 'CN', '中国': 'CN', '中國': 'CN',
    de: 'DE', germany: 'DE', 'ドイツ': 'DE', 'ドイツ連邦共和国': 'DE', '德國': 'DE',
    fr: 'FR', france: 'FR', 'フランス': 'FR', '法國': 'FR',
    it: 'IT', italy: 'IT', 'イタリア': 'IT', '義大利': 'IT', '意大利': 'IT',
    es: 'ES', spain: 'ES', 'スペイン': 'ES', '西班牙': 'ES',
    nl: 'NL', netherlands: 'NL', holland: 'NL', 'オランダ': 'NL', '荷蘭': 'NL',
    be: 'BE', belgium: 'BE', 'ベルギー': 'BE', '比利時': 'BE',
    ch: 'CH', switzerland: 'CH', 'スイス': 'CH', '瑞士': 'CH',
    at: 'AT', austria: 'AT', 'オーストリア': 'AT', '奧地利': 'AT',
    se: 'SE', sweden: 'SE', 'スウェーデン': 'SE', '瑞典': 'SE',
    no: 'NO', norway: 'NO', 'ノルウェー': 'NO', '挪威': 'NO',
    dk: 'DK', denmark: 'DK', 'デンマーク': 'DK', '丹麥': 'DK',
    fi: 'FI', finland: 'FI', 'フィンランド': 'FI', '芬蘭': 'FI',
    pt: 'PT', portugal: 'PT', 'ポルトガル': 'PT', '葡萄牙': 'PT',
    ae: 'AE', uae: 'AE', 'united arab emirates': 'AE', 'アラブ首長国連邦': 'AE', '阿拉伯聯合大公國': 'AE',
    in: 'IN', india: 'IN', 'インド': 'IN', '印度': 'IN',
    za: 'ZA', 'south africa': 'ZA', '南アフリカ': 'ZA', '南非': 'ZA'
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
      { id: 'al', ja: 'アラバマ州', en: 'Alabama', zh: '阿拉巴馬州' },
      { id: 'ak', ja: 'アラスカ州', en: 'Alaska', zh: '阿拉斯加州' },
      { id: 'az', ja: 'アリゾナ州', en: 'Arizona', zh: '亞利桑那州' },
      { id: 'ar', ja: 'アーカンソー州', en: 'Arkansas', zh: '阿肯色州' },
      { id: 'ca', ja: 'カリフォルニア州', en: 'California', zh: '加利福尼亞州' },
      { id: 'co', ja: 'コロラド州', en: 'Colorado', zh: '科羅拉多州' },
      { id: 'ct', ja: 'コネチカット州', en: 'Connecticut', zh: '康乃狄克州' },
      { id: 'de', ja: 'デラウェア州', en: 'Delaware', zh: '德拉瓦州' },
      { id: 'dc', ja: 'ワシントンD.C.', en: 'District of Columbia', zh: '華盛頓哥倫比亞特區' },
      { id: 'fl', ja: 'フロリダ州', en: 'Florida', zh: '佛羅里達州' },
      { id: 'ga', ja: 'ジョージア州', en: 'Georgia', zh: '喬治亞州' },
      { id: 'hi', ja: 'ハワイ州', en: 'Hawaii', zh: '夏威夷州' },
      { id: 'id', ja: 'アイダホ州', en: 'Idaho', zh: '愛達荷州' },
      { id: 'il', ja: 'イリノイ州', en: 'Illinois', zh: '伊利諾州' },
      { id: 'in', ja: 'インディアナ州', en: 'Indiana', zh: '印第安納州' },
      { id: 'ia', ja: 'アイオワ州', en: 'Iowa', zh: '愛荷華州' },
      { id: 'ks', ja: 'カンザス州', en: 'Kansas', zh: '堪薩斯州' },
      { id: 'ky', ja: 'ケンタッキー州', en: 'Kentucky', zh: '肯塔基州' },
      { id: 'la', ja: 'ルイジアナ州', en: 'Louisiana', zh: '路易斯安那州' },
      { id: 'me', ja: 'メイン州', en: 'Maine', zh: '緬因州' },
      { id: 'md', ja: 'メリーランド州', en: 'Maryland', zh: '馬里蘭州' },
      { id: 'ma', ja: 'マサチューセッツ州', en: 'Massachusetts', zh: '麻薩諸塞州' },
      { id: 'mi', ja: 'ミシガン州', en: 'Michigan', zh: '密西根州' },
      { id: 'mn', ja: 'ミネソタ州', en: 'Minnesota', zh: '明尼蘇達州' },
      { id: 'ms', ja: 'ミシシッピ州', en: 'Mississippi', zh: '密西西比州' },
      { id: 'mo', ja: 'ミズーリ州', en: 'Missouri', zh: '密蘇里州' },
      { id: 'mt', ja: 'モンタナ州', en: 'Montana', zh: '蒙大拿州' },
      { id: 'ne', ja: 'ネブラスカ州', en: 'Nebraska', zh: '內布拉斯加州' },
      { id: 'nv', ja: 'ネバダ州', en: 'Nevada', zh: '內華達州' },
      { id: 'nh', ja: 'ニューハンプシャー州', en: 'New Hampshire', zh: '新罕布夏州' },
      { id: 'nj', ja: 'ニュージャージー州', en: 'New Jersey', zh: '紐澤西州' },
      { id: 'nm', ja: 'ニューメキシコ州', en: 'New Mexico', zh: '新墨西哥州' },
      { id: 'ny', ja: 'ニューヨーク州', en: 'New York', zh: '紐約州' },
      { id: 'nc', ja: 'ノースカロライナ州', en: 'North Carolina', zh: '北卡羅來納州' },
      { id: 'nd', ja: 'ノースダコタ州', en: 'North Dakota', zh: '北達科他州' },
      { id: 'oh', ja: 'オハイオ州', en: 'Ohio', zh: '俄亥俄州' },
      { id: 'ok', ja: 'オクラホマ州', en: 'Oklahoma', zh: '奧克拉荷馬州' },
      { id: 'or', ja: 'オレゴン州', en: 'Oregon', zh: '奧勒岡州' },
      { id: 'pa', ja: 'ペンシルベニア州', en: 'Pennsylvania', zh: '賓夕法尼亞州' },
      { id: 'ri', ja: 'ロードアイランド州', en: 'Rhode Island', zh: '羅德島州' },
      { id: 'sc', ja: 'サウスカロライナ州', en: 'South Carolina', zh: '南卡羅來納州' },
      { id: 'sd', ja: 'サウスダコタ州', en: 'South Dakota', zh: '南達科他州' },
      { id: 'tn', ja: 'テネシー州', en: 'Tennessee', zh: '田納西州' },
      { id: 'tx', ja: 'テキサス州', en: 'Texas', zh: '德克薩斯州' },
      { id: 'ut', ja: 'ユタ州', en: 'Utah', zh: '猶他州' },
      { id: 'vt', ja: 'バーモント州', en: 'Vermont', zh: '佛蒙特州' },
      { id: 'va', ja: 'バージニア州', en: 'Virginia', zh: '維吉尼亞州' },
      { id: 'wa', ja: 'ワシントン州', en: 'Washington', zh: '華盛頓州' },
      { id: 'wv', ja: 'ウェストバージニア州', en: 'West Virginia', zh: '西維吉尼亞州' },
      { id: 'wi', ja: 'ウィスコンシン州', en: 'Wisconsin', zh: '威斯康辛州' },
      { id: 'wy', ja: 'ワイオミング州', en: 'Wyoming', zh: '懷俄明州' }
    ],
    GB: [
      { id: 'england', ja: 'イングランド', en: 'England', zh: '英格蘭' },
      { id: 'scotland', ja: 'スコットランド', en: 'Scotland', zh: '蘇格蘭' },
      { id: 'wales', ja: 'ウェールズ', en: 'Wales', zh: '威爾斯' },
      { id: 'ni', ja: '北アイルランド', en: 'Northern Ireland', zh: '北愛爾蘭' }
    ],
    CA: [
      { id: 'on', ja: 'オンタリオ州', en: 'Ontario', zh: '安大略省' },
      { id: 'qc', ja: 'ケベック州', en: 'Quebec', zh: '魁北克省' },
      { id: 'bc', ja: 'ブリティッシュコロンビア州', en: 'British Columbia', zh: '卑詩省' },
      { id: 'ab', ja: 'アルバータ州', en: 'Alberta', zh: '亞伯達省' },
      { id: 'mb', ja: 'マニトバ州', en: 'Manitoba', zh: '曼尼托巴省' },
      { id: 'sk', ja: 'サスカチュワン州', en: 'Saskatchewan', zh: '薩斯喀徹溫省' },
      { id: 'ns', ja: 'ノバスコシア州', en: 'Nova Scotia', zh: '新斯科細亞省' },
      { id: 'nb', ja: 'ニューブランズウィック州', en: 'New Brunswick', zh: '紐布朗斯維克省' },
      { id: 'nl', ja: 'ニューファンドランド・ラブラドール州', en: 'Newfoundland and Labrador', zh: '紐芬蘭與拉布拉多省' },
      { id: 'pe', ja: 'プリンスエドワードアイランド州', en: 'Prince Edward Island', zh: '愛德華王子島省' },
      { id: 'nt', ja: 'ノースウエスト準州', en: 'Northwest Territories', zh: '西北地區' },
      { id: 'yt', ja: 'ユーコン準州', en: 'Yukon', zh: '育空地區' },
      { id: 'nu', ja: 'ヌナブト準州', en: 'Nunavut', zh: '努納武特地區' }
    ],
    AU: [
      { id: 'au_nsw', ja: 'ニューサウスウェールズ州', en: 'New South Wales', zh: '新南威爾斯州' },
      { id: 'au_vic', ja: 'ビクトリア州', en: 'Victoria', zh: '維多利亞州' },
      { id: 'au_qld', ja: 'クイーンズランド州', en: 'Queensland', zh: '昆士蘭州' },
      { id: 'au_wa', ja: '西オーストラリア州', en: 'Western Australia', zh: '西澳州' },
      { id: 'au_sa', ja: '南オーストラリア州', en: 'South Australia', zh: '南澳州' },
      { id: 'au_tas', ja: 'タスマニア州', en: 'Tasmania', zh: '塔斯馬尼亞州' },
      { id: 'au_act', ja: 'オーストラリア首都特別地域', en: 'Australian Capital Territory', zh: '澳洲首都特區' },
      { id: 'au_nt', ja: 'ノーザンテリトリー', en: 'Northern Territory', zh: '北領地' }
    ],
    NZ: [
      { id: 'nz_auckland', ja: 'オークランド地方', en: 'Auckland', zh: '奧克蘭' },
      { id: 'nz_wellington', ja: 'ウェリントン地方', en: 'Wellington', zh: '威靈頓' },
      { id: 'nz_canterbury', ja: 'カンタベリー地方', en: 'Canterbury', zh: '坎特伯雷' },
      { id: 'nz_otago', ja: 'オタゴ地方', en: 'Otago', zh: '奧塔哥' }
    ],
    IE: [
      { id: 'ie_leinster', ja: 'レンスター', en: 'Leinster', zh: '倫斯特' },
      { id: 'ie_munster', ja: 'マンスター', en: 'Munster', zh: '蒙斯特' },
      { id: 'ie_connacht', ja: 'コノート', en: 'Connacht', zh: '康諾特' },
      { id: 'ie_ulster', ja: 'アルスター', en: 'Ulster', zh: '阿爾斯特' }
    ],
    SG: [
      { id: 'sg_central', ja: 'セントラル', en: 'Central', zh: '中區' },
      { id: 'sg_east', ja: 'イースト', en: 'East', zh: '東區' },
      { id: 'sg_north', ja: 'ノース', en: 'North', zh: '北區' },
      { id: 'sg_northeast', ja: 'ノースイースト', en: 'North-East', zh: '東北區' },
      { id: 'sg_west', ja: 'ウェスト', en: 'West', zh: '西區' }
    ],
    TW: [
      { id: 'taipei', ja: '台北市', en: 'Taipei', zh: '臺北市' },
      { id: 'new_taipei', ja: '新北市', en: 'New Taipei', zh: '新北市' },
      { id: 'taoyuan', ja: '桃園市', en: 'Taoyuan', zh: '桃園市' },
      { id: 'taichung', ja: '台中市', en: 'Taichung', zh: '臺中市' },
      { id: 'tainan', ja: '台南市', en: 'Tainan', zh: '臺南市' },
      { id: 'kaohsiung', ja: '高雄市', en: 'Kaohsiung', zh: '高雄市' },
      { id: 'keelung', ja: '基隆市', en: 'Keelung', zh: '基隆市' },
      { id: 'hsinchu_city', ja: '新竹市', en: 'Hsinchu City', zh: '新竹市' },
      { id: 'chiayi_city', ja: '嘉義市', en: 'Chiayi City', zh: '嘉義市' },
      { id: 'hsinchu_county', ja: '新竹県', en: 'Hsinchu County', zh: '新竹縣' },
      { id: 'miaoli', ja: '苗栗県', en: 'Miaoli', zh: '苗栗縣' },
      { id: 'changhua', ja: '彰化県', en: 'Changhua', zh: '彰化縣' },
      { id: 'nantou', ja: '南投県', en: 'Nantou', zh: '南投縣' },
      { id: 'yunlin', ja: '雲林県', en: 'Yunlin', zh: '雲林縣' },
      { id: 'chiayi_county', ja: '嘉義県', en: 'Chiayi County', zh: '嘉義縣' },
      { id: 'pingtung', ja: '屏東県', en: 'Pingtung', zh: '屏東縣' },
      { id: 'yilan', ja: '宜蘭県', en: 'Yilan', zh: '宜蘭縣' },
      { id: 'hualien', ja: '花蓮県', en: 'Hualien', zh: '花蓮縣' },
      { id: 'taitung', ja: '台東県', en: 'Taitung', zh: '臺東縣' },
      { id: 'penghu', ja: '澎湖県', en: 'Penghu', zh: '澎湖縣' },
      { id: 'kinmen', ja: '金門県', en: 'Kinmen', zh: '金門縣' },
      { id: 'lienchiang', ja: '連江県', en: 'Lienchiang', zh: '連江縣' }
    ],
    HK: [
      { id: 'hk_island', ja: '香港島', en: 'Hong Kong Island', zh: '香港島' },
      { id: 'hk_kowloon', ja: '九龍', en: 'Kowloon', zh: '九龍' },
      { id: 'hk_nt', ja: '新界', en: 'New Territories', zh: '新界' }
    ],
    KR: [
      { id: 'seoul', ja: 'ソウル特別市', en: 'Seoul', zh: '首爾特別市' },
      { id: 'busan', ja: '釜山広域市', en: 'Busan', zh: '釜山廣域市' }
    ],
    DE: [
      { id: 'by', ja: 'バイエルン州', en: 'Bavaria', zh: '巴伐利亞邦' },
      { id: 'nw', ja: 'ノルトライン＝ヴェストファーレン州', en: 'North Rhine-Westphalia', zh: '北萊茵－西發利亞邦' },
      { id: 'be', ja: 'ベルリン', en: 'Berlin', zh: '柏林' }
    ],
    FR: [
      { id: 'idf', ja: 'イル＝ド＝フランス', en: 'Ile-de-France', zh: '法蘭西島' },
      { id: 'paca', ja: 'プロヴァンス＝アルプ＝コートダジュール', en: 'Provence-Alpes-Cote d Azur', zh: '普羅旺斯－阿爾卑斯－藍色海岸' }
    ],
    IT: [
      { id: 'it_lazio', ja: 'ラツィオ', en: 'Lazio', zh: '拉齊奧' },
      { id: 'it_lombardy', ja: 'ロンバルディア', en: 'Lombardy', zh: '倫巴底' },
      { id: 'it_tuscany', ja: 'トスカーナ', en: 'Tuscany', zh: '托斯卡尼' }
    ],
    ES: [
      { id: 'es_madrid', ja: 'マドリード州', en: 'Madrid', zh: '馬德里' },
      { id: 'es_catalonia', ja: 'カタルーニャ州', en: 'Catalonia', zh: '加泰隆尼亞' },
      { id: 'es_andalusia', ja: 'アンダルシア州', en: 'Andalusia', zh: '安達魯西亞' }
    ],
    NL: [
      { id: 'nl_nh', ja: '北ホラント州', en: 'North Holland', zh: '北荷蘭省' },
      { id: 'nl_zh', ja: '南ホラント州', en: 'South Holland', zh: '南荷蘭省' }
    ],
    BE: [
      { id: 'be_bru', ja: 'ブリュッセル', en: 'Brussels', zh: '布魯塞爾' },
      { id: 'be_vl', ja: 'フランデレン', en: 'Flanders', zh: '法蘭德斯' }
    ],
    CH: [
      { id: 'ch_zh', ja: 'チューリヒ州', en: 'Zurich', zh: '蘇黎世' },
      { id: 'ch_ge', ja: 'ジュネーヴ州', en: 'Geneva', zh: '日內瓦' }
    ],
    AT: [
      { id: 'at_vienna', ja: 'ウィーン', en: 'Vienna', zh: '維也納' }
    ],
    SE: [
      { id: 'se_stockholm', ja: 'ストックホルム県', en: 'Stockholm', zh: '斯德哥爾摩' }
    ],
    NO: [
      { id: 'no_oslo', ja: 'オスロ', en: 'Oslo', zh: '奧斯陸' }
    ],
    DK: [
      { id: 'dk_hovedstaden', ja: 'デンマーク首都地域', en: 'Capital Region', zh: '首都大區' }
    ],
    FI: [
      { id: 'fi_uusimaa', ja: 'ウーシマー県', en: 'Uusimaa', zh: '新地區' }
    ],
    PT: [
      { id: 'pt_lisbon', ja: 'リスボン県', en: 'Lisbon', zh: '里斯本' }
    ],
    AE: [
      { id: 'ae_dubai', ja: 'ドバイ', en: 'Dubai', zh: '杜拜' },
      { id: 'ae_abudhabi', ja: 'アブダビ', en: 'Abu Dhabi', zh: '阿布達比' }
    ],
    IN: [
      { id: 'in_mh', ja: 'マハーラーシュトラ州', en: 'Maharashtra', zh: '馬哈拉施特拉邦' },
      { id: 'in_dl', ja: 'デリー', en: 'Delhi', zh: '德里' },
      { id: 'in_ka', ja: 'カルナータカ州', en: 'Karnataka', zh: '卡納塔克邦' }
    ],
    ZA: [
      { id: 'za_gt', ja: 'ハウテン州', en: 'Gauteng', zh: '豪登省' },
      { id: 'za_wc', ja: '西ケープ州', en: 'Western Cape', zh: '西開普省' }
    ],
    CN: [
      { id: 'cn_beijing', ja: '北京市', en: 'Beijing', zh: '北京市' },
      { id: 'cn_shanghai', ja: '上海市', en: 'Shanghai', zh: '上海市' },
      { id: 'cn_guangdong', ja: '広東省', en: 'Guangdong', zh: '廣東省' }
    ]
  };

  var CITIES = {
    tokyo: [
      { id: 'tokyo_city', ja: '東京', en: 'Tokyo', zh: '東京' },
      { id: 'shinjuku', ja: '新宿区', en: 'Shinjuku', zh: '新宿區' },
      { id: 'shibuya', ja: '渋谷区', en: 'Shibuya', zh: '澀谷區' },
      { id: 'minato', ja: '港区', en: 'Minato', zh: '港區' },
      { id: 'setagaya', ja: '世田谷区', en: 'Setagaya', zh: '世田谷區' },
      { id: 'hachioji', ja: '八王子市', en: 'Hachioji', zh: '八王子市' },
      { id: 'machida', ja: '町田市', en: 'Machida', zh: '町田市' }
    ],
    kanagawa: [
      { id: 'yokohama', ja: '横浜市', en: 'Yokohama', zh: '橫濱市' },
      { id: 'kawasaki', ja: '川崎市', en: 'Kawasaki', zh: '川崎市' },
      { id: 'sagamihara', ja: '相模原市', en: 'Sagamihara', zh: '相模原市' },
      { id: 'fujisawa', ja: '藤沢市', en: 'Fujisawa', zh: '藤澤市' },
      { id: 'kamakura', ja: '鎌倉市', en: 'Kamakura', zh: '鎌倉市' },
      { id: 'yokosuka', ja: '横須賀市', en: 'Yokosuka', zh: '橫須賀市' }
    ],
    osaka: [
      { id: 'osaka_city', ja: '大阪市', en: 'Osaka', zh: '大阪市' },
      { id: 'sakai', ja: '堺市', en: 'Sakai', zh: '堺市' },
      { id: 'higashiosaka', ja: '東大阪市', en: 'Higashiosaka', zh: '東大阪市' }
    ],
    hyogo: [
      { id: 'kobe', ja: '神戸市', en: 'Kobe', zh: '神戶市' }
    ],
    kyoto: [
      { id: 'kyoto_city', ja: '京都市', en: 'Kyoto', zh: '京都市' }
    ],
    fukuoka: [
      { id: 'fukuoka_city', ja: '福岡市', en: 'Fukuoka', zh: '福岡市' },
      { id: 'kitakyushu', ja: '北九州市', en: 'Kitakyushu', zh: '北九州市' }
    ],
    hokkaido: [
      { id: 'sapporo', ja: '札幌市', en: 'Sapporo', zh: '札幌市' },
      { id: 'hakodate', ja: '函館市', en: 'Hakodate', zh: '函館市' },
      { id: 'asahikawa', ja: '旭川市', en: 'Asahikawa', zh: '旭川市' }
    ],
    aichi: [
      { id: 'nagoya', ja: '名古屋市', en: 'Nagoya', zh: '名古屋市' }
    ],
    miyagi: [{ id: 'sendai', ja: '仙台市', en: 'Sendai', zh: '仙台市' }],
    saitama: [{ id: 'saitama_city', ja: 'さいたま市', en: 'Saitama', zh: '埼玉市' }],
    chiba: [{ id: 'chiba_city', ja: '千葉市', en: 'Chiba', zh: '千葉市' }],
    hiroshima: [{ id: 'hiroshima_city', ja: '広島市', en: 'Hiroshima', zh: '廣島市' }],
    okinawa: [{ id: 'naha', ja: '那覇市', en: 'Naha', zh: '那霸市' }],
    niigata: [{ id: 'niigata_city', ja: '新潟市', en: 'Niigata', zh: '新潟市' }],
    shizuoka: [
      { id: 'shizuoka_city', ja: '静岡市', en: 'Shizuoka', zh: '靜岡市' },
      { id: 'hamamatsu', ja: '浜松市', en: 'Hamamatsu', zh: '濱松市' }
    ],
    ishikawa: [{ id: 'kanazawa', ja: '金沢市', en: 'Kanazawa', zh: '金澤市' }],
    kumamoto: [{ id: 'kumamoto_city', ja: '熊本市', en: 'Kumamoto', zh: '熊本市' }],
    aomori: [{ id: 'aomori_city', ja: '青森市', en: 'Aomori', zh: '青森市' }],
    iwate: [{ id: 'morioka', ja: '盛岡市', en: 'Morioka', zh: '盛岡市' }],
    akita: [{ id: 'akita_city', ja: '秋田市', en: 'Akita', zh: '秋田市' }],
    yamagata: [{ id: 'yamagata_city', ja: '山形市', en: 'Yamagata', zh: '山形市' }],
    fukushima: [{ id: 'fukushima_city', ja: '福島市', en: 'Fukushima', zh: '福島市' }],
    ibaraki: [{ id: 'mito', ja: '水戸市', en: 'Mito', zh: '水戶市' }],
    tochigi: [{ id: 'utsunomiya', ja: '宇都宮市', en: 'Utsunomiya', zh: '宇都宮市' }],
    gunma: [{ id: 'maebashi', ja: '前橋市', en: 'Maebashi', zh: '前橋市' }],
    toyama: [{ id: 'toyama_city', ja: '富山市', en: 'Toyama', zh: '富山市' }],
    fukui: [{ id: 'fukui_city', ja: '福井市', en: 'Fukui', zh: '福井市' }],
    yamanashi: [{ id: 'kofu', ja: '甲府市', en: 'Kofu', zh: '甲府市' }],
    nagano: [{ id: 'nagano_city', ja: '長野市', en: 'Nagano', zh: '長野市' }],
    gifu: [{ id: 'gifu_city', ja: '岐阜市', en: 'Gifu', zh: '岐阜市' }],
    mie: [{ id: 'tsu', ja: '津市', en: 'Tsu', zh: '津市' }],
    shiga: [{ id: 'otsu', ja: '大津市', en: 'Otsu', zh: '大津市' }],
    nara: [{ id: 'nara_city', ja: '奈良市', en: 'Nara', zh: '奈良市' }],
    wakayama: [{ id: 'wakayama_city', ja: '和歌山市', en: 'Wakayama', zh: '和歌山市' }],
    tottori: [{ id: 'tottori_city', ja: '鳥取市', en: 'Tottori', zh: '鳥取市' }],
    shimane: [{ id: 'matsue', ja: '松江市', en: 'Matsue', zh: '松江市' }],
    okayama: [{ id: 'okayama_city', ja: '岡山市', en: 'Okayama', zh: '岡山市' }],
    yamaguchi: [{ id: 'yamaguchi_city', ja: '山口市', en: 'Yamaguchi', zh: '山口市' }],
    tokushima: [{ id: 'tokushima_city', ja: '徳島市', en: 'Tokushima', zh: '德島市' }],
    kagawa: [{ id: 'takamatsu', ja: '高松市', en: 'Takamatsu', zh: '高松市' }],
    ehime: [{ id: 'matsuyama', ja: '松山市', en: 'Matsuyama', zh: '松山市' }],
    kochi: [{ id: 'kochi_city', ja: '高知市', en: 'Kochi', zh: '高知市' }],
    saga: [{ id: 'saga_city', ja: '佐賀市', en: 'Saga', zh: '佐賀市' }],
    nagasaki: [{ id: 'nagasaki_city', ja: '長崎市', en: 'Nagasaki', zh: '長崎市' }],
    oita: [{ id: 'oita_city', ja: '大分市', en: 'Oita', zh: '大分市' }],
    miyazaki: [{ id: 'miyazaki_city', ja: '宮崎市', en: 'Miyazaki', zh: '宮崎市' }],
    kagoshima: [{ id: 'kagoshima_city', ja: '鹿児島市', en: 'Kagoshima', zh: '鹿兒島市' }],
    ca: [
      { id: 'los_angeles', ja: 'ロサンゼルス', en: 'Los Angeles', zh: '洛杉磯' },
      { id: 'san_francisco', ja: 'サンフランシスコ', en: 'San Francisco', zh: '舊金山' },
      { id: 'san_diego', ja: 'サンディエゴ', en: 'San Diego', zh: '聖地牙哥' },
      { id: 'san_jose', ja: 'サンノゼ', en: 'San Jose', zh: '聖荷西' }
    ],
    ny: [
      { id: 'new_york', ja: 'ニューヨーク市', en: 'New York City', zh: '紐約市' },
      { id: 'buffalo', ja: 'バッファロー', en: 'Buffalo', zh: '水牛城' }
    ],
    tx: [
      { id: 'houston', ja: 'ヒューストン', en: 'Houston', zh: '休士頓' },
      { id: 'dallas', ja: 'ダラス', en: 'Dallas', zh: '達拉斯' },
      { id: 'austin', ja: 'オースティン', en: 'Austin', zh: '奧斯汀' },
      { id: 'san_antonio', ja: 'サンアントニオ', en: 'San Antonio', zh: '聖安東尼奧' }
    ],
    wa: [
      { id: 'seattle', ja: 'シアトル', en: 'Seattle', zh: '西雅圖' }
    ],
    fl: [
      { id: 'miami', ja: 'マイアミ', en: 'Miami', zh: '邁阿密' },
      { id: 'orlando', ja: 'オーランド', en: 'Orlando', zh: '奧蘭多' }
    ],
    il: [
      { id: 'chicago', ja: 'シカゴ', en: 'Chicago', zh: '芝加哥' }
    ],
    dc: [
      { id: 'washington_dc', ja: 'ワシントンD.C.', en: 'Washington', zh: '華盛頓' }
    ],
    hi: [
      { id: 'honolulu', ja: 'ホノルル', en: 'Honolulu', zh: '檀香山' }
    ],
    england: [
      { id: 'london', ja: 'ロンドン', en: 'London', zh: '倫敦' },
      { id: 'manchester', ja: 'マンチェスター', en: 'Manchester', zh: '曼徹斯特' },
      { id: 'birmingham', ja: 'バーミンガム', en: 'Birmingham', zh: '伯明罕' }
    ],
    scotland: [
      { id: 'edinburgh', ja: 'エディンバラ', en: 'Edinburgh', zh: '愛丁堡' },
      { id: 'glasgow', ja: 'グラスゴー', en: 'Glasgow', zh: '格拉斯哥' }
    ],
    wales: [
      { id: 'cardiff', ja: 'カーディフ', en: 'Cardiff', zh: '卡迪夫' }
    ],
    ni: [
      { id: 'belfast', ja: 'ベルファスト', en: 'Belfast', zh: '貝爾法斯特' }
    ],
    on: [
      { id: 'toronto', ja: 'トロント', en: 'Toronto', zh: '多倫多' },
      { id: 'ottawa', ja: 'オタワ', en: 'Ottawa', zh: '渥太華' }
    ],
    qc: [
      { id: 'montreal', ja: 'モントリオール', en: 'Montreal', zh: '蒙特婁' }
    ],
    bc: [
      { id: 'vancouver', ja: 'バンクーバー', en: 'Vancouver', zh: '溫哥華' }
    ],
    ab: [
      { id: 'calgary', ja: 'カルガリー', en: 'Calgary', zh: '卡加利' }
    ],
    au_nsw: [
      { id: 'sydney', ja: 'シドニー', en: 'Sydney', zh: '雪梨' }
    ],
    au_vic: [
      { id: 'melbourne', ja: 'メルボルン', en: 'Melbourne', zh: '墨爾本' }
    ],
    au_qld: [
      { id: 'brisbane', ja: 'ブリスベン', en: 'Brisbane', zh: '布里斯本' }
    ],
    au_wa: [
      { id: 'perth', ja: 'パース', en: 'Perth', zh: '伯斯' }
    ],
    au_sa: [
      { id: 'adelaide', ja: 'アデレード', en: 'Adelaide', zh: '阿得雷德' }
    ],
    au_act: [
      { id: 'canberra', ja: 'キャンベラ', en: 'Canberra', zh: '坎培拉' }
    ],
    nz_auckland: [
      { id: 'auckland_city', ja: 'オークランド', en: 'Auckland', zh: '奧克蘭' }
    ],
    nz_wellington: [
      { id: 'wellington_city', ja: 'ウェリントン', en: 'Wellington', zh: '威靈頓' }
    ],
    nz_canterbury: [
      { id: 'christchurch', ja: 'クライストチャーチ', en: 'Christchurch', zh: '基督城' }
    ],
    nz_otago: [
      { id: 'queenstown', ja: 'クイーンズタウン', en: 'Queenstown', zh: '皇后鎮' }
    ],
    ie_leinster: [
      { id: 'dublin', ja: 'ダブリン', en: 'Dublin', zh: '都柏林' }
    ],
    ie_munster: [
      { id: 'cork', ja: 'コーク', en: 'Cork', zh: '科克' }
    ],
    sg_central: [
      { id: 'singapore_city', ja: 'シンガポール', en: 'Singapore', zh: '新加坡' }
    ],
    taipei: [
      { id: 'taipei_city', ja: '台北', en: 'Taipei', zh: '臺北' }
    ],
    new_taipei: [
      { id: 'banqiao', ja: '板橋', en: 'Banqiao', zh: '板橋' },
      { id: 'tamsui', ja: '淡水', en: 'Tamsui', zh: '淡水' }
    ],
    taoyuan: [
      { id: 'taoyuan_city', ja: '桃園', en: 'Taoyuan', zh: '桃園' }
    ],
    taichung: [
      { id: 'taichung_city', ja: '台中', en: 'Taichung', zh: '臺中' }
    ],
    tainan: [
      { id: 'tainan_city', ja: '台南', en: 'Tainan', zh: '臺南' }
    ],
    kaohsiung: [
      { id: 'kaohsiung_city', ja: '高雄', en: 'Kaohsiung', zh: '高雄' }
    ],
    hk_island: [
      { id: 'central_hk', ja: '中環', en: 'Central', zh: '中環' }
    ],
    hk_kowloon: [
      { id: 'tsim_sha_tsui', ja: '尖沙咀', en: 'Tsim Sha Tsui', zh: '尖沙咀' }
    ],
    by: [
      { id: 'munich', ja: 'ミュンヘン', en: 'Munich', zh: '慕尼黑' }
    ],
    nw: [
      { id: 'cologne', ja: 'ケルン', en: 'Cologne', zh: '科隆' },
      { id: 'dusseldorf', ja: 'デュッセルドルフ', en: 'Dusseldorf', zh: '杜塞道夫' }
    ],
    idf: [
      { id: 'paris', ja: 'パリ', en: 'Paris', zh: '巴黎' }
    ],
    paca: [
      { id: 'marseille', ja: 'マルセイユ', en: 'Marseille', zh: '馬賽' },
      { id: 'nice', ja: 'ニース', en: 'Nice', zh: '尼斯' }
    ],
    it_lazio: [
      { id: 'rome', ja: 'ローマ', en: 'Rome', zh: '羅馬' }
    ],
    it_lombardy: [
      { id: 'milan', ja: 'ミラノ', en: 'Milan', zh: '米蘭' }
    ],
    es_madrid: [
      { id: 'madrid_city', ja: 'マドリード', en: 'Madrid', zh: '馬德里' }
    ],
    es_catalonia: [
      { id: 'barcelona', ja: 'バルセロナ', en: 'Barcelona', zh: '巴塞隆納' }
    ],
    nl_nh: [
      { id: 'amsterdam', ja: 'アムステルダム', en: 'Amsterdam', zh: '阿姆斯特丹' }
    ],
    seoul: [
      { id: 'seoul_city', ja: 'ソウル', en: 'Seoul', zh: '首爾' }
    ],
    in_mh: [
      { id: 'mumbai', ja: 'ムンバイ', en: 'Mumbai', zh: '孟買' }
    ],
    in_dl: [
      { id: 'new_delhi', ja: 'ニューデリー', en: 'New Delhi', zh: '新德里' }
    ],
    ae_dubai: [
      { id: 'dubai_city', ja: 'ドバイ', en: 'Dubai', zh: '杜拜' }
    ],
    za_gt: [
      { id: 'johannesburg', ja: 'ヨハネスブルク', en: 'Johannesburg', zh: '約翰尼斯堡' }
    ],
    cn_beijing: [
      { id: 'beijing_city', ja: '北京', en: 'Beijing', zh: '北京' }
    ],
    cn_shanghai: [
      { id: 'shanghai_city', ja: '上海', en: 'Shanghai', zh: '上海' }
    ]
  };

  var TZ_TOKYO = 'Asia/Tokyo (JST, UTC+9)';
  var TZ_TAIPEI = 'Asia/Taipei (CST, UTC+8)';
  var TZ_EAST = 'America/New_York (EST/EDT, UTC-5/-4)';
  var TZ_CENTRAL = 'America/Chicago (CST/CDT, UTC-6/-5)';
  var TZ_MOUNTAIN = 'America/Denver (MST/MDT, UTC-7/-6)';
  var TZ_PACIFIC = 'America/Los_Angeles (PST/PDT, UTC-8/-7)';
  var TIMEZONE_BY_STATE = {
    al: TZ_CENTRAL, ak: 'America/Anchorage (AKST/AKDT, UTC-9/-8)', az: 'America/Phoenix (MST, UTC-7)',
    ar: TZ_CENTRAL, ca: TZ_PACIFIC, co: TZ_MOUNTAIN, ct: TZ_EAST, de: TZ_EAST, dc: TZ_EAST,
    fl: TZ_EAST, ga: TZ_EAST, hi: 'Pacific/Honolulu (HST, UTC-10)', id: TZ_MOUNTAIN, il: TZ_CENTRAL,
    'in': TZ_EAST, ia: TZ_CENTRAL, ks: TZ_CENTRAL, ky: TZ_EAST, la: TZ_CENTRAL, me: TZ_EAST,
    md: TZ_EAST, ma: TZ_EAST, mi: TZ_EAST, mn: TZ_CENTRAL, ms: TZ_CENTRAL, mo: TZ_CENTRAL,
    mt: TZ_MOUNTAIN, ne: TZ_CENTRAL, nv: TZ_PACIFIC, nh: TZ_EAST, nj: TZ_EAST, nm: TZ_MOUNTAIN,
    ny: TZ_EAST, nc: TZ_EAST, nd: TZ_CENTRAL, oh: TZ_EAST, ok: TZ_CENTRAL, or: TZ_PACIFIC,
    pa: TZ_EAST, ri: TZ_EAST, sc: TZ_EAST, sd: TZ_CENTRAL, tn: TZ_EAST, tx: TZ_CENTRAL,
    ut: TZ_MOUNTAIN, vt: TZ_EAST, va: TZ_EAST, wa: TZ_PACIFIC, wv: TZ_EAST, wi: TZ_CENTRAL, wy: TZ_MOUNTAIN,
    england: 'Europe/London (GMT/BST, UTC+0/+1)',
    scotland: 'Europe/London (GMT/BST, UTC+0/+1)',
    wales: 'Europe/London (GMT/BST, UTC+0/+1)',
    ni: 'Europe/London (GMT/BST, UTC+0/+1)',
    by: 'Europe/Berlin (CET/CEST, UTC+1/+2)',
    nw: 'Europe/Berlin (CET/CEST, UTC+1/+2)',
    be: 'Europe/Berlin (CET/CEST, UTC+1/+2)',
    idf: 'Europe/Paris (CET/CEST, UTC+1/+2)',
    paca: 'Europe/Paris (CET/CEST, UTC+1/+2)',
    taipei: TZ_TAIPEI, new_taipei: TZ_TAIPEI, taoyuan: TZ_TAIPEI, taichung: TZ_TAIPEI,
    tainan: TZ_TAIPEI, kaohsiung: TZ_TAIPEI, keelung: TZ_TAIPEI, hsinchu_city: TZ_TAIPEI,
    chiayi_city: TZ_TAIPEI, hsinchu_county: TZ_TAIPEI, miaoli: TZ_TAIPEI, changhua: TZ_TAIPEI,
    nantou: TZ_TAIPEI, yunlin: TZ_TAIPEI, chiayi_county: TZ_TAIPEI, pingtung: TZ_TAIPEI,
    yilan: TZ_TAIPEI, hualien: TZ_TAIPEI, taitung: TZ_TAIPEI, penghu: TZ_TAIPEI,
    kinmen: TZ_TAIPEI, lienchiang: TZ_TAIPEI,
    seoul: 'Asia/Seoul (KST, UTC+9)',
    busan: 'Asia/Seoul (KST, UTC+9)',
    au_nsw: 'Australia/Sydney (AEST/AEDT, UTC+10/+11)',
    au_vic: 'Australia/Sydney (AEST/AEDT, UTC+10/+11)',
    au_qld: 'Australia/Brisbane (AEST, UTC+10)',
    au_wa: 'Australia/Perth (AWST, UTC+8)',
    au_sa: 'Australia/Adelaide (ACST/ACDT, UTC+9:30/+10:30)',
    au_tas: 'Australia/Hobart (AEST/AEDT, UTC+10/+11)',
    au_act: 'Australia/Sydney (AEST/AEDT, UTC+10/+11)',
    au_nt: 'Australia/Darwin (ACST, UTC+9:30)',
    on: 'America/Toronto (EST/EDT, UTC-5/-4)',
    qc: 'America/Toronto (EST/EDT, UTC-5/-4)',
    bc: 'America/Vancouver (PST/PDT, UTC-8/-7)',
    ab: 'America/Edmonton (MST/MDT, UTC-7/-6)',
    mb: 'America/Winnipeg (CST/CDT, UTC-6/-5)',
    sk: 'America/Regina (CST, UTC-6)',
    ns: 'America/Halifax (AST/ADT, UTC-4/-3)',
    nb: 'America/Halifax (AST/ADT, UTC-4/-3)',
    nl: 'America/St_Johns (NST/NDT, UTC-3:30/-2:30)',
    pe: 'America/Halifax (AST/ADT, UTC-4/-3)',
    nt: 'America/Yellowknife (MST/MDT, UTC-7/-6)',
    yt: 'America/Whitehorse (MST, UTC-7)',
    nu: 'America/Iqaluit (EST/EDT, UTC-5/-4)',
    nz_auckland: 'Pacific/Auckland (NZST/NZDT, UTC+12/+13)',
    nz_wellington: 'Pacific/Auckland (NZST/NZDT, UTC+12/+13)',
    nz_canterbury: 'Pacific/Auckland (NZST/NZDT, UTC+12/+13)',
    nz_otago: 'Pacific/Auckland (NZST/NZDT, UTC+12/+13)',
    ie_leinster: 'Europe/Dublin (GMT/IST, UTC+0/+1)',
    ie_munster: 'Europe/Dublin (GMT/IST, UTC+0/+1)',
    ie_connacht: 'Europe/Dublin (GMT/IST, UTC+0/+1)',
    ie_ulster: 'Europe/Dublin (GMT/IST, UTC+0/+1)',
    sg_central: 'Asia/Singapore (SGT, UTC+8)',
    sg_east: 'Asia/Singapore (SGT, UTC+8)',
    sg_north: 'Asia/Singapore (SGT, UTC+8)',
    sg_northeast: 'Asia/Singapore (SGT, UTC+8)',
    sg_west: 'Asia/Singapore (SGT, UTC+8)',
    hk_island: 'Asia/Hong_Kong (HKT, UTC+8)',
    hk_kowloon: 'Asia/Hong_Kong (HKT, UTC+8)',
    hk_nt: 'Asia/Hong_Kong (HKT, UTC+8)',
    it_lazio: 'Europe/Rome (CET/CEST, UTC+1/+2)',
    it_lombardy: 'Europe/Rome (CET/CEST, UTC+1/+2)',
    it_tuscany: 'Europe/Rome (CET/CEST, UTC+1/+2)',
    es_madrid: 'Europe/Madrid (CET/CEST, UTC+1/+2)',
    es_catalonia: 'Europe/Madrid (CET/CEST, UTC+1/+2)',
    es_andalusia: 'Europe/Madrid (CET/CEST, UTC+1/+2)',
    nl_nh: 'Europe/Amsterdam (CET/CEST, UTC+1/+2)',
    nl_zh: 'Europe/Amsterdam (CET/CEST, UTC+1/+2)',
    be_bru: 'Europe/Brussels (CET/CEST, UTC+1/+2)',
    be_vl: 'Europe/Brussels (CET/CEST, UTC+1/+2)',
    ch_zh: 'Europe/Zurich (CET/CEST, UTC+1/+2)',
    ch_ge: 'Europe/Zurich (CET/CEST, UTC+1/+2)',
    at_vienna: 'Europe/Vienna (CET/CEST, UTC+1/+2)',
    se_stockholm: 'Europe/Stockholm (CET/CEST, UTC+1/+2)',
    no_oslo: 'Europe/Oslo (CET/CEST, UTC+1/+2)',
    dk_hovedstaden: 'Europe/Copenhagen (CET/CEST, UTC+1/+2)',
    fi_uusimaa: 'Europe/Helsinki (EET/EEST, UTC+2/+3)',
    pt_lisbon: 'Europe/Lisbon (WET/WEST, UTC+0/+1)',
    ae_dubai: 'Asia/Dubai (GST, UTC+4)',
    ae_abudhabi: 'Asia/Dubai (GST, UTC+4)',
    in_mh: 'Asia/Kolkata (IST, UTC+5:30)',
    in_dl: 'Asia/Kolkata (IST, UTC+5:30)',
    in_ka: 'Asia/Kolkata (IST, UTC+5:30)',
    za_gt: 'Africa/Johannesburg (SAST, UTC+2)',
    za_wc: 'Africa/Johannesburg (SAST, UTC+2)',
    cn_beijing: 'Asia/Shanghai (CST, UTC+8)',
    cn_shanghai: 'Asia/Shanghai (CST, UTC+8)',
    cn_guangdong: 'Asia/Shanghai (CST, UTC+8)'
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

  var TIMEZONE_BY_COUNTRY = {
    JP: TZ_TOKYO,
    TW: TZ_TAIPEI,
    HK: 'Asia/Hong_Kong (HKT, UTC+8)',
    KR: 'Asia/Seoul (KST, UTC+9)',
    CN: 'Asia/Shanghai (CST, UTC+8)',
    SG: 'Asia/Singapore (SGT, UTC+8)',
    GB: 'Europe/London (GMT/BST, UTC+0/+1)',
    IE: 'Europe/Dublin (GMT/IST, UTC+0/+1)',
    DE: 'Europe/Berlin (CET/CEST, UTC+1/+2)',
    FR: 'Europe/Paris (CET/CEST, UTC+1/+2)',
    IT: 'Europe/Rome (CET/CEST, UTC+1/+2)',
    ES: 'Europe/Madrid (CET/CEST, UTC+1/+2)',
    NL: 'Europe/Amsterdam (CET/CEST, UTC+1/+2)',
    BE: 'Europe/Brussels (CET/CEST, UTC+1/+2)',
    CH: 'Europe/Zurich (CET/CEST, UTC+1/+2)',
    AT: 'Europe/Vienna (CET/CEST, UTC+1/+2)',
    SE: 'Europe/Stockholm (CET/CEST, UTC+1/+2)',
    NO: 'Europe/Oslo (CET/CEST, UTC+1/+2)',
    DK: 'Europe/Copenhagen (CET/CEST, UTC+1/+2)',
    FI: 'Europe/Helsinki (EET/EEST, UTC+2/+3)',
    PT: 'Europe/Lisbon (WET/WEST, UTC+0/+1)',
    AU: 'Australia/Sydney (AEST/AEDT, UTC+10/+11)',
    NZ: 'Pacific/Auckland (NZST/NZDT, UTC+12/+13)',
    IN: 'Asia/Kolkata (IST, UTC+5:30)',
    AE: 'Asia/Dubai (GST, UTC+4)',
    ZA: 'Africa/Johannesburg (SAST, UTC+2)',
    US: TZ_EAST,
    CA: 'America/Toronto (EST/EDT, UTC-5/-4)'
  };

  function timezoneFor(stateRaw) {
    var rec = findState(stateRaw);
    if (!rec) return '';
    if (TIMEZONE_BY_STATE[rec.id]) return TIMEZONE_BY_STATE[rec.id];
    for (var i = 0; i < JP_PREFECTURES.length; i++) {
      if (JP_PREFECTURES[i].id === rec.id) return TZ_TOKYO;
    }
    return '';
  }

  function timezoneForCountry(countryRaw) {
    var code = toCanonicalCountry(countryRaw);
    return code && TIMEZONE_BY_COUNTRY[code] ? TIMEZONE_BY_COUNTRY[code] : '';
  }

  function browserTimezone() {
    try {
      if (global.Intl && Intl.DateTimeFormat) {
        return String(Intl.DateTimeFormat().resolvedOptions().timeZone || '').trim();
      }
    } catch (_e) {}
    return '';
  }

  /* KPI-PROFILE-LOCATION-TIMEZONE-RESOLVE */
  function resolveTimezone(opts) {
    opts = opts || {};
    var fromState = timezoneFor(opts.state);
    if (fromState) return fromState;
    var stateRaw = String(opts.state == null ? '' : opts.state).trim();
    if (!stateRaw || isPrompt(stateRaw)) {
      var fromCountry = timezoneForCountry(opts.country);
      if (fromCountry) return fromCountry;
    }
    var existing = String(opts.existing == null ? '' : opts.existing).trim();
    if (existing) return existing;
    return browserTimezone();
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

  function selectValueIfPresent(el) {
    /* KPI-PROFILE-LOCATION-OVERWRITE-SELECT */
    if (!el) return false;
    var v = String(el.value == null ? '' : el.value);
    if (!v) return false;
    try {
      if (typeof el.select === 'function') el.select();
      if (typeof el.setSelectionRange === 'function' && el.type !== 'number') {
        el.setSelectionRange(0, v.length);
      }
    } catch (_e) {}
    return true;
  }

  /* KPI-PROFILE-LOCATION-CANDIDATE-DROPDOWN
   * Native <datalist> filters by current value, so ▼ cannot show the full catalog.
   * Custom menu: ▼ = all candidates; typing = filtered; input body = select-all overwrite.
   */
  var _openMenus = [];

  function filterCandidateLabels(labels, query, opts) {
    opts = opts || {};
    var list = Array.isArray(labels) ? labels.slice() : [];
    if (opts.showAll) return list;
    var q = fold(query);
    if (!q) return list;
    return list.filter(function (label) {
      return fold(label).indexOf(q) !== -1;
    });
  }

  function toggleAriaLabel(locale) {
    var loc = localeOf(locale || localeFromDocument());
    if (loc === 'ja') return '候補一覧を表示';
    if (loc === 'zh-tw') return '顯示候選清單';
    return 'Show suggestions';
  }

  function closeCandidateMenu(el) {
    if (!el || !el._kpiLoc) return;
    var menu = el._kpiLoc.menu;
    var btn = el._kpiLoc.btn;
    if (menu) {
      menu.hidden = true;
      menu.innerHTML = '';
    }
    if (btn) btn.setAttribute('aria-expanded', 'false');
    el._kpiLoc.activeIndex = -1;
    el._kpiLoc.showAll = false;
    var idx = _openMenus.indexOf(el);
    if (idx >= 0) _openMenus.splice(idx, 1);
  }

  function closeAllCandidateMenus(exceptEl) {
    _openMenus.slice().forEach(function (el) {
      if (el !== exceptEl) closeCandidateMenu(el);
    });
  }

  function renderCandidateMenu(el, labels) {
    var menu = el._kpiLoc && el._kpiLoc.menu;
    if (!menu) return;
    menu.innerHTML = '';
    var current = String(el.value || '');
    labels.forEach(function (label, i) {
      var li = document.createElement('li');
      li.className = 'profile-location-option';
      li.setAttribute('role', 'option');
      li.setAttribute('data-value', label);
      li.id = (el.id || 'profile-location') + '-opt-' + i;
      li.textContent = label;
      if (label === current) li.classList.add('is-current');
      li.addEventListener('mousedown', function (e) {
        e.preventDefault();
        e.stopPropagation();
        pickCandidate(el, label);
      });
      menu.appendChild(li);
    });
    menu.hidden = labels.length === 0;
    if (el._kpiLoc.btn) {
      el._kpiLoc.btn.setAttribute('aria-expanded', labels.length ? 'true' : 'false');
    }
  }

  function setActiveCandidate(el, index) {
    if (!el._kpiLoc || !el._kpiLoc.menu) return;
    var items = el._kpiLoc.menu.querySelectorAll('.profile-location-option');
    if (!items.length) {
      el._kpiLoc.activeIndex = -1;
      return;
    }
    if (index < 0) index = items.length - 1;
    if (index >= items.length) index = 0;
    el._kpiLoc.activeIndex = index;
    for (var i = 0; i < items.length; i++) {
      if (i === index) {
        items[i].classList.add('is-active');
        items[i].setAttribute('aria-selected', 'true');
        if (typeof items[i].scrollIntoView === 'function') {
          items[i].scrollIntoView({ block: 'nearest' });
        }
      } else {
        items[i].classList.remove('is-active');
        items[i].removeAttribute('aria-selected');
      }
    }
  }

  function pickCandidate(el, label) {
    el.value = label;
    try {
      el.dispatchEvent(new Event('input', { bubbles: true }));
      el.dispatchEvent(new Event('change', { bubbles: true }));
    } catch (_e) {}
    closeCandidateMenu(el);
    try {
      el.focus();
      selectValueIfPresent(el);
    } catch (_e2) {}
  }

  function openCandidateMenu(el, opts) {
    opts = opts || {};
    if (!el || !el._kpiLoc) return [];
    closeAllCandidateMenus(el);
    var getLabels = el._kpiLoc.getLabels;
    var all = typeof getLabels === 'function' ? (getLabels() || []) : [];
    var showAll = !!opts.showAll;
    el._kpiLoc.showAll = showAll;
    var shown = filterCandidateLabels(all, el.value, { showAll: showAll });
    renderCandidateMenu(el, shown);
    if (_openMenus.indexOf(el) < 0) _openMenus.push(el);
    if (shown.length) {
      var current = String(el.value || '');
      var curIdx = shown.indexOf(current);
      setActiveCandidate(el, curIdx >= 0 ? curIdx : 0);
    }
    return shown;
  }

  function ensureCandidateChrome(el) {
    if (!el || !global.document) return null;
    if (el._kpiLoc && el._kpiLoc.wrap) return el._kpiLoc.wrap;
    var parent = el.parentNode;
    if (!parent) return null;
    var wrap = parent.classList && parent.classList.contains('profile-location-field')
      ? parent
      : null;
    if (!wrap) {
      wrap = document.createElement('div');
      wrap.className = 'profile-location-field';
      parent.insertBefore(wrap, el);
      wrap.appendChild(el);
    }
    el.classList.add('profile-location-input');
    el.removeAttribute('list');
    el.setAttribute('autocomplete', 'off');
    el.setAttribute('aria-autocomplete', 'list');

    var btn = wrap.querySelector('.profile-location-toggle');
    if (!btn) {
      btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'profile-location-toggle';
      btn.tabIndex = -1;
      wrap.appendChild(btn);
    }
    btn.setAttribute('aria-label', toggleAriaLabel());
    btn.setAttribute('aria-expanded', 'false');
    btn.setAttribute('aria-controls', (el.id || 'profile-location') + '-menu');

    var menu = wrap.querySelector('.profile-location-dropdown');
    if (!menu) {
      menu = document.createElement('ul');
      menu.className = 'profile-location-dropdown';
      menu.setAttribute('role', 'listbox');
      menu.hidden = true;
      wrap.appendChild(menu);
    }
    menu.id = (el.id || 'profile-location') + '-menu';

    el._kpiLoc = el._kpiLoc || {};
    el._kpiLoc.wrap = wrap;
    el._kpiLoc.btn = btn;
    el._kpiLoc.menu = menu;
    el._kpiLoc.activeIndex = -1;
    el._kpiLoc.showAll = false;
    return wrap;
  }

  function bindOverwriteSelect(el) {
    if (!el || el.getAttribute('data-kpi-location-overwrite') === '1') return;
    el.setAttribute('data-kpi-location-overwrite', '1');
    function onFocusOrClick(e) {
      if (e && e.target && e.target.classList && e.target.classList.contains('profile-location-toggle')) {
        return;
      }
      selectValueIfPresent(el);
    }
    el.addEventListener('focus', onFocusOrClick);
    el.addEventListener('click', onFocusOrClick);
  }

  function bindCandidateField(el, opts) {
    /* KPI-PROFILE-LOCATION-CANDIDATE-DROPDOWN */
    opts = opts || {};
    if (!el || el.getAttribute('data-kpi-location-dropdown') === '1') {
      if (el && el._kpiLoc && typeof opts.getLabels === 'function') {
        el._kpiLoc.getLabels = opts.getLabels;
      }
      return;
    }
    ensureCandidateChrome(el);
    el.setAttribute('data-kpi-location-dropdown', '1');
    el._kpiLoc.getLabels = typeof opts.getLabels === 'function' ? opts.getLabels : function () { return []; };

    bindOverwriteSelect(el);

    var btn = el._kpiLoc.btn;
    btn.addEventListener('mousedown', function (e) {
      e.preventDefault();
      e.stopPropagation();
    });
    btn.addEventListener('click', function (e) {
      e.preventDefault();
      e.stopPropagation();
      var open = el._kpiLoc.menu && !el._kpiLoc.menu.hidden && el._kpiLoc.showAll;
      if (open) {
        closeCandidateMenu(el);
        return;
      }
      openCandidateMenu(el, { showAll: true });
      try {
        el.focus();
      } catch (_e) {}
    });

    el.addEventListener('input', function () {
      openCandidateMenu(el, { showAll: false });
    });

    el.addEventListener('keydown', function (e) {
      var menu = el._kpiLoc.menu;
      var isOpen = menu && !menu.hidden;
      if (e.key === 'Escape') {
        if (isOpen) {
          e.preventDefault();
          closeCandidateMenu(el);
        }
        return;
      }
      if (e.key === 'ArrowDown') {
        e.preventDefault();
        if (!isOpen) openCandidateMenu(el, { showAll: !String(el.value || '').trim() });
        else setActiveCandidate(el, (el._kpiLoc.activeIndex < 0 ? 0 : el._kpiLoc.activeIndex + 1));
        return;
      }
      if (e.key === 'ArrowUp') {
        if (!isOpen) return;
        e.preventDefault();
        setActiveCandidate(el, (el._kpiLoc.activeIndex < 0 ? 0 : el._kpiLoc.activeIndex - 1));
        return;
      }
      if (e.key === 'Enter' && isOpen && el._kpiLoc.activeIndex >= 0) {
        var items = menu.querySelectorAll('.profile-location-option');
        var active = items[el._kpiLoc.activeIndex];
        if (active) {
          e.preventDefault();
          pickCandidate(el, active.getAttribute('data-value') || active.textContent);
        }
      }
    });

    el.addEventListener('blur', function () {
      setTimeout(function () {
        if (!el._kpiLoc || !el._kpiLoc.wrap) return;
        var active = document.activeElement;
        if (active && el._kpiLoc.wrap.contains(active)) return;
        closeCandidateMenu(el);
      }, 120);
    });
  }

  function bindLocationOverwrite() {
    if (!global.document) return;
    ['profile-country', 'profile-state', 'profile-city'].forEach(function (id) {
      var el = document.getElementById(id);
      if (!el) return;
      if (el.getAttribute('data-kpi-location-dropdown') === '1') return;
      bindOverwriteSelect(el);
    });
  }

  if (global.document) {
    document.addEventListener('mousedown', function (e) {
      if (!_openMenus.length) return;
      var t = e.target;
      _openMenus.slice().forEach(function (el) {
        if (el._kpiLoc && el._kpiLoc.wrap && el._kpiLoc.wrap.contains(t)) return;
        closeCandidateMenu(el);
      });
    });
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', bindLocationOverwrite);
    } else {
      bindLocationOverwrite();
    }
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
    timezoneForCountry: timezoneForCountry,
    browserTimezone: browserTimezone,
    resolveTimezone: resolveTimezone,
    fillDatalist: fillDatalist,
    findState: findState,
    findCity: findCity,
    selectValueIfPresent: selectValueIfPresent,
    bindOverwriteSelect: bindOverwriteSelect,
    bindLocationOverwrite: bindLocationOverwrite,
    filterCandidateLabels: filterCandidateLabels,
    bindCandidateField: bindCandidateField,
    openCandidateMenu: openCandidateMenu,
    closeCandidateMenu: closeCandidateMenu,
    closeAllCandidateMenus: closeAllCandidateMenus
  };
})(typeof window !== 'undefined' ? window : this);
