// ── MOOD SCAPE DATA ──────────────────────────────────────────────────────────

let currentState = null;
let currentPlace = null;
let currentPlaceState = null;
let isPlaying = false;
let chatHistory = {}; // Store chat logs per place: { "seoul__hongdae": [{role: "user"/"local", text: "..."}] }
const waveHeights = [0.3,0.6,0.8,0.5,0.9,0.4,0.7,0.5,0.6,0.8,0.3,0.7,0.9,0.4,0.6,0.5,0.8,0.7,0.3,0.6];

const MOOD_DATA = {
  states: {
    "Seoul": { score: 0.85, emoji: "🏙️", desc: "Capital since 1394 — sourced vibrant, high-energy soundscape", hiddenGem: { name: "Oil Tank Culture Park", note: "A decommissioned 1970s oil depot in Mapo-gu, its five tanks converted into galleries and performance spaces most visitors never hear about.", quote: "The park's industrial aesthetic, with its massive tanks now serving as art spaces and performance venues, makes it one of the most unique hidden gems in Seoul.", source: "Linda Goes East", sourceUrl: "https://lindagoeseast.com/2024/09/15/discover-hidden-gems-in-seoul/" }, places: [
      { name: "Hongdae", score: 0.94, type: "Youth & arts district", emoji: "🎨", instrumentation: "K-indie basslines, warehouse techno, street busker guitar", character: "a packed university nightlife district with buskers and pop-up galleries at midnight", photo: "https://upload.wikimedia.org/wikipedia/commons/d/db/Street_hongdae_Seoul.jpg", photoArtist: "U0894629", photoLicense: "CC BY-SA 4.0", photoPage: "https://en.wikipedia.org/wiki/Hongdae_(area)", mapsUrl: "https://www.google.com/maps/search/?api=1&query=Hongdae%2C%20Seoul%2C%20South%20Korea", photos: [
        { url: "https://upload.wikimedia.org/wikipedia/commons/e/e9/Hongdae_Party_District_at_Night%2C_Seoul.jpg", artist: "Ken Eckert", license: "CC BY-SA 4.0", page: "https://commons.wikimedia.org/wiki/File:Hongdae_Party_District_at_Night,_Seoul.jpg" },
        { url: "https://upload.wikimedia.org/wikipedia/commons/f/fd/Hongdae_Main_Road%2C_Seoul.jpg", artist: "Ken Eckert", license: "CC BY-SA 4.0", page: "https://commons.wikimedia.org/wiki/File:Hongdae_Main_Road,_Seoul.jpg" }
      ] },
      { name: "Gyeongbokgung Palace", score: 0.22, type: "Historic royal palace", emoji: "🏯", instrumentation: "ceremonial court music, stone courtyard reverb, temple bell", character: "a 14th-century royal palace at dawn, guards changing in ceremonial silence", photo: "https://upload.wikimedia.org/wikipedia/commons/thumb/6/63/%EA%B4%91%ED%99%94%EB%AC%B8_%EC%9B%94%EB%8C%80.jpg/3840px-%EA%B4%91%ED%99%94%EB%AC%B8_%EC%9B%94%EB%8C%80.jpg", photoArtist: "", photoLicense: "", photoPage: "https://en.wikipedia.org/wiki/Gyeongbokgung", mapsUrl: "https://www.google.com/maps/search/?api=1&query=Gyeongbokgung%20Palace%2C%20Seoul%2C%20South%20Korea", photos: [
        { url: "https://upload.wikimedia.org/wikipedia/commons/9/90/Gyeonghoeru_Pavilion_in_Gyeongbokgung_Palace.jpg", artist: "Hhk1201", license: "CC BY-SA 4.0", page: "https://commons.wikimedia.org/wiki/File:Gyeonghoeru_Pavilion_in_Gyeongbokgung_Palace.jpg" },
        { url: "https://upload.wikimedia.org/wikipedia/commons/f/f5/Gyeongbokgung_Palace_Changing_of_the_Guard_Ceremony_2019_%284%29.jpg", artist: "Ethan Doyle White", license: "CC BY-SA 4.0", page: "https://commons.wikimedia.org/wiki/File:Gyeongbokgung_Palace_Changing_of_the_Guard_Ceremony_2019_(4).jpg" }
      ] },
      { name: "Gangnam", score: 0.9, type: "Luxury & business hub", emoji: "💎", instrumentation: "glossy K-pop synth-pop, sidechain-pumped bass, glass-tower shimmer", character: "a glittering high-rise district of designer boutiques and rooftop bars", photo: "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a2/Teheran-ro_Yeongdong-daero_crossing_7.jpg/3840px-Teheran-ro_Yeongdong-daero_crossing_7.jpg", photoArtist: "", photoLicense: "", photoPage: "https://en.wikipedia.org/wiki/Gangnam_District", mapsUrl: "https://www.google.com/maps/search/?api=1&query=Gangnam%2C%20Seoul%2C%20South%20Korea", photos: [
        { url: "https://upload.wikimedia.org/wikipedia/commons/f/fe/Starfield_Library_COEX_20240218.jpg", artist: "Sean Young", license: "CC BY 4.0", page: "https://commons.wikimedia.org/wiki/File:Starfield_Library_COEX_20240218.jpg" },
        { url: "https://upload.wikimedia.org/wikipedia/commons/b/b5/Gangnam-daero_in_Seoul.jpg", artist: "Christophe95", license: "CC BY-SA 4.0", page: "https://commons.wikimedia.org/wiki/File:Gangnam-daero_in_Seoul.jpg" }
      ] },
      { name: "Bukchon Hanok Village", score: 0.18, type: "Traditional hanok village", emoji: "🏘️", instrumentation: "solo daegeum flute, dawn stillness, wooden windchime", character: "a 600-year-old hillside village of traditional wooden houses at sunrise", photo: "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2e/Bukchon_Hanok_Village_01.jpg/3840px-Bukchon_Hanok_Village_01.jpg", photoArtist: "", photoLicense: "", photoPage: "https://en.wikipedia.org/wiki/Bukchon_Hanok_Village", mapsUrl: "https://www.google.com/maps/search/?api=1&query=Bukchon%20Hanok%20Village%2C%20Seoul%2C%20South%20Korea", photos: [
        { url: "https://upload.wikimedia.org/wikipedia/commons/a/ab/Bukchon-ro_11-gil_street_with_hanok_houses_and_blue_sky_in_Bukchon_Hanok_Village_Seoul.jpg", artist: "Basile Morin", license: "CC BY-SA 4.0", page: "https://commons.wikimedia.org/wiki/File:Bukchon-ro_11-gil_street_with_hanok_houses_and_blue_sky_in_Bukchon_Hanok_Village_Seoul.jpg" },
        { url: "https://upload.wikimedia.org/wikipedia/commons/d/db/Bukchon-ro_11-gil_street_with_hanok_houses_at_sunrise_in_Bukchon_Hanok_Village_Seoul.jpg", artist: "Basile Morin", license: "CC BY-SA 4.0", page: "https://commons.wikimedia.org/wiki/File:Bukchon-ro_11-gil_street_with_hanok_houses_at_sunrise_in_Bukchon_Hanok_Village_Seoul.jpg" }
      ] },
      { name: "N Seoul Tower", score: 0.55, type: "Mountain-top observation tower", emoji: "🗼", instrumentation: "twinkling glockenspiel, distant city hum, cable-car cable creak", character: "a mountaintop tower over the whole skyline at night, love-locks glinting on the railing", photo: "https://upload.wikimedia.org/wikipedia/en/a/a6/NamsanTower_%28Cropped%29.jpeg", photoArtist: "", photoLicense: "", photoPage: "https://en.wikipedia.org/wiki/Namsan_Seoul_Tower", mapsUrl: "https://www.google.com/maps/search/?api=1&query=N%20Seoul%20Tower%2C%20Seoul%2C%20South%20Korea", photos: [
        { url: "https://upload.wikimedia.org/wikipedia/commons/0/0f/N_Seoul_Tower_Panorama_001.jpg", artist: "Spike", license: "CC BY-SA 4.0", page: "https://commons.wikimedia.org/wiki/File:N_Seoul_Tower_Panorama_001.jpg" },
        { url: "https://upload.wikimedia.org/wikipedia/commons/4/47/View_from_N_Seoul_Tower_at_night.jpg", artist: "Evilbish", license: "CC BY-SA 3.0", page: "https://commons.wikimedia.org/wiki/File:View_from_N_Seoul_Tower_at_night.jpg" }
      ] },
      { name: "Dongdaemun Design Plaza", score: 0.78, type: "Futuristic design landmark", emoji: "🛸", instrumentation: "sleek electronic pulse, LED-panel shimmer, fashion-week footsteps", character: "a curving titanium spaceship of a building hosting fashion shows and light-art festivals", photo: "https://upload.wikimedia.org/wikipedia/commons/8/8f/Dongdaemun_Design_Plaza_at_night%2C_Seoul%2C_Korea.jpg", photoArtist: "Eugene Lim", photoLicense: "CC BY 2.0", photoPage: "https://en.wikipedia.org/wiki/Dongdaemun_Design_Plaza", mapsUrl: "https://www.google.com/maps/search/?api=1&query=Dongdaemun%20Design%20Plaza%2C%20Seoul%2C%20South%20Korea", photos: [
        { url: "https://upload.wikimedia.org/wikipedia/commons/1/13/Dongdaemun_Design_Plaza_grass.jpg", artist: "Tristan Surtel", license: "CC BY-SA 4.0", page: "https://commons.wikimedia.org/wiki/File:Dongdaemun_Design_Plaza_grass.jpg" },
        { url: "https://upload.wikimedia.org/wikipedia/commons/3/30/Dongdaemun_Design_Plaza_-_DDP2369.jpg", artist: "lumoplank", license: "CC0 1.0", page: "https://commons.wikimedia.org/wiki/File:Dongdaemun_Design_Plaza_-_DDP2369.jpg" }
      ] }
    ]},
    "Busan": { score: 0.72, emoji: "🌊", desc: "2nd city, world's 6th-busiest port, festival energy", hiddenGem: { name: "Hocheon Cultural Village", note: "A quiet hillside village overlooked in favor of the far more famous Gamcheon Culture Village a few neighborhoods over.", quote: "One day, when I was looking for things to do in Busan, as I was running out of ideas quickly, I learned that Hocheon Cultural Village was a thing.", source: "Ashley Hajimirsadeghi", sourceUrl: "https://www.ashleyhajimirsadeghi.com/blog/hidden-gems-busan-south-korea" }, places: [
      { name: "Haeundae Beach", score: 0.8, type: "Beach & resort strip", emoji: "🏖️", instrumentation: "summer house music, seagulls, boardwalk crowd hum", character: "Korea's most famous beach backed by glittering resort towers in high summer", photo: "https://upload.wikimedia.org/wikipedia/commons/thumb/e/ea/Haeundae_Beach_May_2024.jpg/3840px-Haeundae_Beach_May_2024.jpg", photoArtist: "", photoLicense: "", photoPage: "https://en.wikipedia.org/wiki/Haeundae_Beach", mapsUrl: "https://www.google.com/maps/search/?api=1&query=Haeundae%20Beach%2C%20Busan%2C%20South%20Korea" },
      { name: "Gamcheon Culture Village", score: 0.55, type: "Hillside art village", emoji: "🎭", instrumentation: "lo-fi hip-hop, wind chimes, hillside echo", character: "a pastel hillside village stacked like a Korean Cinque Terre, murals on every wall", photo: "https://upload.wikimedia.org/wikipedia/commons/thumb/e/ee/Gamcheon_Houses%2C_2024.jpg/3840px-Gamcheon_Houses%2C_2024.jpg", photoArtist: "", photoLicense: "", photoPage: "https://en.wikipedia.org/wiki/Gamcheon_Culture_Village", mapsUrl: "https://www.google.com/maps/search/?api=1&query=Gamcheon%20Culture%20Village%2C%20Busan%2C%20South%20Korea" },
      { name: "Jagalchi Market", score: 0.68, type: "Fish market & harbor", emoji: "🐟", instrumentation: "vendor calls, gull cries, harbor engine drone, brass", character: "Korea's largest seafood market, boats unloading at dawn, vendors shouting prices", photo: "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d4/Jagalchi_Market_20200523_019.jpg/3840px-Jagalchi_Market_20200523_019.jpg", photoArtist: "", photoLicense: "", photoPage: "https://en.wikipedia.org/wiki/Jagalchi_Market", mapsUrl: "https://www.google.com/maps/search/?api=1&query=Jagalchi%20Market%2C%20Busan%2C%20South%20Korea" },
      { name: "Taejongdae", score: 0.35, type: "Cliffside coastal park", emoji: "🪨", instrumentation: "crashing waves, seabird cry, lighthouse foghorn", character: "sheer cliffs dropping into the sea, a lighthouse at the end of a pine-forest trail", photo: "https://upload.wikimedia.org/wikipedia/commons/4/47/Korea-Busan-Taejongdae-03.jpg", photoArtist: "*intacto", photoLicense: "CC BY 2.0", photoPage: "https://en.wikipedia.org/wiki/Taejongdae", mapsUrl: "https://www.google.com/maps/search/?api=1&query=Taejongdae%2C%20Busan%2C%20South%20Korea" },
      { name: "BIFF Square", score: 0.82, type: "Cinema & street-food district", emoji: "🎬", instrumentation: "sizzling street-food grill, film-reel clatter, neon marquee hum", character: "Busan's original film-festival district, street-food stalls sizzling under movie-star handprints", photo: "https://upload.wikimedia.org/wikipedia/commons/5/55/Nampo-Dong_Christmas_Lights_in_Busan.jpg", photoArtist: "Ken Eckert", photoLicense: "CC BY-SA 4.0", photoPage: "https://en.wikipedia.org/wiki/Nampo-dong", mapsUrl: "https://www.google.com/maps/search/?api=1&query=BIFF%20Square%20Nampo-dong%2C%20Busan%2C%20South%20Korea" }
    ]},
    "Daegu": { score: 0.6, emoji: "🌶️", desc: "Textile-and-apple city, balanced market rhythm", hiddenGem: { name: "Bangcheon Market", note: "A postwar refugee market turned mural-lined night street, still eclipsed by Seomun Market's fame.", quote: "While most tourists head to popular markets such as Gukchaebosang Memorial Park or Seomun Market, the locals' favorite remains the relatively unknown Bangcheon Market.", source: "Korea.net", sourceUrl: "https://www.korea.net/NewsFocus/FoodTravel/view?articleId=119067" }, places: [
      { name: "Seomun Market", score: 0.72, type: "Traditional night market", emoji: "🏮", instrumentation: "sizzling street-food percussion, festival drum, crowd chatter", character: "a 500-year-old night market of sizzling street food and lantern-lit stalls", photo: "https://upload.wikimedia.org/wikipedia/commons/f/fd/10%EA%B2%BD_%EC%84%9C%EB%AC%B8%EC%8B%9C%EC%9E%A5.jpg", photoArtist: "대구광역시", photoLicense: "CC BY-SA 4.0", photoPage: "https://en.wikipedia.org/wiki/Seomun_Market", mapsUrl: "https://www.google.com/maps/search/?api=1&query=Seomun%20Market%2C%20Daegu%2C%20South%20Korea" },
      { name: "Apsan Park", score: 0.3, type: "Mountain park & cable car", emoji: "🚡", instrumentation: "acoustic guitar, cicada drone, mountain wind", character: "a forested mountain park overlooking the city, cable cars gliding through pines", photo: "https://upload.wikimedia.org/wikipedia/commons/e/e0/Daegupanorama4.jpg", photoArtist: "", photoLicense: "CC BY-SA 3.0", photoPage: "https://en.wikipedia.org/wiki/Apsan_Park", mapsUrl: "https://www.google.com/maps/search/?api=1&query=Apsan%20Park%2C%20Daegu%2C%20South%20Korea" },
      { name: "Donghwasa Temple", score: 0.14, type: "Mountain Buddhist temple", emoji: "🛕", instrumentation: "temple bell, monk chant, pine-forest hush", character: "a mountain temple guarded by a towering stone Buddha, incense drifting through pine trees", photo: "https://upload.wikimedia.org/wikipedia/commons/5/59/Korea-Daegu-Donghwasa-01.jpg", photoArtist: "by martinroell", photoLicense: "CC BY-SA 2.0", photoPage: "https://en.wikipedia.org/wiki/Donghwasa", mapsUrl: "https://www.google.com/maps/search/?api=1&query=Donghwasa%20Temple%2C%20Daegu%2C%20South%20Korea" },
      { name: "E-World & Duryu Park", score: 0.75, type: "Amusement park & night tower", emoji: "🎡", instrumentation: "carnival ride chime, pop-fireworks crackle, Ferris-wheel motor hum", character: "an amusement park lighting up at dusk beneath a spinning observation tower", photo: "https://upload.wikimedia.org/wikipedia/commons/4/4d/11%EA%B2%BD_83%ED%83%80%EC%9B%8C.jpg", photoArtist: "대구광역시", photoLicense: "CC BY 4.0", photoPage: "https://commons.wikimedia.org/wiki/File:11경_83타워.jpg", mapsUrl: "https://www.google.com/maps/search/?api=1&query=E-World%20Duryu%20Park%2C%20Daegu%2C%20South%20Korea" }
    ]},
    "Incheon": { score: 0.62, emoji: "⚓", desc: "1883 port city split between Chinatown and Songdo", hiddenGem: { name: "Sudoguksan Museum of Housing and Living", note: "A recreated 1960s-70s Incheon neighborhood — homes, a barbershop, a corner store — tucked inside a municipal museum most tourists skip.", quote: "The exhibitions perfectly display life in Incheon in the 60s and 70s on two floors.", source: "Linda Goes East", sourceUrl: "https://lindagoeseast.com/2017/02/15/hidden-gems-incheon/" }, places: [
      { name: "Incheon Chinatown", score: 0.66, type: "Historic Chinatown", emoji: "🥟", instrumentation: "Chinese brass ensemble, sizzling wok percussion, harbor bell", character: "Korea's oldest Chinatown, red lanterns and the smell of jjajangmyeon at dusk", photo: "https://upload.wikimedia.org/wikipedia/commons/thumb/5/52/Chinatown%2C_incheon_20230430_002.jpg/3840px-Chinatown%2C_incheon_20230430_002.jpg", photoArtist: "", photoLicense: "", photoPage: "https://en.wikipedia.org/wiki/Incheon_Chinatown", mapsUrl: "https://www.google.com/maps/search/?api=1&query=Incheon%20Chinatown%2C%20Incheon%2C%20South%20Korea" },
      { name: "Songdo Central Park", score: 0.58, type: "Futuristic waterfront district", emoji: "🌆", instrumentation: "glassy ambient synth, canal water lapping, distant traffic hum", character: "a brand-new planned city of glass towers and seawater canals", photo: "https://upload.wikimedia.org/wikipedia/commons/thumb/2/24/South_Korea%2C_Incheon%2C_Songdo%2C_the_Sharp_Central_Park_Towers.jpg/3840px-South_Korea%2C_Incheon%2C_Songdo%2C_the_Sharp_Central_Park_Towers.jpg", photoArtist: "", photoLicense: "", photoPage: "https://en.wikipedia.org/wiki/Songdo", mapsUrl: "https://www.google.com/maps/search/?api=1&query=Songdo%20Central%20Park%2C%20Incheon%2C%20South%20Korea" },
      { name: "Wolmido", score: 0.5, type: "Amusement pier", emoji: "🎡", instrumentation: "carnival calliope, seagulls, tide bell", character: "an old-fashioned seaside amusement pier with a ferris wheel at sunset", photo: "https://upload.wikimedia.org/wikipedia/commons/f/fc/Walmido_promenade.jpg", photoArtist: "Goodwillgames", photoLicense: "CC BY-SA 4.0", photoPage: "https://en.wikipedia.org/wiki/Wolmido", mapsUrl: "https://www.google.com/maps/search/?api=1&query=Wolmido%2C%20Incheon%2C%20South%20Korea" },
      { name: "Ganghwa Dolmen Site", score: 0.1, type: "UNESCO prehistoric megalith site", emoji: "🪨", instrumentation: "stone-on-stone resonance, open-field wind, distant crow call", character: "5,000-year-old stone tombs standing alone in open farmland, older than the pyramids", photo: "https://upload.wikimedia.org/wikipedia/commons/9/9c/Ganghwa_Bugeun-ri_dolmen.jpg", photoArtist: "ChongDae", photoLicense: "CC BY-SA 3.0", photoPage: "https://commons.wikimedia.org/wiki/File:Ganghwa_Bugeun-ri_dolmen.jpg", mapsUrl: "https://www.google.com/maps/search/?api=1&query=Ganghwa%20Dolmen%20Site%2C%20Incheon%2C%20South%20Korea" },
      { name: "Jayu Park", score: 0.42, type: "Historic hilltop memorial park", emoji: "🎖️", instrumentation: "brass memorial fanfare, harbor foghorn, park-bench quiet", character: "a hilltop war-memorial park overlooking the harbor where the Incheon Landing began", photo: "https://upload.wikimedia.org/wikipedia/commons/e/e9/Jayu_Park_20230430_024.jpg", photoArtist: "Mobius6", photoLicense: "CC BY-SA 4.0", photoPage: "https://en.wikipedia.org/wiki/Jayu_Park", mapsUrl: "https://www.google.com/maps/search/?api=1&query=Jayu%20Park%2C%20Incheon%2C%20South%20Korea" }
    ]},
    "Gwangju": { score: 0.42, emoji: "🎨", desc: "Democratization memory beside Asia's oldest art biennale", hiddenGem: { name: "1913 Songjeong Station Market", note: "A century-old market that opened alongside its train station and still runs on that same everyday rhythm.", quote: "Originally built in 1913, the Songjeong Station market opened alongside the station itself.", source: "Carly in Korea", sourceUrl: "https://carlyinkorea.com/2023/01/19/ten-things-to-do-in-gwangju/" }, places: [
      { name: "Mudeungsan National Park", score: 0.15, type: "Granite-peak national park", emoji: "⛰️", instrumentation: "solo daegeum, pine wind, distant temple bell", character: "a granite-peaked mountain sacred to the city, pine forest and quiet trails", photo: "https://upload.wikimedia.org/wikipedia/commons/2/2d/Mt_Mudeungsan_-_panoramio.jpg", photoArtist: "gary4now", photoLicense: "CC BY 3.0", photoPage: "https://en.wikipedia.org/wiki/Mudeungsan", mapsUrl: "https://www.google.com/maps/search/?api=1&query=Mudeungsan%20National%20Park%2C%20Gwangju%2C%20South%20Korea" },
      { name: "Yangnim-dong", score: 0.38, type: "Historic art & missionary quarter", emoji: "🖼️", instrumentation: "muted trumpet, rain on tile roofs, sparse piano", character: "a century-old hillside quarter of missionary houses turned into galleries", photo: "https://upload.wikimedia.org/wikipedia/commons/4/45/Gwangju_montage.png", photoArtist: "ASDFGHJ (talk)", photoLicense: "CC BY-SA 2.0", photoPage: "https://en.wikipedia.org/wiki/Gwangju", mapsUrl: "https://www.google.com/maps/search/?api=1&query=Yangnim-dong%2C%20Gwangju%2C%20South%20Korea" },
      { name: "Kia AutoLand Gwangju", score: 0.68, type: "Automobile assembly plant", emoji: "🚗", instrumentation: "robotic-arm servo whine, conveyor-belt clank, assembly-line rhythm", character: "a car rolling off the line every few seconds inside a vast automated assembly plant", photo: "https://upload.wikimedia.org/wikipedia/commons/0/03/Gwangju_KIA_Factory.jpg", photoArtist: "Neoalpha", photoLicense: "CC0", photoPage: "https://commons.wikimedia.org/wiki/File:Gwangju_KIA_Factory.jpg", mapsUrl: "https://www.google.com/maps/search/?api=1&query=Kia%20AutoLand%20Gwangju%2C%20South%20Korea" },
      { name: "5.18 National Cemetery", score: 0.08, type: "Democracy memorial cemetery", emoji: "🕊️", instrumentation: "solo funeral bell, wind through pines, quiet marble hush", character: "the memorial cemetery for Korea's 1980 pro-democracy uprising, solemn rows of white headstones", photo: "https://upload.wikimedia.org/wikipedia/commons/8/83/Gate_of_Memorial.jpg", photoArtist: "Salamander724", photoLicense: "Public domain", photoPage: "https://en.wikipedia.org/wiki/May_18th_National_Cemetery", mapsUrl: "https://www.google.com/maps/search/?api=1&query=5.18%20National%20Cemetery%2C%20Gwangju%2C%20South%20Korea" }
    ]},
    "Daejeon": { score: 0.48, emoji: "🔬", desc: "Science capital — sourced calm, mixed-source soundscape", hiddenGem: { name: "Sungsimdang Bakery", note: "A 1956 steamed-bun stall turned nationwide-famous bakery that has deliberately never opened outside Daejeon.", quote: "Most of the locals that you ask would tell you to check out the bakery Sungsimdang.", source: "Interesting Korea", sourceUrl: "https://interestingkorea.com/sungsimdang-daejeon-bakery-with-a-history/" }, places: [
      { name: "Yuseong Hot Springs", score: 0.35, type: "Hot spring resort district", emoji: "♨️", instrumentation: "steam hiss, soft vibraphone, warm pad drone", character: "a centuries-old hot spring resort town wrapped in mineral steam", photo: "https://upload.wikimedia.org/wikipedia/commons/4/49/Yuseong-gu_DAEJEON.PNG", photoArtist: "", photoLicense: "CC BY-SA 3.0", photoPage: "https://en.wikipedia.org/wiki/Yuseong_District", mapsUrl: "https://www.google.com/maps/search/?api=1&query=Yuseong%20Hot%20Springs%2C%20Daejeon%2C%20South%20Korea" },
      { name: "Hanbat Arboretum", score: 0.22, type: "Botanical arboretum", emoji: "🌳", instrumentation: "birdsong, koto-like pluck, leaf rustle", character: "a quiet botanical garden in the middle of the science city", photo: "https://upload.wikimedia.org/wikipedia/commons/thumb/d/de/Korea-Daejeon-Uam_Historic_Park-01.jpg/3840px-Korea-Daejeon-Uam_Historic_Park-01.jpg", photoArtist: "", photoLicense: "", photoPage: "https://en.wikipedia.org/wiki/Daejeon", mapsUrl: "https://www.google.com/maps/search/?api=1&query=Hanbat%20Arboretum%2C%20Daejeon%2C%20South%20Korea" },
      { name: "Daedeok Innopolis", score: 0.5, type: "National research & science district", emoji: "🔬", instrumentation: "server-room hum, cleanroom whir, quiet lab keyboard clatter", character: "Korea's largest research cluster, satellite labs and robotics institutes humming quietly behind glass", photo: "https://upload.wikimedia.org/wikipedia/commons/2/25/ETRI-1%2C_Korea.jpg", photoArtist: "Yoshi Canopus", photoLicense: "CC BY-SA 3.0", photoPage: "https://commons.wikimedia.org/wiki/File:ETRI-1,_Korea.jpg", mapsUrl: "https://www.google.com/maps/search/?api=1&query=Daedeok%20Innopolis%2C%20Daejeon%2C%20South%20Korea" },
      { name: "Expo Park & Hanbit Tower", score: 0.6, type: "Former World's Fair park", emoji: "🛰️", instrumentation: "retro-futuristic synth chime, fountain splash, science-museum ambience", character: "the leftover grounds of Korea's 1993 World Expo, a golden tower rising over fountains", photo: "https://upload.wikimedia.org/wikipedia/commons/3/37/Maglev_in_Daejeon_06.jpg", photoArtist: "Brücke-Osteuropa", photoLicense: "CC0", photoPage: "https://en.wikipedia.org/wiki/Expo_Science_Park", mapsUrl: "https://www.google.com/maps/search/?api=1&query=Expo%20Park%20Hanbit%20Tower%2C%20Daejeon%2C%20South%20Korea" }
    ]},
    "Ulsan": { score: 0.55, emoji: "🏭", desc: "Shipbuilding capital with a whaling-port past", hiddenGem: { name: "Amethyst Cavern Park", note: "A former Silla-era gem mine reopened as a small cave park, overshadowed by Ulsan's shipyards and beaches.", quote: "The cave has been producing impressive and high-quality amethyst going back to Korea's Silla kingdom.", source: "Hallyu Stargazer", sourceUrl: "https://www.hallyusg.net/2023/01/17/ktravel-ulsan/" }, places: [
      { name: "Taehwagang River Park", score: 0.4, type: "Riverside bamboo park", emoji: "🎋", instrumentation: "bamboo wind chime, river flow, soft flute", character: "the world's largest riverside bamboo forest, cutting through an industrial city", photo: "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a8/Taehwa_River_from_Hotel_Riverside_Ulsan.jpg/3840px-Taehwa_River_from_Hotel_Riverside_Ulsan.jpg", photoArtist: "", photoLicense: "", photoPage: "https://en.wikipedia.org/wiki/Ulsan", mapsUrl: "https://www.google.com/maps/search/?api=1&query=Taehwagang%20River%20Park%2C%20Ulsan%2C%20South%20Korea" },
      { name: "Ganjeolgot", score: 0.45, type: "Sunrise cape & lighthouse", emoji: "🌅", instrumentation: "ocean swell, lighthouse foghorn drone, gull cry", character: "mainland Korea's easternmost point, first sunrise of the year over open ocean", photo: "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c5/Ganjeolgot%2C_Ulsan_on_August_16th%2C_2018.jpg/3840px-Ganjeolgot%2C_Ulsan_on_August_16th%2C_2018.jpg", photoArtist: "Choi2451", photoLicense: "CC BY-SA 4.0", photoPage: "https://commons.wikimedia.org/wiki/File:Ganjeolgot,_Ulsan_on_August_16th,_2018.jpg", mapsUrl: "https://www.google.com/maps/search/?api=1&query=Ganjeolgot%2C%20Ulsan%2C%20South%20Korea" },
      { name: "Hyundai Motor Ulsan Plant", score: 0.72, type: "World's largest car-assembly plant", emoji: "🏭", instrumentation: "stamping-press thud, welding-robot spark crackle, dockside crane hum", character: "the world's largest single automobile plant, five factories producing a car every few seconds", photo: "https://upload.wikimedia.org/wikipedia/commons/f/f1/Hyundai_car_assembly_line.jpg", photoArtist: "User: Anonyme", photoLicense: "CC BY 2.5", photoPage: "https://commons.wikimedia.org/wiki/File:Hyundai_car_assembly_line.jpg", mapsUrl: "https://www.google.com/maps/search/?api=1&query=Hyundai%20Motor%20Ulsan%20Plant%2C%20South%20Korea" },
      { name: "Hyundai Heavy Industries Shipyard", score: 0.66, type: "Megaship shipyard", emoji: "🚢", instrumentation: "Goliath-crane groan, steel-plate welding hiss, dry-dock horn blast", character: "a shipyard building some of the largest vessels on Earth, cranes the size of skyscrapers", photo: "https://upload.wikimedia.org/wikipedia/commons/6/68/Hyundai_heavy_industries.jpg", photoArtist: "SarahTz", photoLicense: "CC BY 2.0", photoPage: "https://en.wikipedia.org/wiki/HD_Hyundai_Heavy_Industries", mapsUrl: "https://www.google.com/maps/search/?api=1&query=Hyundai%20Heavy%20Industries%20Shipyard%2C%20Ulsan%2C%20South%20Korea" }
    ]},
    "Sejongsi": { score: 0.35, emoji: "🏛️", desc: "Newest planned capital, garden-first and still growing", hiddenGem: { name: "Ieung Bridge", note: "A circular pedestrian and bike bridge over the Geumgang River — Sejong's actual civic landmark, largely unknown outside the city.", quote: "The Ieung Bridge is arguably Sejong's most prominent landmark.", source: "Chris Tharp", sourceUrl: "https://christharp.substack.com/p/an-afternoon-in-sejong-south-koreas" }, places: [
      { name: "Sejong Lake Park", score: 0.32, type: "Lakeside planned-city park", emoji: "🏞️", instrumentation: "minimalist synth pad, water ripple, distant construction hum", character: "a brand-new artificial lake park at the heart of Korea's planned administrative capital", photo: "https://upload.wikimedia.org/wikipedia/commons/thumb/0/01/Sejong_Area_1.jpg/3840px-Sejong_Area_1.jpg", photoArtist: "", photoLicense: "", photoPage: "https://en.wikipedia.org/wiki/Sejong_City", mapsUrl: "https://www.google.com/maps/search/?api=1&query=Sejong%20Lake%20Park%2C%20Sejong%2C%20South%20Korea" },
      { name: "Geumgang Riverside", score: 0.28, type: "River promenade", emoji: "🌊", instrumentation: "acoustic fingerstyle guitar, river current, evening cricket", character: "a quiet riverside promenade at dusk in Korea's newest city", photo: "https://upload.wikimedia.org/wikipedia/commons/thumb/5/53/Geum_River_Sejong.jpg/3840px-Geum_River_Sejong.jpg", photoArtist: "Minseong Kim", photoLicense: "CC BY-SA 4.0", photoPage: "https://commons.wikimedia.org/wiki/File:Geum_River_Sejong.jpg", mapsUrl: "https://www.google.com/maps/search/?api=1&query=Geumgang%20Riverside%2C%20Sejong%2C%20South%20Korea" },
      { name: "Government Complex Sejong", score: 0.45, type: "National government complex", emoji: "🏛️", instrumentation: "quiet corridor echo, rooftop-garden breeze, official footsteps", character: "a decentralized government complex with the world's longest rooftop garden connecting 15 ministries", photo: "https://upload.wikimedia.org/wikipedia/commons/8/87/Sejong_BRT_Station_Gov%27t_Complex_Sejong_South_02.jpg", photoArtist: "*Youngjin", photoLicense: "CC BY-SA 3.0", photoPage: "https://commons.wikimedia.org/wiki/File:Sejong_BRT_Station_Gov't_Complex_Sejong_South_02.jpg", mapsUrl: "https://www.google.com/maps/search/?api=1&query=Government%20Complex%20Sejong%2C%20South%20Korea" }
    ]},
    "Gyeonggi-do": { score: 0.5, emoji: "🏰", desc: "Seoul's walled-fortress, semiconductor-powered commuter belt", hiddenGem: { name: "Jebudo Island", note: "An island reachable only twice a day, when the tide pulls back and opens a sea road on foot from the mainland.", quote: "For those living in and around Seoul, getting to the ideal beaches of the east coast might take too long or cost too much money. Instead, there is a reasonable alternative: Jebudo Island.", source: "Saturdays in Korea", sourceUrl: "http://saturdaysinkorea.blogspot.com/2012/06/jebudo-island.html" }, places: [
      { name: "Suwon Hwaseong Fortress", score: 0.42, type: "UNESCO fortress", emoji: "🏯", instrumentation: "martial drum, brass fanfare, stone-wall echo", character: "an 18th-century UNESCO fortress wall you can walk the full 5.7km circuit of", photo: "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d1/Hwaseong_Fortress%2C_Suwon%2C_Gyeonggi-do%2C_Republic_of_Korea_%282%29.jpg/3840px-Hwaseong_Fortress%2C_Suwon%2C_Gyeonggi-do%2C_Republic_of_Korea_%282%29.jpg", photoArtist: "", photoLicense: "", photoPage: "https://en.wikipedia.org/wiki/Hwaseong_Fortress", mapsUrl: "https://www.google.com/maps/search/?api=1&query=Suwon%20Hwaseong%20Fortress%2C%20Gyeonggi-do%2C%20South%20Korea" },
      { name: "Nami Island", score: 0.35, type: "Scenic river island", emoji: "🌲", instrumentation: "acoustic guitar, birdsong, tree-lined breeze", character: "a crescent-shaped river island famous for its tree-lined autumn paths", photo: "https://upload.wikimedia.org/wikipedia/commons/7/79/Nami_Island.JPG", photoArtist: "", photoLicense: "CC BY-SA 3.0", photoPage: "https://en.wikipedia.org/wiki/Namiseom", mapsUrl: "https://www.google.com/maps/search/?api=1&query=Nami%20Island%2C%20Gyeonggi-do%2C%20South%20Korea" },
      { name: "Paju Book City", score: 0.3, type: "Architectural book town", emoji: "📚", instrumentation: "minimalist piano, paper rustle, concrete reverb", character: "a planned town built entirely around publishing houses and bookshops", photo: "https://upload.wikimedia.org/wikipedia/commons/2/24/Pajubookcityhanok.jpg", photoArtist: "Ccmontgom", photoLicense: "CC BY-SA 3.0", photoPage: "https://en.wikipedia.org/wiki/Paju_Book_City", mapsUrl: "https://www.google.com/maps/search/?api=1&query=Paju%20Book%20City%2C%20Gyeonggi-do%2C%20South%20Korea" },
      { name: "Samsung Digital City", score: 0.7, type: "Global tech HQ campus", emoji: "📱", instrumentation: "cleanroom hum, glass-elevator chime, semiconductor-fab whir", character: "Samsung Electronics' 390-acre headquarters campus, 35,000 engineers working behind glass towers", photo: "https://upload.wikimedia.org/wikipedia/commons/e/e2/Samsung_headquarters.jpg", photoArtist: "Oskar Alexanderson", photoLicense: "CC BY-SA 2.0", photoPage: "https://en.wikipedia.org/wiki/Samsung", mapsUrl: "https://www.google.com/maps/search/?api=1&query=Samsung%20Digital%20City%2C%20Suwon%2C%20South%20Korea" },
      { name: "Korean Folk Village", score: 0.3, type: "Recreated Joseon-era village", emoji: "🏘️", instrumentation: "farmer's percussion band, tightrope-walker gasp, thatched-roof wind", character: "a recreated Joseon-dynasty village with 260 relocated houses and live folk performances", photo: "https://upload.wikimedia.org/wikipedia/commons/b/b8/Farmer_dance.jpg", photoArtist: "Isaac Crumm at English Wikipedia", photoLicense: "Public domain", photoPage: "https://en.wikipedia.org/wiki/Korean_Folk_Village", mapsUrl: "https://www.google.com/maps/search/?api=1&query=Korean%20Folk%20Village%2C%20Yongin%2C%20South%20Korea" }
    ]},
    "Gangwon": { score: 0.34, emoji: "🏔️", desc: "80% mountain, Korea's most restorative soundscape", hiddenGem: { name: "Goseong", note: "Korea's northeasternmost county, kept underdeveloped for decades by its proximity to the North Korean border.", quote: "Goseong exists as a hidden gem nestled within the breathtaking landscapes of Northwestern South Korea.", source: "South of Seoul", sourceUrl: "https://blog.southofseoul.net/discovering-goseong-gangwondo/" }, places: [
      { name: "Seoraksan National Park", score: 0.08, type: "National park", emoji: "🦅", instrumentation: "solo cello, alpine wind, sparse piano", character: "Korea's most dramatic granite peaks, glowing at sunrise above cloud forest", photo: "https://upload.wikimedia.org/wikipedia/commons/thumb/0/01/Dinosaur_Ridge_of_Seoraksan.jpg/3840px-Dinosaur_Ridge_of_Seoraksan.jpg", photoArtist: "", photoLicense: "", photoPage: "https://en.wikipedia.org/wiki/Seoraksan", mapsUrl: "https://www.google.com/maps/search/?api=1&query=Seoraksan%20National%20Park%2C%20Gangwon-do%2C%20South%20Korea" },
      { name: "Gangneung", score: 0.5, type: "Coastal coffee city", emoji: "☕", instrumentation: "lo-fi coffee-shop beat, ocean ambience, indie guitar", character: "Korea's coffee capital, cafes lining a pine-backed beach", photo: "https://upload.wikimedia.org/wikipedia/commons/4/4d/Jumunjin_Lighthouse_20220501_026.jpg", photoArtist: "Mobius6", photoLicense: "CC BY-SA 4.0", photoPage: "https://en.wikipedia.org/wiki/Gangneung", mapsUrl: "https://www.google.com/maps/search/?api=1&query=Gangneung%2C%20Gangwon-do%2C%20South%20Korea" },
      { name: "Chuncheon", score: 0.4, type: "Lake city", emoji: "⛵", instrumentation: "acoustic mandolin, lake ripple, chalkboard-cafe hum", character: "a lake-ringed city famous for grilled chicken and slow afternoons on the water", photo: "https://upload.wikimedia.org/wikipedia/commons/thumb/1/15/Chuncheon-01.jpg/3840px-Chuncheon-01.jpg", photoArtist: "", photoLicense: "", photoPage: "https://en.wikipedia.org/wiki/Chuncheon", mapsUrl: "https://www.google.com/maps/search/?api=1&query=Chuncheon%2C%20Gangwon-do%2C%20South%20Korea" },
      { name: "Woljeongsa & Odaesan", score: 0.1, type: "Mountain temple & national park", emoji: "🌲", instrumentation: "fir-forest hush, temple wind chime, stone pagoda stillness", character: "a nine-story stone pagoda in a fir forest at the foot of Odaesan's highest peaks", photo: "https://upload.wikimedia.org/wikipedia/commons/c/c5/%EC%9B%94%EC%A0%95%EC%82%AC1.jpg", photoArtist: "(c)한국불교문화사업단, culturalcorpsofkoreanbuddhism", photoLicense: "CC BY-SA 4.0", photoPage: "https://en.wikipedia.org/wiki/Woljeongsa", mapsUrl: "https://www.google.com/maps/search/?api=1&query=Woljeongsa%20Temple%20Odaesan%2C%20Gangwon-do%2C%20South%20Korea" },
      { name: "Cheorwon Peace Observatory", score: 0.2, type: "DMZ border observatory", emoji: "🔭", instrumentation: "monorail motor whir, wind over open plain, distant binocular click", character: "an observatory looking straight into the DMZ and a North Korean propaganda village beyond", photo: "https://upload.wikimedia.org/wikipedia/commons/c/c3/DMZ_Tour_during_Best_Squad_Competition_%289085348%29.jpg", photoArtist: "U.S. Army EIGHTHARMY by Pfc. Yun Hyuk Kim", photoLicense: "Public domain", photoPage: "https://commons.wikimedia.org/wiki/File:DMZ_Tour_during_Best_Squad_Competition_(9085348).jpg", mapsUrl: "https://www.google.com/maps/search/?api=1&query=Cheorwon%20Peace%20Observatory%2C%20Gangwon-do%2C%20South%20Korea" }
    ]},
    "Chungcheongbuk-do": { score: 0.28, emoji: "🌸", desc: "World's oldest printed book, now a chip hub", hiddenGem: { name: "Hwalok Cave", note: "An abandoned talc and jade mine in Chungju, repurposed into an underground park with light art and cave kayaking.", quote: "A Hidden Local Spot Near Seoul You've Probably Never Heard Of.", source: "Just K Travel", sourceUrl: "https://justktravel.com/hwalok-cave-chungju-korea-guide/" }, places: [
      { name: "Danyang", score: 0.25, type: "River valley & limestone peaks", emoji: "🏞️", instrumentation: "folk guitar, light percussion, flowing water", character: "a river valley threading between limestone peaks, kayaked at golden hour", photo: "https://upload.wikimedia.org/wikipedia/commons/f/ff/Korea-Danyang-Dodamsambong_3087-07.JPG", photoArtist: "Steve46814", photoLicense: "CC BY-SA 3.0", photoPage: "https://en.wikipedia.org/wiki/Danyang_County", mapsUrl: "https://www.google.com/maps/search/?api=1&query=Danyang%2C%20Chungcheongbuk-do%2C%20South%20Korea" },
      { name: "Songnisan National Park", score: 0.12, type: "Mountain Buddhist temple", emoji: "☸️", instrumentation: "wooden moktak percussion, chanting, forest silence", character: "a mountain temple valley so quiet you can hear pine needles fall", photo: "https://upload.wikimedia.org/wikipedia/commons/thumb/8/84/Gwaneum_Peak_at_Songnisan.jpg/3840px-Gwaneum_Peak_at_Songnisan.jpg", photoArtist: "", photoLicense: "", photoPage: "https://en.wikipedia.org/wiki/Songnisan", mapsUrl: "https://www.google.com/maps/search/?api=1&query=Songnisan%20National%20Park%2C%20Chungcheongbuk-do%2C%20South%20Korea" },
      { name: "SK Hynix Cheongju Campus", score: 0.68, type: "Semiconductor fabrication campus", emoji: "💾", instrumentation: "cleanroom air-filter hum, silicon-wafer chime, fab-line drone", character: "a sprawling memory-chip fabrication campus, cleanrooms manufacturing the world's DRAM", photo: null, photoArtist: "", photoLicense: "", photoPage: "", mapsUrl: "https://www.google.com/maps/search/?api=1&query=SK%20Hynix%20Cheongju%20Campus%2C%20South%20Korea" },
      { name: "Chungju Lake", score: 0.32, type: "Mountain reservoir lake", emoji: "🚤", instrumentation: "boat-engine putter, lake ripple, valley echo", character: "a vast reservoir threading through steep valleys, cruise boats crossing calm water", photo: "https://upload.wikimedia.org/wikipedia/commons/5/5a/Korea-Chungju-Mountain-01.jpg", photoArtist: "Jared Broad from Auckland, New Zealand", photoLicense: "CC BY 2.0", photoPage: "https://en.wikipedia.org/wiki/Chungju", mapsUrl: "https://www.google.com/maps/search/?api=1&query=Chungju%20Lake%2C%20Chungcheongbuk-do%2C%20South%20Korea" }
    ]},
    "Chungcheongnam-do": { score: 0.3, emoji: "🏺", desc: "Ancient Baekje capitals beside a modern EV plant", hiddenGem: { name: "Gongju", note: "The former Baekje capital of Ungjin, carrying three UNESCO World Heritage sites without Buyeo's tour-bus traffic.", quote: "This former capital of the Ungjin Empire is a real hidden gem destination in Chungcheongnam-do, that's absolutely packed with worthwhile cultural and historical experiences.", source: "Travel-Stained", sourceUrl: "https://travel-stained.com/gongju-korea-travel-guide/" }, places: [
      { name: "Buyeo", score: 0.18, type: "Ancient Baekje capital ruins", emoji: "🏛️", instrumentation: "gayageum, temple bell, river mist ambience", character: "the last capital of the Baekje kingdom, ruins wrapped in river mist", photo: "https://upload.wikimedia.org/wikipedia/commons/thumb/3/37/Buyeo_National_Museum_%2820160719_1%29.png/3840px-Buyeo_National_Museum_%2820160719_1%29.png", photoArtist: "", photoLicense: "", photoPage: "https://en.wikipedia.org/wiki/Buyeo_County", mapsUrl: "https://www.google.com/maps/search/?api=1&query=Buyeo%2C%20Chungcheongnam-do%2C%20South%20Korea" },
      { name: "Taean Beach", score: 0.42, type: "West-coast tidal beach", emoji: "🏖️", instrumentation: "tide wash, seagulls, mellow acoustic guitar", character: "a wide tidal-flat beach on the west coast at low tide", photo: "https://upload.wikimedia.org/wikipedia/commons/thumb/5/51/Gauido_at_Taeanhaean_National_Park_image_2.jpg/3840px-Gauido_at_Taeanhaean_National_Park_image_2.jpg", photoArtist: "", photoLicense: "", photoPage: "https://en.wikipedia.org/wiki/Taeanhaean_National_Park", mapsUrl: "https://www.google.com/maps/search/?api=1&query=Taean%20Beach%2C%20Chungcheongnam-do%2C%20South%20Korea" },
      { name: "Hyundai Motor Asan Plant", score: 0.68, type: "Automobile assembly plant", emoji: "🚗", instrumentation: "press-line stamping thud, paint-booth mist hiss, engine-line torque wrench", character: "a 300,000-car-a-year assembly plant building Sonatas and electric IONIQs", photo: null, photoArtist: "", photoLicense: "", photoPage: "", mapsUrl: "https://www.google.com/maps/search/?api=1&query=Hyundai%20Motor%20Asan%20Plant%2C%20South%20Korea" },
      { name: "Oeam Folk Village", score: 0.16, type: "500-year-old hanok village", emoji: "🏘️", instrumentation: "thatched-roof wind rustle, stream trickle, wooden gate creak", character: "a 500-year-old village of thatched and tiled hanok where residents still farm the land", photo: "https://upload.wikimedia.org/wikipedia/commons/9/90/Oeam_Folk_Village%2C_2006_%281%29.jpg", photoArtist: "indytrucks (a flickr user)", photoLicense: "CC BY 2.0", photoPage: "https://en.wikipedia.org/wiki/Oeam", mapsUrl: "https://www.google.com/maps/search/?api=1&query=Oeam%20Folk%20Village%2C%20Asan%2C%20South%20Korea" }
    ]},
    "Jeollabuk-do": { score: 0.38, emoji: "🍚", desc: "UNESCO gastronomy city, birthplace of bibimbap", hiddenGem: { name: "Jaman Mural Village", note: "A former hillside slum above Jeonju Hanok Village, repainted mural by mural into an open-air gallery.", quote: "There was the area filled with beautiful murals having various themes. It gave me plenty of pleasure with vibrant color as well as creative high quality.", source: "Korea's Hidden Gem", sourceUrl: "http://lightkorea.blogspot.com/2014/12/the-jaman-mural-village-in-jeonju-south.html" }, places: [
      { name: "Jeonju Hanok Village", score: 0.34, type: "Traditional food village", emoji: "🥘", instrumentation: "pansori vocals, gayageum, slow warmth", character: "the hometown of bibimbap, hundreds of hanok guesthouses in one dense quarter", photo: "https://upload.wikimedia.org/wikipedia/commons/e/ed/Jeonju_Hanok_Maeul_01.jpg", photoArtist: "Bernard Gagnon", photoLicense: "CC0", photoPage: "https://en.wikipedia.org/wiki/Jeonju", mapsUrl: "https://www.google.com/maps/search/?api=1&query=Jeonju%20Hanok%20Village%2C%20Jeollabuk-do%2C%20South%20Korea" },
      { name: "Naejangsan National Park", score: 0.15, type: "Autumn-foliage national park", emoji: "🍁", instrumentation: "solo daegeum, falling-leaf rustle, mountain stream", character: "a mountain valley considered Korea's finest for autumn foliage", photo: "https://upload.wikimedia.org/wikipedia/commons/thumb/5/54/Najaengsan.JPG/3840px-Najaengsan.JPG", photoArtist: "", photoLicense: "", photoPage: "https://en.wikipedia.org/wiki/Naejangsan", mapsUrl: "https://www.google.com/maps/search/?api=1&query=Naejangsan%20National%20Park%2C%20Jeollabuk-do%2C%20South%20Korea" },
      { name: "Gunsan Modern History Street", score: 0.4, type: "Japanese colonial-era historic street", emoji: "🎞️", instrumentation: "old bank-vault echo, tram-bell ghost, retro film-reel flutter", character: "a preserved 1920s colonial port street of Japanese banks and warehouses turned museums", photo: "https://upload.wikimedia.org/wikipedia/commons/1/12/%EB%8C%80%EC%95%BC%EC%97%AD.jpg", photoArtist: "홍성국강준현", photoLicense: "CC BY-SA 3.0", photoPage: "https://en.wikipedia.org/wiki/Gunsan", mapsUrl: "https://www.google.com/maps/search/?api=1&query=Gunsan%20Modern%20History%20Street%2C%20South%20Korea" },
      { name: "Muju Deogyusan Ski Resort", score: 0.5, type: "Ski resort & mountain gondola", emoji: "🎿", instrumentation: "gondola cable hum, powder-snow crunch, alpine wind", character: "Korea's alpine ski resort, a gondola climbing through Deogyusan's high mountain snow", photo: "https://upload.wikimedia.org/wikipedia/commons/4/47/Mujugun_County_32_%2816860118935%29.jpg", photoArtist: "Republic of  Korea from Seoul, Republic of Korea", photoLicense: "CC BY-SA 2.0", photoPage: "https://commons.wikimedia.org/wiki/File:Mujugun_County_32_(16860118935).jpg", mapsUrl: "https://www.google.com/maps/search/?api=1&query=Muju%20Deogyusan%20Ski%20Resort%2C%20South%20Korea" }
    ]},
    "Jeollanam-do": { score: 0.28, emoji: "🎋", desc: "Tea fields beside Korea's biggest petrochemical complex", hiddenGem: { name: "Gangjin", note: "The birthplace of Goryeo celadon pottery, still largely unvisited outside Korea's own ceramics circles.", quote: "An almost secret city hidden in Jeollanam-do, Gangjin is recognized by Koreans as the birthplace of Goryeo celadon.", source: "Lea Moreau, Gwangju News", sourceUrl: "https://gwangjunewsgic.com/travel/around-korea/gangjin/" }, places: [
      { name: "Suncheon Bay", score: 0.08, type: "Wetland & reed marsh", emoji: "🦢", instrumentation: "ambient wetland drone, solo oboe, bird calls", character: "a vast tidal reed marsh at golden hour, cranes overhead", photo: "https://upload.wikimedia.org/wikipedia/commons/d/dd/Suncheon3.jpg", photoArtist: "Byeonggwan", photoLicense: "Public domain", photoPage: "https://en.wikipedia.org/wiki/Suncheon_Bay_Ecological_Park", mapsUrl: "https://www.google.com/maps/search/?api=1&query=Suncheon%20Bay%2C%20Jeollanam-do%2C%20South%20Korea" },
      { name: "Boseong Green Tea Fields", score: 0.2, type: "Terraced tea plantation", emoji: "🍵", instrumentation: "koto-like pluck, misty hush, distant rooster", character: "terraced green tea fields disappearing into morning mist", photo: "https://upload.wikimedia.org/wikipedia/commons/8/82/Korea-Boseong-Green.tea-02.jpg", photoArtist: "by Fred Ojardias", photoLicense: "CC BY 2.0", photoPage: "https://en.wikipedia.org/wiki/Boseong_County", mapsUrl: "https://www.google.com/maps/search/?api=1&query=Boseong%20Green%20Tea%20Fields%2C%20Jeollanam-do%2C%20South%20Korea" },
      { name: "Damyang Juknokwon", score: 0.16, type: "Bamboo grove", emoji: "🎍", instrumentation: "bamboo wind chime, rustling leaves, soft flute", character: "a dense bamboo forest with wind moving through it like static", photo: "https://upload.wikimedia.org/wikipedia/commons/e/ea/Korea-Damyang-Hanok_in_the_Bamboo_Forest-01.jpg", photoArtist: "UNC - CFC - USFK from Seoul, Republic of Korea", photoLicense: "CC BY 2.0", photoPage: "https://en.wikipedia.org/wiki/Damyang_County", mapsUrl: "https://www.google.com/maps/search/?api=1&query=Damyang%20Juknokwon%2C%20Jeollanam-do%2C%20South%20Korea" },
      { name: "Naganeupseong Folk Village", score: 0.14, type: "Living walled folk village", emoji: "🧱", instrumentation: "straw-roof wind, well-bucket creak, farmyard rooster", character: "a 600-year-old walled town still farmed by about 100 households behind stone ramparts", photo: "https://upload.wikimedia.org/wikipedia/commons/2/26/Naganeupseong_Folk_Village_MS3656.JPG", photoArtist: "Marco Schmidt [1]", photoLicense: "CC BY-SA 3.0", photoPage: "https://en.wikipedia.org/wiki/Naganeupseong", mapsUrl: "https://www.google.com/maps/search/?api=1&query=Naganeupseong%20Folk%20Village%2C%20Suncheon%2C%20South%20Korea" },
      { name: "Yeosu", score: 0.62, type: "Coastal night-view city", emoji: "🌃", instrumentation: "cable-car pulley hum, harbor-light shimmer, night-market sizzle", character: "a coastal city famous for its glittering night sea view and cross-harbor cable car", photo: "https://upload.wikimedia.org/wikipedia/commons/d/d3/Dolsan_Bridge1.JPG", photoArtist: "Glabb", photoLicense: "Public domain", photoPage: "https://en.wikipedia.org/wiki/Yeosu", mapsUrl: "https://www.google.com/maps/search/?api=1&query=Yeosu%2C%20South%20Korea" }
    ]},
    "Gyeongsangbuk-do": { score: 0.36, emoji: "🗿", desc: "Thousand-year Silla capital and steel-mill port", hiddenGem: { name: "Mungyeong Saejae", note: "A Joseon-era mountain pass and hiking trail overshadowed by Gyeongju's ruins and Andong's Hahoe Village.", quote: "Quite unknown but a true hidden gem and one of the most beautiful hiking trails in South Korea.", source: "Linda Goes East", sourceUrl: "https://lindagoeseast.com/2016/04/27/mungyeong-saejae-koreas-hiking-spot/" }, places: [
      { name: "Gyeongju Historic Area", score: 0.2, type: "Ancient Silla capital", emoji: "🗿", instrumentation: "gayageum, slow strings, temple bells", character: "a 1,000-year former capital where royal burial mounds rise from the city itself", photo: "https://upload.wikimedia.org/wikipedia/commons/2/24/Gyeongju_montage.png", photoArtist: "Kyoww (montage)", photoLicense: "CC BY-SA 4.0", photoPage: "https://en.wikipedia.org/wiki/Gyeongju", mapsUrl: "https://www.google.com/maps/search/?api=1&query=Gyeongju%20Historic%20Area%2C%20Gyeongsangbuk-do%2C%20South%20Korea" },
      { name: "Hahoe Folk Village", score: 0.24, type: "UNESCO folk village", emoji: "🎭", instrumentation: "mask-dance drum, courtyard echo, wooden clack", character: "a horseshoe-river folk village famous for traditional mask-dance drama", photo: "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d8/Hahoe_Folk_Village_02.jpg/3840px-Hahoe_Folk_Village_02.jpg", photoArtist: "", photoLicense: "", photoPage: "https://en.wikipedia.org/wiki/Hahoe_Folk_Village", mapsUrl: "https://www.google.com/maps/search/?api=1&query=Hahoe%20Folk%20Village%2C%20Gyeongsangbuk-do%2C%20South%20Korea" },
      { name: "POSCO Pohang Steelworks", score: 0.7, type: "Integrated steelworks", emoji: "🏭", instrumentation: "blast-furnace roar, molten-steel hiss, rolling-mill clang", character: "one of Korea's founding steel mills, blast furnaces glowing orange along the Pohang coast", photo: "https://upload.wikimedia.org/wikipedia/commons/4/4e/%ED%8F%AC%EC%8A%A4%EC%BD%94_%ED%8F%AC%ED%95%AD.jpg", photoArtist: "Aatu Dorochenko", photoLicense: "CC BY-SA 4.0", photoPage: "https://commons.wikimedia.org/wiki/File:포스코_포항.jpg", mapsUrl: "https://www.google.com/maps/search/?api=1&query=POSCO%20Pohang%20Steelworks%2C%20South%20Korea" },
      { name: "Yangdong Folk Village", score: 0.16, type: "UNESCO clan hanok village", emoji: "🏘️", instrumentation: "gayageum, valley wind, 500-year-old wooden-beam creak", character: "Korea's largest traditional clan village, tile-roofed noble houses over 500 years old", photo: "https://upload.wikimedia.org/wikipedia/commons/e/ee/2008-Korea-Gyeongju-Yangdong_Village-13.jpg", photoArtist: "Kok Leng Yeo from Singapore, Singapore", photoLicense: "CC BY 2.0", photoPage: "https://commons.wikimedia.org/wiki/File:2008-Korea-Gyeongju-Yangdong_Village-13.jpg", mapsUrl: "https://www.google.com/maps/search/?api=1&query=Yangdong%20Folk%20Village%2C%20Gyeongju%2C%20South%20Korea" }
    ]},
    "Gyeongsangnam-do": { score: 0.46, emoji: "⛵", desc: "Shipyard city and a 1592 lantern-festival legend", hiddenGem: { name: "Geochang", note: "An inland county of history and mountain scenery that sits outside every major Gyeongsangnam-do itinerary.", quote: "Geochang, Korea is an unassuming area with a lot to share.", source: "Hallie Bradley, The Soul of Seoul", sourceUrl: "https://thesoulofseoul.net/geochang-korea-guide/" }, places: [
      { name: "Tongyeong", score: 0.48, type: "Harbor & island city", emoji: "⛵", instrumentation: "cable-car wind, harbor engine hum, mellow brass", character: "a hillside harbor city looking out over hundreds of small islands", photo: "https://upload.wikimedia.org/wikipedia/commons/7/7f/Korea-Tongyeong-Collage-01.jpg", photoArtist: "Jungho Jung and User:Asfreeas Derivative work by User:Caspian blue", photoLicense: "CC BY 3.0", photoPage: "https://en.wikipedia.org/wiki/Tongyeong", mapsUrl: "https://www.google.com/maps/search/?api=1&query=Tongyeong%2C%20Gyeongsangnam-do%2C%20South%20Korea" },
      { name: "Jinju", score: 0.44, type: "Fortress river city", emoji: "🏯", instrumentation: "festival drum, river flow, lantern-float ambience", character: "a riverside fortress city famous for its autumn floating-lantern festival", photo: "https://upload.wikimedia.org/wikipedia/commons/2/29/View_of_Jinju_01.jpg", photoArtist: "Bernard Gagnon", photoLicense: "CC0", photoPage: "https://en.wikipedia.org/wiki/Jinju", mapsUrl: "https://www.google.com/maps/search/?api=1&query=Jinju%2C%20Gyeongsangnam-do%2C%20South%20Korea" },
      { name: "Hanwha Ocean Geoje Shipyard", score: 0.64, type: "Megaship shipyard", emoji: "🚢", instrumentation: "900-ton Goliath-crane groan, dry-dock flood roar, steel-hull weld spark", character: "a shipyard with the world's largest dry dock, building tankers the length of four football fields", photo: "https://upload.wikimedia.org/wikipedia/commons/c/c9/Aerial_View_of_Daewoo_Shipbuilding_%26_Marine_Engineering.jpg", photoArtist: "IikaJzuchiN", photoLicense: "CC BY-SA 4.0", photoPage: "https://commons.wikimedia.org/wiki/File:Aerial_View_of_Daewoo_Shipbuilding_&_Marine_Engineering.jpg", mapsUrl: "https://www.google.com/maps/search/?api=1&query=Hanwha%20Ocean%20Geoje%20Shipyard%2C%20South%20Korea" },
      { name: "Haegeumgang", score: 0.4, type: "Scenic sea-cliff islet", emoji: "🏝️", instrumentation: "boat-tour engine, sea-cliff echo, gull chorus", character: "a jagged sea-cliff islet off Geoje reached only by boat, called Korea's Geumgangsan of the sea", photo: "https://upload.wikimedia.org/wikipedia/commons/7/73/KOCIS_Korea_Haegeumgang_05_%2810011598385%29.jpg", photoArtist: "Korea.net / Korean Culture and Information Service (Jeon Han)", photoLicense: "CC BY-SA 2.0", photoPage: "https://commons.wikimedia.org/wiki/File:KOCIS_Korea_Haegeumgang_05_(10011598385).jpg", mapsUrl: "https://www.google.com/maps/search/?api=1&query=Haegeumgang%2C%20Geoje%2C%20South%20Korea" }
    ]},
    "Jeju-do": { score: 0.42, emoji: "🌋", desc: "Volcanic island — sourced highest-pleasantness score in Korea", hiddenGem: { name: "Gimnyeong", note: "A white-sand fishing village a short bus ride from Jeju City, next door to Manjanggul Cave's crowds but rarely visited itself.", quote: "A short bus ride from Jeju City you'll find the mesmerizing white sand beach and traditional fishing village of Gimnyeong.", source: "Jarrod Hall, Hidden Lanes", sourceUrl: "https://hiddenlanes.com/blog/top-unknown-places-in-jeju-city-south-korea" }, places: [
      { name: "Hallasan", score: 0.12, type: "National park & volcano", emoji: "🏔️", instrumentation: "solo flute, wind, volcanic ambience", character: "a dormant volcano with a crater lake at its summit, above the clouds", photo: "https://upload.wikimedia.org/wikipedia/commons/9/9d/Hallasan_Above.jpg", photoArtist: "LG전자", photoLicense: "CC BY 2.0", photoPage: "https://en.wikipedia.org/wiki/Hallasan", mapsUrl: "https://www.google.com/maps/search/?api=1&query=Hallasan%2C%20Jeju-do%2C%20South%20Korea" },
      { name: "Seongsan Ilchulbong", score: 0.3, type: "UNESCO sunrise peak", emoji: "🌅", instrumentation: "gentle strings, ocean breeze, dawn chorus", character: "a tuff-cone crater rising from the sea, famous for sunrise", photo: "https://upload.wikimedia.org/wikipedia/commons/thumb/6/61/Seongsan_Ilchulbong_from_the_air.jpg/3840px-Seongsan_Ilchulbong_from_the_air.jpg", photoArtist: "", photoLicense: "", photoPage: "https://en.wikipedia.org/wiki/Seongsan_Ilchulbong", mapsUrl: "https://www.google.com/maps/search/?api=1&query=Seongsan%20Ilchulbong%2C%20Jeju-do%2C%20South%20Korea" },
      { name: "Jeju City", score: 0.65, type: "Island capital", emoji: "🍊", instrumentation: "light jazz, tropical guitar, ocean rhythm", character: "the relaxed island capital, tangerine orchards and black lava-stone walls", photo: "https://upload.wikimedia.org/wikipedia/commons/f/fd/Jeju_-_Hallasan.JPG", photoArtist: "J. Patrick Fischer", photoLicense: "CC BY-SA 3.0", photoPage: "https://en.wikipedia.org/wiki/Jeju_City", mapsUrl: "https://www.google.com/maps/search/?api=1&query=Jeju%20City%2C%20Jeju-do%2C%20South%20Korea" },
      { name: "Seongeup Folk Village", score: 0.2, type: "600-year-old living folk village", emoji: "🗿", instrumentation: "black-stone wall wind, thatched-roof rustle, horse-hoof clop", character: "a 600-year-old walled village of black volcanic-stone houses, still lived in today", photo: "https://upload.wikimedia.org/wikipedia/commons/c/c5/Seongeup_Historic_Village.jpg", photoArtist: "Trainholic", photoLicense: "CC BY-SA 4.0", photoPage: "https://en.wikipedia.org/wiki/Seongeup_Folk_Village", mapsUrl: "https://www.google.com/maps/search/?api=1&query=Seongeup%20Folk%20Village%2C%20Jeju%2C%20South%20Korea" },
      { name: "Manjanggul Cave", score: 0.08, type: "UNESCO lava tube cave", emoji: "🕳️", instrumentation: "cave-drip echo, deep stone resonance, underground silence", character: "an 8.9km lava tube cave, one of Earth's longest, formed a hundred thousand years ago", photo: "https://upload.wikimedia.org/wikipedia/commons/b/b6/Manjanggul_lava_column%2C_largest_in_the_world.jpg", photoArtist: "AhmadElq", photoLicense: "CC BY-SA 4.0", photoPage: "https://en.wikipedia.org/wiki/Manjanggul", mapsUrl: "https://www.google.com/maps/search/?api=1&query=Manjanggul%20Cave%2C%20Jeju%2C%20South%20Korea" }
    ]}
  }
}

