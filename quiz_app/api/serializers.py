import re
from urllib.parse import parse_qs, urlparse

from rest_framework import serializers


from ..models import Quiz, Questions

#### Wie die URL beim POST-Endpunkt verarbeitet wird
# Der Benutzer fügt einen YouTube-Link ins Formular ein.
# Das Frontend schickt diesen Link an POST /api/quizzes/. 
# Im JSON heißt das Feld url, zum Beispiel {"url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"}.
# Die View übergibt die Anfrage an den Serializer. Der JSON-Body steht in request.data. Die View gibt diese Daten an den QuizCreateSerializer weiter und startet mit is_valid() die Prüfung.
# URLField prüft die grundlegende Eingabe. Es prüft, ob url vorhanden, höchstens 200 Zeichen lang und als URL aufgebaut ist. Ein Link zu example.com könnte diese Prüfung ebenfalls bestehen.
#validate_url prüft, ob der Link für Quizly geeignet ist. 
# DRF ruft diese Methode automatisch auf und übergibt ihr den Wert aus url. Du zerlegst den Link in Host, Pfad und Query. 
# Bei youtube.com/watch oder www.youtube.com/watch suchst du die Video-ID im Parameter v. 
# Bei youtu.be steht die ID direkt im Pfad. Fehlt die ID oder gehört der Host zu einer anderen Website, meldest du einen Validierungsfehler für url.
# Die View arbeitet mit der geprüften URL weiter. Wenn alles passt, gibst du aus validate_url den Link zurück. Die View findet ihn dann in validated_data unter url und kann ihn später an yt-dlp weitergeben. 
# Bei einem Validierungsfehler antwortet der Endpunkt mit 400.


class QuizCreateSerializer(serializers.Serializer):
    """Validate and normalize the video URL submitted to create a quiz."""

    url = serializers.URLField(max_length=200)

    def validate_url(self, value):
        """Return the canonical URL for a YouTube video or short link."""
        parsed_url = urlparse(value)
        host = parsed_url.hostname

        if parsed_url.scheme not in {"http", "https"}:
            raise serializers.ValidationError("Bitte gib einen HTTP- oder HTTPS-Link ein.")

        if host == "youtu.be":
            video_ids = [parsed_url.path.removeprefix("/").removesuffix("/")]
        elif host in {"youtube.com", "www.youtube.com"} and parsed_url.path == "/watch":
            query_params = parse_qs(parsed_url.query, keep_blank_values=True)
            video_ids = query_params.get("v", [])
        else:
            raise serializers.ValidationError("Bitte gib einen YouTube-Videolink ein.")

        if len(video_ids) != 1 or not re.fullmatch(r"[A-Za-z0-9_-]{11}", video_ids[0]):
            raise serializers.ValidationError("Der YouTube-Link muss genau eine gültige Video-ID enthalten.")

        return f"https://www.youtube.com/watch?v={video_ids[0]}"


class QuestionSerializer(serializers.ModelSerializer):
    """Serialize a quiz question and its answer options."""

    def get_fields(self):
        fields = super().get_fields()
        if not self.context.get("include_question_timestamps", True):
            fields.pop("created_at")
            fields.pop("updated_at")
        return fields

    class Meta:
        model = Questions
        fields = ('id', 'question_title', 'question_options', 'answer', 'created_at', 'updated_at')
    
class QuizSerializer(serializers.ModelSerializer):
    ''' Serializes a quiz and its associated questions. '''
    questions = QuestionSerializer(source='quiz_question', many=True, read_only=True)
    class Meta:
        model = Quiz
        fields = ('id', 'title', 'description', 'created_at', 'updated_at', 'video_url', 'questions')


