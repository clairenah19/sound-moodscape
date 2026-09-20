# Accessibility tester recruitment and session brief

Status: **future work; participation unlikely in the current study**. The user does not expect blind/low-vision participation to be available. No invitations have been sent. This brief is retained for a possible later study; it is not an active recruitment requirement for completing the current project. Full-stat readouts, longitude panning, and N/S/E/W navigation remain deferred.

The current study may evaluate how general listeners perceive generated music. It cannot establish usefulness or usability for blind/low-vision users. Keyboard, focus and screen-reader checks by the development team should be reported as technical checks only. Sighted participants using a blindfold or closing their eyes do not substitute for intended-user accessibility evaluation.

## Recruitment

Invite 1–2 adult blind or low-vision volunteers through an existing contact or an accessibility/community organization selected by the researcher. Ask about preferred format, browser/device, screen reader or magnification, and availability. Do not request a diagnosis. Offer an accessible consent document and agree on compensation/time before booking. This is a usability pilot, not a representative validation sample.

Suggested invitation:

“I’m developing Moodscape, a map that represents regional activity through sound. Would you be interested in a voluntary 20–30 minute usability session using your usual browser and assistive technology? We want to understand the current interface before changing its keyboard and audio navigation. You can skip any task or stop at any point. Please let me know your preferred way to communicate and any adjustments you would like.”

The researcher must provide contact details, arrange accessible scheduling and consent, and record whether participants actually agree. Do not mark recruitment complete because an invitation was drafted.

## Session tasks using the current interface

1. Find and open a region without coaching; describe what the focus and announcements convey.
2. Find the activity score and the inputs behind it. Note whether a long automatic readout would help or overwhelm.
3. Open a landmark and distinguish the illustrative score from Wikipedia popularity.
4. Try sound navigation, then return to normal browsing and type in search. Note keyboard conflicts.
5. Compare two navigation tones; ask what direction and activity they communicate without explaining the mapping first.
6. Discuss preferences for optional longitude-based stereo position, N/S/E/W movement, boundaries, and repeat-stat commands.

Record task completion, misunderstandings, focus loss, conflicts with assistive technology, and the participant's own words with permission. Do not infer “accessible” from successful automated tests. Stop recording on request. Store consent/contact separately from anonymized notes.

## Proposed implementation after recruitment

- Full stat readout: name, model status, activity, density, tourism intensity, complaints, facilities, crowding, and separate visitor pleasantness, with units; confirm verbosity preference first.
- Stereo position: derive a region representative longitude from map geometry, normalize west/east across actual regions, route navigation cues through StereoPannerNode, and retain a centered fallback on unsupported devices. Explain that panning represents region position, not exact landmark position.
- Directional navigation: choose the nearest region in the requested geographic cardinal sector, do not wrap across national boundaries, announce “no region north/east/south/west,” and leave editing fields and ordinary screen-reader commands alone.
- Test ordinary Tab/Enter operation independently of guided mode, browser resize, zoom, focus return, reduced motion, and mono/headphone listening.

Reference for the planned panning implementation: [MDN StereoPannerNode.pan](https://developer.mozilla.org/en-US/docs/Web/API/StereoPannerNode/pan), -1 left through +1 right. No panning change was made in this pass.