// ── TRANSPARENT REGION ACTIVITY PROXY ────────────────────────────────────────
// Every input is an official, province-comparable statistic. The weights are
// explicit design hypotheses, not fitted coefficients and not ISO Eventfulness.
// Log min-max scaling prevents Seoul's density and Jeju's tourism intensity from
// dominating solely because they are extreme. Raw source tables and citations
// live in research/moodscape_*_official_*.csv.
const REGION_MODEL_INPUTS = {
  "Seoul":             { populationK:9340, density:15432, tourismTripsK:10742, complaints:63452, facilities:266,  overall:79.6, crowding:70.7, revisit:75.1, recommend:73.4 },
  "Busan":             { populationK:3239, density:4197,  tourismTripsK:12460, complaints:11746, facilities:933,  overall:80.7, crowding:74.8, revisit:77.5, recommend:75.5 },
  "Daegu":             { populationK:2335, density:2637,  tourismTripsK:3579,  complaints:9820,  facilities:240,  overall:77.8, crowding:72.6, revisit:76.0, recommend:72.5 },
  "Incheon":           { populationK:3058, density:2859,  tourismTripsK:9786,  complaints:9309,  facilities:706,  overall:78.0, crowding:76.3, revisit:74.9, recommend:74.1 },
  "Gwangju":           { populationK:1447, density:2888,  tourismTripsK:1364,  complaints:3966,  facilities:50,   overall:83.3, crowding:81.9, revisit:79.9, recommend:77.4 },
  "Daejeon":           { populationK:1465, density:2714,  tourismTripsK:3368,  complaints:3870,  facilities:45,   overall:77.9, crowding:75.7, revisit:73.9, recommend:71.0 },
  "Ulsan":             { populationK:1094, density:1029,  tourismTripsK:4066,  complaints:2523,  facilities:234,  overall:80.6, crowding:79.4, revisit:77.1, recommend:74.8 },
  "Sejongsi":          { populationK:398,  density:855,   tourismTripsK:1390,  complaints:305,   facilities:321,  overall:78.2, crowding:77.0, revisit:72.6, recommend:71.2 },
  "Gyeonggi-do":       { populationK:13949,density:1366,  tourismTripsK:51016, complaints:29532, facilities:21430,overall:79.3, crowding:77.2, revisit:75.8, recommend:74.2 },
  "Gangwon":           { populationK:1517, density:90,    tourismTripsK:31070, complaints:2746,  facilities:577,  overall:81.0, crowding:76.1, revisit:77.1, recommend:75.5 },
  "Chungcheongbuk-do": { populationK:1631, density:220,   tourismTripsK:11052, complaints:2357,  facilities:3492, overall:79.5, crowding:77.1, revisit:75.3, recommend:73.7 },
  "Chungcheongnam-do": { populationK:2229, density:270,   tourismTripsK:21783, complaints:3513,  facilities:4111, overall:79.1, crowding:76.1, revisit:75.4, recommend:73.6 },
  "Jeollabuk-do":      { populationK:1747, density:216,   tourismTripsK:15328, complaints:2809,  facilities:1281, overall:82.9, crowding:81.3, revisit:80.4, recommend:77.9 },
  "Jeollanam-do":      { populationK:1747, density:141,   tourismTripsK:23705, complaints:1942,  facilities:1205, overall:83.2, crowding:82.1, revisit:81.6, recommend:79.3 },
  "Gyeongsangbuk-do":  { populationK:2583, density:136,   tourismTripsK:23367, complaints:2563,  facilities:3944, overall:80.0, crowding:76.4, revisit:76.9, recommend:75.5 },
  "Gyeongsangnam-do":  { populationK:3230, density:306,   tourismTripsK:25793, complaints:4443,  facilities:4448, overall:82.0, crowding:77.8, revisit:78.9, recommend:76.0 },
  "Jeju-do":           { populationK:676,  density:365,   tourismTripsK:11551, complaints:2031,  facilities:211,  overall:82.5, crowding:78.6, revisit:78.3, recommend:77.0 },
};

