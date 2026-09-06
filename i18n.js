// Lightweight, dependency-free English/Korean interface localization.
// Text rendered later by ui.js is translated by the MutationObserver as well.
(function () {
  "use strict";

  const exact = new Map(Object.entries({
    "South Korea": "대한민국",
    "Korean": "한국어",
    "Search a place, city, or region…": "장소, 도시 또는 지역 검색…",
    "Language for the accessibility estimate": "접근성 추정 및 인터페이스 언어",
    "Zoom in": "확대",
    "Zoom out": "축소",
    "Reset view": "보기 초기화",
    "About & research": "소개 및 연구",
    "Explore the map": "지도 둘러보기",
    "🔊 Sound navigation": "🔊 소리 탐색",
    "Click a province to explore places": "지역을 클릭해 장소를 둘러보세요",
    "Hover over a province to preview its vibe.": "지역 위에 마우스를 올려 분위기를 미리 확인하세요.",
    "Click to explore places.": "클릭하여 장소를 둘러보세요.",
    "Click to dive into places.": "클릭하여 장소를 자세히 둘러보세요.",
    "Mood atmosphere": "분위기",
    "Peaceful": "평온함",
    "Exciting": "활기참",
    "Activity": "활동성",
    "Language accessibility": "언어 접근성",
    "The vibe, in words": "글로 표현한 분위기",
    "Places to explore": "둘러볼 장소",
    "See data and calculation": "데이터와 계산 보기",
    "Modelled proxy": "모델링된 추정치",
    "How this became music": "이 장소가 음악이 된 방식",
    "Generated soundscape": "생성된 사운드스케이프",
    "Play/pause": "재생/일시정지",
    "About & Research — Moodscape": "소개 및 연구 — Moodscape",
    "Feeling Korea Through Sound": "소리로 느끼는 한국",
    "Research question": "연구 질문",
    "Why sonification": "왜 소리로 표현할까요?",
    "The sonification algorithm": "소리 변환 알고리즘",
    "What's actually running vs. what's proposed.": "현재 구현된 기능과 제안 단계의 기능",
    "Sources": "출처",
    "Back": "뒤로",
    "No data yet": "아직 데이터가 없습니다",
    "Major": "장조",
    "Minor": "단조",
    "Calm": "차분함",
    "Balanced": "균형 잡힘",
    "Lively": "활기참",
    "Saved ✓": "저장됨 ✓",
    "Seoul": "서울",
    "Busan": "부산",
    "Daegu": "대구",
    "Incheon": "인천",
    "Gwangju": "광주",
    "Daejeon": "대전",
    "Ulsan": "울산",
    "Sejongsi": "세종",
    "Gyeonggi-do": "경기도",
    "Gangwon": "강원도",
    "Chungcheongbuk-do": "충청북도",
    "Chungcheongnam-do": "충청남도",
    "Jeollabuk-do": "전북특별자치도",
    "Jeollanam-do": "전라남도",
    "Gyeongsangbuk-do": "경상북도",
    "Gyeongsangnam-do": "경상남도",
    "Jeju-do": "제주특별자치도"
  }));

  const patterns = [
    [/^Back to (.+)$/, "$1(으)로 돌아가기"],
    [/^Modelled activity — (.+)$/, "모델링된 활동성 — $1"],
    [/^Estimate (.+) accessibility via AI$/, "AI로 $1 접근성 추정하기"],
    [/^Estimating (.+) accessibility for (.+)…$/, "$2의 $1 접근성을 추정하는 중…"],
    [/^(.+) activity proxy · (.+) visitor pleasantness context$/, "활동성 추정치 $1 · 방문객 만족도 참고치 $2"],
    [/^Density \(35%\)$/, "인구 밀도 (35%)"],
    [/^Tourism intensity \(30%\)$/, "관광 강도 (30%)"],
    [/^Noise complaints \(15%\)$/, "소음 민원 (15%)"],
    [/^Noise facilities \(10%\)$/, "소음 배출 시설 (10%)"],
    [/^Crowding pressure \(10%\)$/, "혼잡 압력 (10%)"]
  ];

  const languageCodes = {
    English: "en", Korean: "ko", "Mandarin Chinese": "zh-CN", Japanese: "ja",
    Spanish: "es", French: "fr", German: "de", Vietnamese: "vi", Russian: "ru",
    Arabic: "ar", Hindi: "hi", Portuguese: "pt", Thai: "th"
  };

  // Core navigation and interactive controls for every language offered by the picker.
  // Korean has the larger dictionary above; these maps cover the shared live interface.
  const coreTranslations = {
    "zh-CN": {"South Korea":"韩国","About & research":"关于与研究","Explore the map":"探索地图","🔊 Sound navigation":"🔊 声音导航","Click a province to explore places":"点击省份探索地点","Mood atmosphere":"氛围","Peaceful":"宁静","Exciting":"活跃","Activity":"活跃度","Language accessibility":"语言无障碍程度","The vibe, in words":"文字描述的氛围","Places to explore":"可探索地点","See data and calculation":"查看数据和计算","Modelled proxy":"模型估算值","How this became music":"这里如何化为音乐","Generated soundscape":"生成的声音景观","Search a place, city, or region…":"搜索地点、城市或地区…","Zoom in":"放大","Zoom out":"缩小","Reset view":"重置视图","Sources":"来源"},
    ja: {"South Korea":"韓国","About & research":"概要と研究","Explore the map":"地図を見る","🔊 Sound navigation":"🔊 サウンドナビ","Click a province to explore places":"地域をクリックして場所を探索","Mood atmosphere":"雰囲気","Peaceful":"穏やか","Exciting":"活気","Activity":"活動度","Language accessibility":"言語アクセシビリティ","The vibe, in words":"言葉で表す雰囲気","Places to explore":"探索する場所","See data and calculation":"データと計算を見る","Modelled proxy":"モデル推定値","How this became music":"音楽になった仕組み","Generated soundscape":"生成されたサウンドスケープ","Search a place, city, or region…":"場所、都市、地域を検索…","Zoom in":"拡大","Zoom out":"縮小","Reset view":"表示をリセット","Sources":"出典"},
    es: {"South Korea":"Corea del Sur","About & research":"Acerca de e investigación","Explore the map":"Explorar el mapa","🔊 Sound navigation":"🔊 Navegación sonora","Click a province to explore places":"Haz clic en una provincia para explorar","Mood atmosphere":"Atmósfera","Peaceful":"Tranquilo","Exciting":"Emocionante","Activity":"Actividad","Language accessibility":"Accesibilidad lingüística","The vibe, in words":"El ambiente, en palabras","Places to explore":"Lugares para explorar","See data and calculation":"Ver datos y cálculo","Modelled proxy":"Estimación modelada","How this became music":"Cómo se convirtió en música","Generated soundscape":"Paisaje sonoro generado","Search a place, city, or region…":"Buscar un lugar, ciudad o región…","Zoom in":"Acercar","Zoom out":"Alejar","Reset view":"Restablecer vista","Sources":"Fuentes"},
    fr: {"South Korea":"Corée du Sud","About & research":"À propos et recherche","Explore the map":"Explorer la carte","🔊 Sound navigation":"🔊 Navigation sonore","Click a province to explore places":"Cliquez sur une province pour explorer","Mood atmosphere":"Atmosphère","Peaceful":"Paisible","Exciting":"Dynamique","Activity":"Activité","Language accessibility":"Accessibilité linguistique","The vibe, in words":"L'ambiance, en mots","Places to explore":"Lieux à explorer","See data and calculation":"Voir les données et le calcul","Modelled proxy":"Estimation modélisée","How this became music":"Comment ce lieu est devenu musique","Generated soundscape":"Paysage sonore généré","Search a place, city, or region…":"Rechercher un lieu, une ville ou une région…","Zoom in":"Zoom avant","Zoom out":"Zoom arrière","Reset view":"Réinitialiser la vue","Sources":"Sources"},
    de: {"South Korea":"Südkorea","About & research":"Über das Projekt und Forschung","Explore the map":"Karte erkunden","🔊 Sound navigation":"🔊 Klangnavigation","Click a province to explore places":"Region anklicken und Orte erkunden","Mood atmosphere":"Atmosphäre","Peaceful":"Ruhig","Exciting":"Lebhaft","Activity":"Aktivität","Language accessibility":"Sprachliche Zugänglichkeit","The vibe, in words":"Die Stimmung in Worten","Places to explore":"Orte zum Erkunden","See data and calculation":"Daten und Berechnung ansehen","Modelled proxy":"Modellierte Schätzung","How this became music":"Wie daraus Musik wurde","Generated soundscape":"Erzeugte Klanglandschaft","Search a place, city, or region…":"Ort, Stadt oder Region suchen…","Zoom in":"Vergrößern","Zoom out":"Verkleinern","Reset view":"Ansicht zurücksetzen","Sources":"Quellen"},
    vi: {"South Korea":"Hàn Quốc","About & research":"Giới thiệu và nghiên cứu","Explore the map":"Khám phá bản đồ","🔊 Sound navigation":"🔊 Điều hướng bằng âm thanh","Click a province to explore places":"Nhấp vào một tỉnh để khám phá","Mood atmosphere":"Bầu không khí","Peaceful":"Yên bình","Exciting":"Sôi động","Activity":"Mức độ hoạt động","Language accessibility":"Khả năng tiếp cận ngôn ngữ","The vibe, in words":"Không khí qua lời kể","Places to explore":"Địa điểm khám phá","See data and calculation":"Xem dữ liệu và tính toán","Modelled proxy":"Ước tính mô hình","How this became music":"Cách nơi này trở thành âm nhạc","Generated soundscape":"Cảnh quan âm thanh được tạo","Search a place, city, or region…":"Tìm địa điểm, thành phố hoặc vùng…","Zoom in":"Phóng to","Zoom out":"Thu nhỏ","Reset view":"Đặt lại chế độ xem","Sources":"Nguồn"},
    ru: {"South Korea":"Южная Корея","About & research":"О проекте и исследования","Explore the map":"Открыть карту","🔊 Sound navigation":"🔊 Звуковая навигация","Click a province to explore places":"Нажмите на регион, чтобы изучить места","Mood atmosphere":"Атмосфера","Peaceful":"Спокойно","Exciting":"Оживлённо","Activity":"Активность","Language accessibility":"Языковая доступность","The vibe, in words":"Атмосфера в словах","Places to explore":"Места для изучения","See data and calculation":"Данные и расчёт","Modelled proxy":"Модельная оценка","How this became music":"Как это стало музыкой","Generated soundscape":"Созданный звуковой ландшафт","Search a place, city, or region…":"Поиск места, города или региона…","Zoom in":"Увеличить","Zoom out":"Уменьшить","Reset view":"Сбросить вид","Sources":"Источники"},
    ar: {"South Korea":"كوريا الجنوبية","About & research":"حول المشروع والبحث","Explore the map":"استكشف الخريطة","🔊 Sound navigation":"🔊 التنقل بالصوت","Click a province to explore places":"انقر على منطقة لاستكشاف الأماكن","Mood atmosphere":"الأجواء","Peaceful":"هادئ","Exciting":"نابض بالحياة","Activity":"النشاط","Language accessibility":"إمكانية الوصول اللغوي","The vibe, in words":"الأجواء بالكلمات","Places to explore":"أماكن للاستكشاف","See data and calculation":"عرض البيانات والحساب","Modelled proxy":"تقدير بالنموذج","How this became music":"كيف تحول هذا إلى موسيقى","Generated soundscape":"مشهد صوتي مولّد","Search a place, city, or region…":"ابحث عن مكان أو مدينة أو منطقة…","Zoom in":"تكبير","Zoom out":"تصغير","Reset view":"إعادة ضبط العرض","Sources":"المصادر"},
    hi: {"South Korea":"दक्षिण कोरिया","About & research":"परिचय और शोध","Explore the map":"मानचित्र देखें","🔊 Sound navigation":"🔊 ध्वनि नेविगेशन","Click a province to explore places":"स्थान देखने के लिए प्रदेश चुनें","Mood atmosphere":"माहौल","Peaceful":"शांत","Exciting":"रोमांचक","Activity":"गतिविधि","Language accessibility":"भाषाई सुगम्यता","The vibe, in words":"शब्दों में माहौल","Places to explore":"देखने योग्य स्थान","See data and calculation":"डेटा और गणना देखें","Modelled proxy":"मॉडल आधारित अनुमान","How this became music":"यह संगीत कैसे बना","Generated soundscape":"निर्मित ध्वनि-परिदृश्य","Search a place, city, or region…":"स्थान, शहर या क्षेत्र खोजें…","Zoom in":"ज़ूम इन","Zoom out":"ज़ूम आउट","Reset view":"दृश्य रीसेट करें","Sources":"स्रोत"},
    pt: {"South Korea":"Coreia do Sul","About & research":"Sobre e pesquisa","Explore the map":"Explorar o mapa","🔊 Sound navigation":"🔊 Navegação sonora","Click a province to explore places":"Clique numa província para explorar","Mood atmosphere":"Atmosfera","Peaceful":"Tranquilo","Exciting":"Animado","Activity":"Atividade","Language accessibility":"Acessibilidade linguística","The vibe, in words":"O ambiente, em palavras","Places to explore":"Lugares para explorar","See data and calculation":"Ver dados e cálculo","Modelled proxy":"Estimativa modelada","How this became music":"Como isto se tornou música","Generated soundscape":"Paisagem sonora gerada","Search a place, city, or region…":"Pesquisar lugar, cidade ou região…","Zoom in":"Ampliar","Zoom out":"Reduzir","Reset view":"Redefinir vista","Sources":"Fontes"},
    th: {"South Korea":"เกาหลีใต้","About & research":"เกี่ยวกับและงานวิจัย","Explore the map":"สำรวจแผนที่","🔊 Sound navigation":"🔊 การนำทางด้วยเสียง","Click a province to explore places":"คลิกจังหวัดเพื่อสำรวจสถานที่","Mood atmosphere":"บรรยากาศ","Peaceful":"สงบ","Exciting":"คึกคัก","Activity":"กิจกรรม","Language accessibility":"การเข้าถึงด้านภาษา","The vibe, in words":"บรรยากาศในคำพูด","Places to explore":"สถานที่น่าสำรวจ","See data and calculation":"ดูข้อมูลและการคำนวณ","Modelled proxy":"ค่าประมาณจากแบบจำลอง","How this became music":"สิ่งนี้กลายเป็นดนตรีได้อย่างไร","Generated soundscape":"ภูมิทัศน์เสียงที่สร้างขึ้น","Search a place, city, or region…":"ค้นหาสถานที่ เมือง หรือภูมิภาค…","Zoom in":"ขยาย","Zoom out":"ย่อ","Reset view":"รีเซ็ตมุมมอง","Sources":"แหล่งที่มา"}
  };

  const emptyStateTranslations = {
    ko: {"Hover over a province to preview its vibe.":"지역 위에 마우스를 올려 분위기를 미리 확인하세요.","Click to explore places.":"클릭하여 장소를 둘러보세요.","Click to dive into places.":"클릭하여 장소를 자세히 둘러보세요."},
    "zh-CN": {"Hover over a province to preview its vibe.":"将鼠标悬停在省份上以预览其氛围。","Click to explore places.":"点击以探索地点。","Click to dive into places.":"点击深入探索地点。"},
    ja: {"Hover over a province to preview its vibe.":"地域にカーソルを合わせると雰囲気を確認できます。","Click to explore places.":"クリックして場所を探索してください。","Click to dive into places.":"クリックして場所を詳しく探索してください。"},
    es: {"Hover over a province to preview its vibe.":"Pasa el cursor sobre una provincia para ver su ambiente.","Click to explore places.":"Haz clic para explorar lugares.","Click to dive into places.":"Haz clic para explorar los lugares en detalle."},
    fr: {"Hover over a province to preview its vibe.":"Survolez une province pour découvrir son ambiance.","Click to explore places.":"Cliquez pour explorer les lieux.","Click to dive into places.":"Cliquez pour explorer les lieux en détail."},
    de: {"Hover over a province to preview its vibe.":"Bewege den Mauszeiger über eine Region, um ihre Stimmung zu sehen.","Click to explore places.":"Klicke, um Orte zu erkunden.","Click to dive into places.":"Klicke, um Orte genauer zu erkunden."},
    vi: {"Hover over a province to preview its vibe.":"Di chuột qua một tỉnh để xem trước không khí.","Click to explore places.":"Nhấp để khám phá các địa điểm.","Click to dive into places.":"Nhấp để khám phá địa điểm chi tiết hơn."},
    ru: {"Hover over a province to preview its vibe.":"Наведите курсор на регион, чтобы увидеть его атмосферу.","Click to explore places.":"Нажмите, чтобы изучить места.","Click to dive into places.":"Нажмите, чтобы подробнее изучить места."},
    ar: {"Hover over a province to preview its vibe.":"مرّر المؤشر فوق منطقة لمعاينة أجوائها.","Click to explore places.":"انقر لاستكشاف الأماكن.","Click to dive into places.":"انقر لاستكشاف الأماكن بالتفصيل."},
    hi: {"Hover over a province to preview its vibe.":"किसी प्रदेश का माहौल देखने के लिए उस पर कर्सर रखें।","Click to explore places.":"स्थानों को देखने के लिए क्लिक करें।","Click to dive into places.":"स्थानों को विस्तार से देखने के लिए क्लिक करें।"},
    pt: {"Hover over a province to preview its vibe.":"Passe o cursor sobre uma província para ver o seu ambiente.","Click to explore places.":"Clique para explorar lugares.","Click to dive into places.":"Clique para explorar os lugares em detalhe."},
    th: {"Hover over a province to preview its vibe.":"เลื่อนเมาส์เหนือจังหวัดเพื่อดูบรรยากาศ","Click to explore places.":"คลิกเพื่อสำรวจสถานที่","Click to dive into places.":"คลิกเพื่อสำรวจสถานที่โดยละเอียด"}
  };

  const originals = new WeakMap();
  let current = "en";
  let observer;
  let translationQueue = [];
  let translationTimer;
  let translationGeneration = 0;
  const translationCache = {};

  function cachedTranslation(language, source) {
    if (!translationCache[language]) {
      try {
        translationCache[language] = JSON.parse(localStorage.getItem("moodscape_full_translation_" + language) || "{}");
      } catch (e) { translationCache[language] = {}; }
    }
    return translationCache[language][source];
  }

  function saveCachedTranslation(language, source, result) {
    if (!translationCache[language]) translationCache[language] = {};
    translationCache[language][source] = result;
    try {
      localStorage.setItem("moodscape_full_translation_" + language, JSON.stringify(translationCache[language]));
    } catch (e) {}
  }

  function queueFullTranslation(node, source) {
    const cached = cachedTranslation(current, source);
    if (cached) {
      node.nodeValue = node.nodeValue.replace(node.nodeValue.trim(), cached);
      return;
    }
    const language = current;
    translationQueue.push({
      source, language, generation: translationGeneration,
      apply(result) {
        if (node.isConnected && current === language && originals.get(node).trim() === source) {
          node.nodeValue = node.nodeValue.replace(node.nodeValue.trim(), result);
          markUntranslated(node, false);
        }
      }
    });
    clearTimeout(translationTimer);
    translationTimer = setTimeout(flushTranslationQueue, 30);
  }

  function queueAttributeTranslation(el, attr, source) {
    const cached = cachedTranslation(current, source);
    if (cached) { el.setAttribute(attr, cached); return; }
    const language = current;
    translationQueue.push({
      source, language, generation: translationGeneration,
      apply(result) {
        if (el.isConnected && current === language) el.setAttribute(attr, result);
      }
    });
    clearTimeout(translationTimer);
    translationTimer = setTimeout(flushTranslationQueue, 30);
  }

  function queueTitleTranslation(source) {
    const cached = cachedTranslation(current, source);
    if (cached) { document.title = cached; return; }
    const language = current;
    translationQueue.push({
      source, language, generation: translationGeneration,
      apply(result) { if (current === language) document.title = result; }
    });
    clearTimeout(translationTimer);
    translationTimer = setTimeout(flushTranslationQueue, 30);
  }

  async function translateBatch(items) {
    const language = items[0].language;
    const payload = items.map((item, index) => `\uE000${index}\uE001${item.source}`).join("\n");
    const url = "https://translate.googleapis.com/translate_a/single?client=gtx&sl=en&tl="
      + encodeURIComponent(language) + "&dt=t&q=" + encodeURIComponent(payload);
    const response = await fetch(url);
    if (!response.ok) throw new Error("Translation request failed");
    const data = await response.json();
    const translatedPayload = (data[0] || []).map(part => part[0] || "").join("");
    const results = [];
    const matcher = /\uE000(\d+)\uE001([\s\S]*?)(?=\uE000\d+\uE001|$)/g;
    let match;
    while ((match = matcher.exec(translatedPayload))) results[Number(match[1])] = match[2].trim();
    return results;
  }

  async function flushTranslationQueue() {
    const queued = translationQueue;
    translationQueue = [];
    const groups = [];
    let group = [];
    let size = 0;
    queued.forEach(item => {
      if (item.language !== current || item.generation !== translationGeneration) return;
      if (group.length && size + item.source.length > 3500) {
        groups.push(group); group = []; size = 0;
      }
      group.push(item); size += item.source.length + 8;
    });
    if (group.length) groups.push(group);

    // A small amount of parallelism keeps long pages responsive without flooding
    // the translation service with one request per paragraph.
    for (let offset = 0; offset < groups.length; offset += 3) {
      await Promise.all(groups.slice(offset, offset + 3).map(async items => {
        try {
          const results = await translateBatch(items);
          items.forEach((item, index) => {
            const result = results[index];
            if (!result) return;
            saveCachedTranslation(item.language, item.source, result);
            item.apply(result);
          });
        } catch (e) {
          // Keep the original text if the visitor is offline. A later language
          // change retries it, while all built-in interface labels still work.
        }
      }));
    }
  }

  function translated(value) {
    const trimmed = value.trim();
    const dictionary = current === "ko" ? exact : coreTranslations[current];
    const emptyDictionary = emptyStateTranslations[current];
    const replacement = (dictionary instanceof Map ? dictionary.get(trimmed) : dictionary && dictionary[trimmed])
      || (emptyDictionary && emptyDictionary[trimmed]);
    if (replacement) return value.replace(trimmed, replacement);
    if (current === "ko") for (const [pattern, patternReplacement] of patterns) {
      if (pattern.test(trimmed)) return value.replace(trimmed, trimmed.replace(pattern, patternReplacement));
    }
    return value;
  }

  // Screen readers pick a voice from the nearest lang attribute. Untranslated
  // English text inside a ko/ja/ar document would otherwise be read by that
  // language's voice, which is unintelligible. Marking it lang="en" makes the
  // reader switch voices for exactly the runs that are still English.
  function markUntranslated(node, isStillEnglish) {
    const el = node.parentElement;
    if (!el) return;
    if (current === "en") {
      if (el.dataset.i18nLangMark) {
        el.removeAttribute("lang");
        delete el.dataset.i18nLangMark;
      }
      return;
    }
    // Both cases are asserted explicitly. Marking only the English runs would
    // let a mixed container (a translated label beside an untranslated
    // paragraph) pass lang="en" down to the label by inheritance, so a
    // translated element states its own language too.
    const value = isStillEnglish ? "en" : current;
    if (!el.hasAttribute("lang") || el.dataset.i18nLangMark) {
      el.setAttribute("lang", value);
      el.dataset.i18nLangMark = "1";
    }
  }

  function translateTextNode(node) {
    if (!node.nodeValue || !node.nodeValue.trim()) return;
    if (!originals.has(node)) originals.set(node, node.nodeValue);
    const source = originals.get(node);
    if (current === "en") {
      node.nodeValue = source;
      markUntranslated(node, false);
      return;
    }
    const immediate = translated(source);
    node.nodeValue = immediate;
    markUntranslated(node, immediate === source);
    if (immediate === source) queueFullTranslation(node, source.trim());
  }

  function translateElement(el) {
    if (!(el instanceof Element)) return;
    const attrs = ["placeholder", "title", "aria-label"];
    attrs.forEach(attr => {
      if (!el.hasAttribute(attr)) return;
      const key = "i18nOriginal" + attr.replace(/-([a-z])/g, (_, c) => c.toUpperCase());
      if (!el.dataset[key]) el.dataset[key] = el.getAttribute(attr);
      const source = el.dataset[key];
      if (current === "en") {
        el.setAttribute(attr, source);
      } else {
        const immediate = translated(source);
        el.setAttribute(attr, immediate);
        if (immediate === source) queueAttributeTranslation(el, attr, source);
      }
    });
    for (const node of el.childNodes) {
      if (node.nodeType === Node.TEXT_NODE) translateTextNode(node);
      else if (node.nodeType === Node.ELEMENT_NODE) translateElement(node);
    }
  }

  function apply() {
    if (!document.body) return;
    if (observer) observer.disconnect();
    document.documentElement.lang = current;
    document.documentElement.dir = current === "ar" ? "rtl" : "ltr";
    if (!document.documentElement.dataset.i18nOriginalTitle) {
      document.documentElement.dataset.i18nOriginalTitle = document.title;
    }
    const originalTitle = document.documentElement.dataset.i18nOriginalTitle;
    if (current === "en") {
      document.title = originalTitle;
    } else {
      document.title = translated(originalTitle);
      if (document.title === originalTitle) queueTitleTranslation(originalTitle);
    }
    translateElement(document.body);
    if (observer) observer.observe(document.body, { childList: true, subtree: true });
  }

  window.setInterfaceLanguage = function (language) {
    current = languageCodes[language] || languageCodes.English;
    translationGeneration += 1;
    translationQueue = [];
    clearTimeout(translationTimer);
    try { localStorage.setItem("moodscape_interface_language", current); } catch (e) {}
    apply();
  };

  document.addEventListener("DOMContentLoaded", function () {
    observer = new MutationObserver(mutations => {
      if (current === "en") return;
      observer.disconnect();
      mutations.forEach(m => m.addedNodes.forEach(node => {
        if (node.nodeType === Node.TEXT_NODE) translateTextNode(node);
        else if (node.nodeType === Node.ELEMENT_NODE) translateElement(node);
      }));
      observer.observe(document.body, { childList: true, subtree: true });
    });
    let saved = "en";
    try {
      const config = JSON.parse(localStorage.getItem("moodscape_language") || "{}");
      saved = languageCodes[config.language] || "en";
    } catch (e) {}
    current = saved;
    apply();

    // Bind directly as well as supporting the HTML callback. This makes the
    // visible interface update in the same event that changes the selection.
    const selector = document.getElementById("header-lang-select");
    if (selector) {
      selector.addEventListener("change", function () {
        window.setInterfaceLanguage(this.value);
      });
    }
  });
})();
