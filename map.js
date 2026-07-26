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

  // ── DRAW TACTILE PATHS (ACCESSIBILITY OVERLAY) ──────────────────────────────
  const TACTILE_NODES = [
    "Seoul", "Incheon", "Gyeonggi-do", "Gangwon", "Chungcheongbuk-do", 
    "Sejongsi", "Daejeon", "Chungcheongnam-do", "Jeollabuk-do", "Gwangju", 
    "Jeollanam-do", "Jeju-do", "Gyeongsangnam-do", "Busan", "Ulsan", 
    "Daegu", "Gyeongsangbuk-do"
  ];
  window._tactileNodes = TACTILE_NODES;

  const centroids = [];
  TACTILE_NODES.forEach(nodeKey => {
    const feature = geojson.features.find(f => {
      const rawName = f.properties.CTP_KOR_NM || f.properties.name || "";
      const engName = f.properties.CTP_ENG_NM || f.properties.name_eng || rawName;
      const key = KOREA_PROVINCE_MAP[engName] || KOREA_PROVINCE_MAP[rawName];
      return key === nodeKey;
    });
    if (feature) {
      const cent = pathFn.centroid(feature);
      centroids.push({ key: nodeKey, x: cent[0], y: cent[1] });
    }
  });
  window._tactileCentroids = centroids;

  // Draw the yellow dashed path overlay
  mapG.selectAll("path.tactile-path-line").remove();
  if (centroids.length > 1) {
    const lineGenerator = d3.line()
      .x(d => d.x)
      .y(d => d.y);

    mapG.append("path")
      .datum(centroids)
      .attr("class", "tactile-path-line")
      .attr("d", lineGenerator)
      .style("display", window._accessibilityActive ? "block" : "none");
  }

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

// ── ACCESSIBILITY / TACTILE NAVIGATION CONTROLS ──────────────────────────────
let activeNodeIdx = -1;

window.toggleAccessibilityMode = function() {
  const btn = document.getElementById("acc-toggle");
  const panel = document.getElementById("map-panel");
  const pathLine = d3.select(".tactile-path-line");
  
  window._accessibilityActive = !window._accessibilityActive;
  
  if (window._accessibilityActive) {
    btn.classList.add("active");
    panel.classList.add("accessibility-active");
    pathLine.style("display", "block");
    
    // Start at Seoul (Index 0)
    activeNodeIdx = 0;
    const nodeKey = window._tactileNodes[activeNodeIdx];
    highlightTactileNode(nodeKey);
    playTactileTick(true);
    vocalizeTactileState(nodeKey);
  } else {
    btn.classList.remove("active");
    panel.classList.remove("accessibility-active");
    pathLine.style("display", "none");
    d3.select(".map-g").selectAll("circle.tactile-node-ring").remove();
    d3.select("#map-svg").selectAll(".region-path").classed("active-node", false);
    
    if (window.speechSynthesis) window.speechSynthesis.cancel();
    activeNodeIdx = -1;
  }
};

function highlightTactileNode(nodeKey) {
  const mapG = d3.select(".map-g");
  const svg = d3.select("#map-svg");
  
  mapG.selectAll("circle.tactile-node-ring").remove();
  svg.selectAll(".region-path").classed("active-node", false);
  
  if (!nodeKey) return;
  
  // Highlight active province outline path
  svg.selectAll(".region-path").filter(f => {
    const rawName = f.properties.CTP_KOR_NM || f.properties.name || "";
    const engName = f.properties.CTP_ENG_NM || f.properties.name_eng || rawName;
    const key = KOREA_PROVINCE_MAP[engName] || KOREA_PROVINCE_MAP[rawName];
    return key === nodeKey;
  }).classed("active-node", true);

  // Draw pulsing rings around centroid
  const cent = window._tactileCentroids.find(c => c.key === nodeKey);
  if (cent) {
    const ring = mapG.append("circle")
      .attr("class", "tactile-node-ring")
      .attr("cx", cent.x)
      .attr("cy", cent.y);
      
    const animateRing = () => {
      ring.attr("r", 8)
        .style("opacity", 1)
        .transition()
        .duration(1200)
        .ease(d3.easeQuadOut)
        .attr("r", 28)
        .style("opacity", 0)
        .on("end", () => {
          if (window._accessibilityActive && activeNodeIdx !== -1 && window._tactileNodes[activeNodeIdx] === nodeKey) {
            animateRing();
          } else {
            ring.remove();
          }
        });
    };
    animateRing();
  }
}

// Global Key Listeners
window.addEventListener("keydown", (e) => {
  if (!window._accessibilityActive) return;
  if (!window._tactileNodes || window._tactileNodes.length === 0) return;
  
  if (e.key === "ArrowRight") {
    e.preventDefault();
    activeNodeIdx = (activeNodeIdx + 1) % window._tactileNodes.length;
    const nodeKey = window._tactileNodes[activeNodeIdx];
    highlightTactileNode(nodeKey);
    playTactileTick(false);
    vocalizeTactileState(nodeKey);
  } else if (e.key === "ArrowLeft") {
    e.preventDefault();
    activeNodeIdx = (activeNodeIdx - 1 + window._tactileNodes.length) % window._tactileNodes.length;
    const nodeKey = window._tactileNodes[activeNodeIdx];
    highlightTactileNode(nodeKey);
    playTactileTick(false);
    vocalizeTactileState(nodeKey);
  } else if (e.key === "Enter" || e.key === " ") {
    e.preventDefault();
    const nodeKey = window._tactileNodes[activeNodeIdx];
    if (nodeKey) {
      d3.select("#map-svg").selectAll(".region-path").filter(f => {
        const rawName = f.properties.CTP_KOR_NM || f.properties.name || "";
        const engName = f.properties.CTP_ENG_NM || f.properties.name_eng || rawName;
        const key = KOREA_PROVINCE_MAP[engName] || KOREA_PROVINCE_MAP[rawName];
        return key === nodeKey;
      }).dispatch("click");
      playTactileTick(true);
    }
  } else if (e.key === "Escape") {
    e.preventDefault();
    goCountry();
    playTactileTick(true);
  }
});