const SOUNDSCAPE_REFERENCE = {
  "Seoul": { eventfulness:78, note:"Published Seoul soundwalk / POI research; retained only as an external validation reference." },
  "Daejeon": { eventfulness:45, note:"Published Yuseong-gu in-situ study; retained only as an external validation reference." },
};

const regionInputRows = Object.values(REGION_MODEL_INPUTS);
const activityRaw = x => ({
  density:x.density,
  tourism:x.tourismTripsK / x.populationK,
  complaints:x.complaints / x.populationK * 100,
  facilities:x.facilities / x.populationK * 100,
  crowdingPressure:100 - x.crowding,
});
const rawRows = regionInputRows.map(activityRaw);
function logScale(value, key) {
  const logs = rawRows.map(r => Math.log1p(r[key]));
  return (Math.log1p(value) - Math.min(...logs)) / (Math.max(...logs) - Math.min(...logs));
}
const REGION_MODEL = {};
Object.entries(REGION_MODEL_INPUTS).forEach(([name, x]) => {
  const r = activityRaw(x);
  const components = {
    density:logScale(r.density,"density"), tourism:logScale(r.tourism,"tourism"),
    complaints:logScale(r.complaints,"complaints"), facilities:logScale(r.facilities,"facilities"),
    crowding:logScale(r.crowdingPressure,"crowdingPressure"),
  };
  const activity = 100 * (components.density*.35 + components.tourism*.30 + components.complaints*.15 + components.facilities*.10 + components.crowding*.10);
  const pleasantness = x.overall*.40 + x.recommend*.25 + x.revisit*.20 + x.crowding*.15;
  REGION_MODEL[name] = { activity, pleasantness, components, raw:r, input:x, reference:SOUNDSCAPE_REFERENCE[name] || null };
});

