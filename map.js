// ── MOOD SCAPE D3 MAP INITIALIZATION & ZOOM ──────────────────────────────────

const svg = d3.select("#map-svg");
const tooltip = document.getElementById("tooltip");
const hint = document.getElementById("map-hint");

function initMap(geojson) {
  const panel = document.getElementById("map-panel");
  const W = panel.offsetWidth || 400;
  const H = panel.offsetHeight || 600;
  const pad = 32;

  svg.selectAll("*").remove();
  svg.attr("width", W).attr("height", H).attr("viewBox", null);

  const proj = d3.geoMercator().fitExtent([[pad, pad], [W - pad, H - pad]], geojson);
  const pathFn = d3.geoPath().projection(proj);

  let mapG = svg.append("g").attr("class", "map-g");

  // Zoom + pan
  const zoom = d3.zoom()
    .scaleExtent([1, 12])
    .translateExtent([[0, 0], [W, H]])
    .on("start", () => { svg.node().classList.add("grabbing"); tooltip.style.display = "none"; })
    .on("zoom", (event) => { mapG.attr("transform", event.transform); })
    .on("end", () => { svg.node().classList.remove("grabbing"); });
    
  svg.call(zoom).on("dblclick.zoom", null);
  window._mapZoom = zoom;
  window._mapSvg = svg;

  mapG.selectAll("path.region-path")
    .data(geojson.features)
    .join("path")
    .attr("class", "region-path")
    .attr("d", pathFn)
    .attr("fill", d => {
      const rawName = d.properties.CTP_KOR_NM || d.properties.name || "";
      const engName = d.properties.CTP_ENG_NM || d.properties.name_eng || rawName;
      const moodKey = KOREA_PROVINCE_MAP[engName] || KOREA_PROVINCE_MAP[rawName];
      const s = moodKey && MOOD_DATA.states[moodKey];
      return s ? MOOD_COLOR(s.score) : "#1e2235";
    })
    .on("mousemove", function(event, d) {
      const rawName = d.properties.CTP_KOR_NM || d.properties.name || "";
      const engName = d.properties.CTP_ENG_NM || d.properties.name_eng || rawName;
      const moodKey = KOREA_PROVINCE_MAP[engName] || KOREA_PROVINCE_MAP[rawName];
      const s = moodKey && MOOD_DATA.states[moodKey];
      tooltip.style.display = "block";
      tooltip.style.left = (event.offsetX + 14) + "px";
      tooltip.style.top = (event.offsetY - 10) + "px";
      tooltip.innerHTML = `<div class="tt-name">${s ? s.emoji + " " : ""}${engName || rawName}</div><div class="tt-score">${s ? MOOD_LABEL(s.score) + " — " + Math.round(s.score * 100) + " / 100" : "No data yet"}</div>`;
    })
    .on("mouseleave", function() { tooltip.style.display = "none"; })
    .on("click", function(event, d) {
      const rawName = d.properties.CTP_KOR_NM || d.properties.name || "";
      const engName = d.properties.CTP_ENG_NM || d.properties.name_eng || rawName;
      const moodKey = KOREA_PROVINCE_MAP[engName] || KOREA_PROVINCE_MAP[rawName];
      if (!moodKey || !MOOD_DATA.states[moodKey]) return;
      svg.selectAll(".region-path").classed("active", false);
      d3.select(this).classed("active", true);
      showStateSide(moodKey);
      currentState = moodKey;
      updateBreadcrumb(moodKey, null);
      hint.style.display = "none";
    });

  window.addEventListener("resize", () => { if (window._koreaData) initMap(window._koreaData); });
}

window.addEventListener("DOMContentLoaded", () => {
  window._koreaData = KOREA_GEOJSON;
  initMap(KOREA_GEOJSON);
  document.getElementById("map-hint").textContent = "Click a province to explore places";

  // Zoom control buttons
  const zoomBy = (factor) => {
    if (window._mapZoom && window._mapSvg) {
      window._mapSvg.transition().duration(250).call(window._mapZoom.scaleBy, factor);
    }
  };
  document.getElementById("zoom-in").addEventListener("click", () => zoomBy(1.5));
  document.getElementById("zoom-out").addEventListener("click", () => zoomBy(1 / 1.5));
  document.getElementById("zoom-reset").addEventListener("click", () => {
    if (window._mapZoom && window._mapSvg) {
      window._mapSvg.transition().duration(300).call(window._mapZoom.transform, d3.zoomIdentity);
    }
  });
});
