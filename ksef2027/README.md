# KSEF 2027 submissions — Moodscape

| | National (국내분야) | International |
|---|---|---|
| Paper | `national/KSEF2027_National_논문_Moodscape.pdf` (.docx source), Korean, 9 pages | `international/KSEF2027_International_Research_paper_Moodscape.pdf` (.docx source), English, 9 pages |
| Presentation | `national/KSEF2027_National_발표자료_Moodscape.pdf` (.pptx source), Korean, 13 slides | `international/KSEF2027_International_Presentation_Moodscape.pdf` (.pptx source), English, 13 slides |
| Form abstract | `abstracts.md` (국문 800자 내외) | `abstracts.md` (English, ~250 words) |

## Format sources

- **Papers** fill the official template `붙임3. KSEF National(국내분야) 논문양식.docx`: A4, its header, its title-block table
  (Korean/English title, authors, 요약 ≤500자, Abstract ≤200 words, Key Words ≤5 in alphabetical order), body 10 pages
  or fewer, references in citation order with authors given-name first. The International guidelines give no template,
  so the English paper uses the same KSEF template with the Korean rows removed and the header changed, and contains
  every item the guidelines require (names, school, country, motivation, objectives, methodology, results, conclusions).
- **Presentations**: International asks for PowerPoint format submitted as PDF; National allows any format as PDF.
  Both are 7-minute talks (7 min + 8 min Q&A), so each deck has 13 slides.
- The template fonts (한양신명조, 돋움, 바탕) are HWP fonts that macOS lacks; the build uses AppleMyungjo (명조) and
  Apple SD Gothic Neo (돋움).

## Rebuild

```
python3 ksef2027/build_papers.py   # needs python-docx, pypdf; exports PDF with Apple Pages
python3 ksef2027/build_decks.py    # needs python-pptx; exports PDF with Keynote
```

Every number is read from `research/paper/stats.json` and the audio-measurement CSVs, which the analysis scripts in
`research/` produce. Links in the papers and decks point at the git tag `ksef2027-submission`, so they keep working
if the branch is merged or deleted.

## Before submitting (to do by the participant)

1. Replace the placeholders `[참가자 이름]`, `[학교명]`, `[지역]`, `[Participant Name]`, `[School Name]`, `[City]`,
   `[분과코드]`/`[Code]` in `build_papers.py` and `build_decks.py`, then rebuild.
2. Choose categories. Suggested: National A6 시스템/소프트웨어 (or C2 인문사회/예술); International COM (Computer Science,
   data analysis/software).
3. Rename the PDFs to the required patterns: National `분과코드_대표학생명_논문.pdf`, `분과코드_대표학생명_발표자료.pdf`;
   International `Representative student name_Research paper.pdf`, `Representative student name_Presentation.pdf`.
4. Merge this branch into `main` so the GitHub Pages demo (`https://clairenah19.github.io/sound-moodscape/`) shows the
   current text. The live site still serves an older `main` whose intro claims a built-in synth that does not exist.
5. International also needs a team photo and a 30-second 1920×1080 MP4 introduction video (not produced here).