function computeRegionScore(stateName) {
  return REGION_MODEL[stateName] ? REGION_MODEL[stateName].activity / 100 : null;
}

// Region scores now come live from the composite above. Place-level scores stay
// illustrative (no per-landmark equivalent data exists) but are re-anchored to the new
// region baseline so each region's internal spread (e.g. Hongdae vs.
// Gyeongbokgung within Seoul) survives rather than being overwritten.
Object.keys(MOOD_DATA.states).forEach(stateName => {
  const state = MOOD_DATA.states[stateName];
  const newScore = computeRegionScore(stateName);
  if (newScore === null) return;
  const delta = newScore - state.score;
  state.places.forEach(p => { p.score = Math.max(0, Math.min(1, p.score + delta)); });
  state.score = newScore;
});

// South Korea province name mapping (from TopoJSON SIG_CD codes to our MOOD_DATA keys)
const KOREA_PROVINCE_MAP = {
  "Seoul": "Seoul",
  "Busan": "Busan",
  "Daegu": "Daegu",
  "Incheon": "Incheon",
  "Gwangju": "Gwangju",
  "Daejeon": "Daejeon",
  "Ulsan": "Ulsan",
  "Sejongsi": "Sejongsi",
  "Gyeonggi-do": "Gyeonggi-do",
  "Gangwon-do": "Gangwon",
  "Chungcheongbuk-do": "Chungcheongbuk-do",
  "Chungcheongnam-do": "Chungcheongnam-do",
  "Jeollabuk-do": "Jeollabuk-do",
  "Jeollanam-do": "Jeollanam-do",
  "Gyeongsangbuk-do": "Gyeongsangbuk-do",
  "Gyeongsangnam-do": "Gyeongsangnam-do",
  "Jeju-do": "Jeju-do",
};

