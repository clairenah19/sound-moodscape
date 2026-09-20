# Live external-service checks

Status as of 2026-09-13: **BLOCKED, not pass/fail tested**.

| Feature | Live status | Evidence still required |
|---|---|---|
| Gemini Ask a Local | BLOCKED — key not accessible in this session | Real reply and working main-page send/error UI |
| Gemini music-style prediction | BLOCKED — key not accessible in this session | Real structured prediction; record whether photo fetch succeeded |
| Gemini language-accessibility estimate | BLOCKED — key not accessible in this session | Real score/label/reasoning and cached display |
| Gangnam real Suno track | BLOCKED — key not accessible in this session | Generated MP3, provenance and actual listening judgment |

The user believes keys are saved inside Moodscape. No matching open Chrome/Safari tab or environment-variable key was found. This does not establish that no key exists; the browser/origin must be identified. No secret was printed or committed. API failure and absence of a usable key are distinct statuses.

`live_feature_checks.html` runs all three Gemini calls using the same app functions and same-origin saved configuration. It also has a separate button to generate exactly one Gangnam track and record a human listening judgment. Open it under the **same origin** (scheme, hostname and port) where the keys were saved. A newly chosen localhost port has different storage. The report redacts saved keys and can be downloaded.

No service-success claim or audible minor-key confirmation is inferred from a prompt, mock response, or static code inspection. Automated fixture tests are recorded separately in the implementation report.
