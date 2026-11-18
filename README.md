# Quizly

## Quiz aus einem YouTube-Video erstellen

- FFmpeg und `ffprobe` müssen systemweit installiert und im Suchpfad verfügbar sein.
  Auf macOS mit Homebrew lassen sie sich mit `brew install ffmpeg` installieren.
- Für den YouTube-Abruf verwendet `yt-dlp` eine unterstützte Deno- oder Node.js-Version.
- Hinterlege den Gemini-Schlüssel als `GEMINI_API_KEY` in deiner lokalen `.env`.
  `GEMINI_MODEL` kann optional ein anderes Gemini-Flash-Modell auswählen.
- Beim ersten Transkribieren lädt Whisper das Modell `base` herunter und speichert es im lokalen Cache.

Nach dem Login sendest du mit dem `access_token`-Cookie eine POST-Anfrage an
`/api/quizzes/`. Der JSON-Body enthält zum Beispiel
`{"url": "https://www.youtube.com/watch?v=jNQXAC9IVRw"}`.
Die API lädt die Audiospur, transkribiert sie lokal und sendet das Transkript
an Gemini. Nach dem Speichern gibt sie das Quiz mit zehn Fragen und HTTP 201 zurück.