const MOOD_COLOR = (score) => {
  // Blue (peaceful, score=0) → Purple (mid) → Red (exciting, score=1)
  const r = Math.round(59 + score * (220 - 59));
  const g = Math.round(130 - score * 110);
  const b = Math.round(246 - score * 210);
  return `rgb(${r},${g},${b})`;
};

const MOOD_LABEL = (score) => {
  if (score < 0.2) return "Very peaceful";
  if (score < 0.4) return "Calm";
  if (score < 0.6) return "Balanced";
  if (score < 0.8) return "Lively";
  return "Very exciting";
};

function getMoodDesc(score, name) {
  if (score < 0.15) return `${name} is one of the most serene spots in the country — near-total quiet.`;
  if (score < 0.35) return `${name} offers calm, unhurried energy — great for reflection and rest.`;
  if (score < 0.55) return `${name} strikes a balance — active enough to feel alive, quiet enough to breathe.`;
  if (score < 0.75) return `${name} buzzes with life and things to do, especially evenings and weekends.`;
  return `${name} is among the most electric places in Korea — constant energy day and night.`;
}

// Regional flavor for the generic (non-landmark-specific) local personas below —
// keeps every province's "park ranger" and "local explorer" distinct instead of
// reusing the same one or two names/greetings everywhere.
const REGION_FLAVOR = {
  "Seoul": { ranger: "Tae-yang", local: "Min-jun", hook: "the best night-market snacks, palace shortcuts, or which subway line beats the traffic" },
  "Busan": { ranger: "Seung-hyun", local: "Ha-neul", hook: "the freshest milhoe stalls, our Gyeongsang satoori dialect, or the best sunset spot on the sand" },
  "Daegu": { ranger: "Do-yoon", local: "Eun-bi", hook: "why our food is famously the spiciest in Korea, where to find real apple makgeolli, or the best chimaek spot" },
  "Incheon": { ranger: "Hae-won", local: "Yu-jin", hook: "real jjajangmyeon versus the Chinatown version, container-port life, or ferry routes out to the islands" },
  "Gwangju": { ranger: "Ye-jin", local: "Seo-jun", hook: "why this is called Korea's food capital, where the biennale murals are, or our 1980 democracy history" },
  "Daejeon": { ranger: "Min-jae", local: "Ji-ho", hook: "KAIST campus life, the best mineral hot-spring baths, or why everyone here loves sujebi soup" },
  "Ulsan": { ranger: "Woo-jin", local: "Da-hye", hook: "our whaling-port past, the shipyard's scale, or the best spot to watch a launch from the dry dock" },
  "Sejongsi": { ranger: "Da-eun", local: "Hyun-woo", hook: "what it's like living in a city built from scratch, our rooftop gardens, or the best new-town cafes" },
  "Gyeonggi-do": { ranger: "Joon-ho", local: "Na-yeon", hook: "real Suwon galbi, semiconductor-belt commuter life, or the best fortress-wall sunset view" },
  "Gangwon": { ranger: "San-ho", local: "Bo-mi", hook: "buckwheat memil noodles, our mountain dialect, or the best untouched trail nobody talks about" },
  "Chungcheongbuk-do": { ranger: "Bo-ram", local: "Ye-eun", hook: "Jikji — the world's oldest printed book — our grape harvest, or the new chip-town cafes" },
  "Chungcheongnam-do": { ranger: "Chan-mi", local: "Jae-won", hook: "Baekje-era ruins, tidal-flat clam digging, or life beside Korea's EV assembly lines" },
  "Jeollabuk-do": { ranger: "Ha-eun", local: "Sung-min", hook: "why bibimbap was born here, our UNESCO gastronomy status, or the best hanok-stay breakfast" },
  "Jeollanam-do": { ranger: "Seo-yeon", local: "Do-hyun", hook: "picking tea on Boseong's slopes, fresh-caught seafood, or life beside the petrochemical coast" },
  "Gyeongsangbuk-do": { ranger: "Tae-min", local: "Ga-young", hook: "Silla-dynasty burial mounds, our steel-mill skyline, or the best market hoe-deopbap" },
  "Gyeongsangnam-do": { ranger: "Ji-woo", local: "Su-bin", hook: "the shipyard's scale, the lantern-festival legend, or the best island-hopping route" },
  "Jeju-do": { ranger: "Soon-ja", local: "Areum", hook: "black pork BBQ, our haenyeo sea-women divers, or the sweetest hallabong tangerine stand" },
};

