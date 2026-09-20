// Separate evidence display: pageview popularity never changes p.score or audio.
const landmarkPageviews = new Map();
let landmarkPageviewStatus = 'loading';
function evidenceEscape(value) {
  return String(value).replace(/[&<>"']/g, c => ({'&':'&amp;', '<':'&lt;', '>':'&gt;', '"':'&quot;', "'":'&#39;'}[c]));
}
function renderLandmarkEvidence(place, stateName) {
  const row = landmarkPageviews.get(stateName + '__' + place.name);
  const delta = (place.score - MOOD_DATA.states[stateName].score) * 100;
  let popularity = landmarkPageviewStatus === 'loading' ? 'Loading public pageview data…' : 'No pageview record available.';
  if (row) {
    const title = evidenceEscape(row.wikipedia_title || 'No linked English Wikipedia article');
    const articleUrl = 'https://en.wikipedia.org/wiki/' + encodeURIComponent(row.wikipedia_title || '');
    const source = row.wikipedia_title ? `<a href="${articleUrl}" target="_blank" rel="noopener">${title}</a>` : title;
    popularity = `<div>${source}</div><div>${evidenceEscape(row.start)} to ${evidenceEscape(row.end)}</div>`;
    if (row.status === 'ok' && Number.isFinite(Number(row.popularity_offset_0_100)) && row.popularity_offset_0_100 !== '') {
      popularity += `<strong>${Number(row.popularity_offset_0_100).toFixed(1)} / 100 popularity offset</strong>
        <div>${Number(row.avg_monthly_views).toLocaleString()} average monthly views · ${row.months_covered} complete months</div>`;
    } else {
      popularity += `<div>Offset unavailable: ${evidenceEscape(row.status.replaceAll('_', ' '))}.
        ${row.months_covered !== '' ? `${row.months_covered} of ${row.expected_months} months available.` : ''}</div>`;
    }
    popularity += `<p>${evidenceEscape(row.article_scope)}. English Wikipedia readership is a popularity proxy, not a soundscape measurement.</p>`;
  } else if (landmarkPageviewStatus === 'error') {
    popularity = 'Pageview data could not be loaded. Serve the site over HTTP and try again.';
  }
  return `<div class="panel-section">
    <div class="panel-title">Landmark evidence — two separate views</div>
    <div class="landmark-evidence-grid">
      <div><b>Existing illustrative score</b><p>${Math.round(place.score * 100)} / 100 · ${delta >= 0 ? '+' : ''}${delta.toFixed(1)} points from the region baseline.</p>
        <p>Author judgment; currently drives the music. Landmark field measurement pending.</p></div>
      <div><b>Wikipedia popularity</b>${popularity}</div>
    </div>
    <p class="suno-help">The log-scaled popularity offset is shown for comparison only. It is not added to the mood score and does not change the soundscape.
      <a href="research/moodscape_landmark_pageviews.csv" download>Download source CSV</a></p>
  </div>`;
}
fetch('research/moodscape_landmark_pageviews.json')
  .then(r => { if (!r.ok) throw new Error('Pageview data unavailable'); return r.json(); })
  .then(data => {
    data.rows.forEach(row => landmarkPageviews.set(row.state + '__' + row.place, row));
    landmarkPageviewStatus = 'ready';
  }).catch(() => { landmarkPageviewStatus = 'error'; })
  .finally(() => {
    const host = document.getElementById('landmark-evidence');
    if (host && currentPlace && currentPlaceState) host.innerHTML = renderLandmarkEvidence(currentPlace, currentPlaceState);
  });