function getLocalPersona(stateName, place) {
  const name = (place.name || "").toLowerCase();
  const type = (place.type || "").toLowerCase();
  const char = (place.character || "").toLowerCase();
  const flavor = REGION_FLAVOR[stateName] || { ranger: "Yeon-woo", local: "Yoon-a", hook: "my favorite spots, hidden gems, or local food recommendations" };

  // 1. Gyeongbokgung
  if (name.includes("gyeongbokgung")) {
    return {
      name: "Min-ho (Royal Guard)",
      avatar: "💂‍♂️",
      greeting: "Hello, traveler! I am Min-ho, a guard protecting Gwanghwamun gate. Ask me anything about the Joseon dynasty history, palace secrets, or our changing of the guard ceremony!"
    };
  }
  // 2. Gyeongju Bulguksa
  if (name.includes("bulguksa")) {
    return {
      name: "Beop-gyeong (Buddhist Monk)",
      avatar: "🙏",
      greeting: "Welcome. I am monk Beop-gyeong of Bulguksa Temple. Ask me about our ancient pagoda treasures, the Seokguram Grotto, or Buddhist meditation practices!"
    };
  }
  // 3. Hongdae
  if (name.includes("hongdae")) {
    return {
      name: "Ji-hye (Indie Bassist)",
      avatar: "🎸",
      greeting: "Hey! I'm Ji-hye, bassist for a local garage rock band. Ask me about the best live indie clubs, hidden record stores, or post-show street food in Hongdae!"
    };
  }
  // 4. Gangnam
  if (name.includes("gangnam")) {
    return {
      name: "Jun-su (Fashion Stylist)",
      avatar: "🕶️",
      greeting: "Welcome to Gangnam! I'm Jun-su, a fashion stylist. Ask me about the hottest shopping streets, luxury cafes, or premium rooftop lounges in the district!"
    };
  }
  // 5. Bukchon Hanok
  if (name.includes("bukchon")) {
    return {
      name: "Grandma Kim (Tea House Owner)",
      avatar: "🍵",
      greeting: "Hello, dear traveler. I am Grandma Kim, and I run a small traditional tea house here in the village. Ask me about our 600-year-old wooden houses, tea pairings, or quiet alleys!"
    };
  }
  // 6. Jeju Hallasan / Parks
  if (name.includes("hallasan") || type.includes("mountain") || type.includes("park")) {
    return {
      name: `${flavor.ranger} (Park Ranger)`,
      avatar: "🥾",
      greeting: `Welcome to the trails! I'm ${flavor.ranger}, a forest ranger here in ${stateName}. Ask me about the hiking courses, weather conditions, local wildlife, or volcano safety!`
    };
  }
  // 7. Beaches / Haeundae
  if (name.includes("beach") || type.includes("beach")) {
    return {
      name: "Min-ki (Surf Coach)",
      avatar: "🏄‍♂️",
      greeting: "Hey, surf's up! I'm Min-ki, a local surf instructor. Ask me about the wave conditions, beach safety, or best coastal sunset bars!"
    };
  }
  // 8. Solemn / Memorial
  if (name.includes("cemetery") || name.includes("memorial") || name.includes("dmz") || name.includes("5.18")) {
    return {
      name: "Mr. Park (Historical Guide)",
      avatar: "🎙️",
      greeting: "Greetings. I am Mr. Park, a historical guide. Ask me about the history, solemn background, and commemorative monuments of this memorial site."
    };
  }

  // Fallback default persona based on place category
  if (type.includes("traditional") || type.includes("temple") || type.includes("folk") || type.includes("village")) {
    return {
      name: "Sung-ho (Local Craftsman)",
      avatar: "🏺",
      greeting: `Welcome to ${place.name}! I am Sung-ho, a local craftsman. Ask me about our traditional arts, village history, or local heritage!`
    };
  }

  return {
    name: `${flavor.local} (Local Explorer)`,
    avatar: "🎒",
    greeting: `Hi! I'm ${flavor.local}, a local resident who loves exploring ${place.name}. Ask me about ${flavor.hook}!`
  };
}
