import re # reguläre Expression - mit re.search sucht Python an einer beliebigen Stelle im TExt nach dem angegebenen Muster
from rest_framework import serializers
from urllib.parse import urlparse, parse_qs, urlencode


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
    ''' Validates the video URL submitted to create a quiz. '''
    url = serializers.URLField(required=True, allow_blank=False, max_length=200) # übernimmt die grundsätzlich Prüfung für ein gültiges URL Format
    
    def validate_url(self, value): # value enthält den eingegebenen Link als Text
        ''' Validates a YouTube video link and returns its canonical URL. '''
        parsed_url = urlparse(value) # parse -> einen Text nach seiner Struktur zu lesen. | urlparse(value) zerlegt diesen Text in sechs Teile (scheme: Protokoll, also https; netloc: Addressteil, wie www.youtube.de; path, wie /watch; params; query; fragment)
        host = parsed_url.hostname # extrahiert nur den Host
        
        allowed_hosts = ["youtube.com", "www.youtube.com", "youtu.be"]

        if parsed_url.scheme not in {"http", "https"}:
            raise serializers.ValidationError("Bitte gib einen HTTP- oder HTTPS-Link ein.")
        
        if host not in allowed_hosts:
            raise serializers.ValidationError(
                f"Der Host '{host}' ist nicht erlaubt."
            )
        
        # Die Video-ID steht beim Kurzlink im Pfad und beim /watch-Link in der Query.
        if host == "youtu.be":
            video_ids = [parsed_url.path.removeprefix("/").removesuffix("/")]
        elif parsed_url.path == "/watch":
            query_params = parse_qs(parsed_url.query, keep_blank_values=True)
            video_ids = query_params.get("v", [])
        else:
            raise serializers.ValidationError("Bitte gib einen YouTube Link mit dem Pfad /watch ein")

        if len(video_ids) != 1 or not re.fullmatch(r"[A-Za-z0-9_-]{11}", video_ids[0]):
            raise serializers.ValidationError("Der YouTube-Link muss genau eine gültige Video-ID enthalten.")

        video_id = video_ids[0] # Hole die einzelne Video-ID aus der Liste.

        query = urlencode({"v": video_id}) # Baue die Query mit genau einem Parameter, zum Beispiel v=jNQXAC9IVRw.
        return f"https://www.youtube.com/watch?{query}" # Gib die URL in dem Format zurück, das Quizly speichert.
    
    

class QuestionSerializer(serializers.ModelSerializer):
    ''' Serializes a quiz question with its answer options, correct answer, and timestamps. '''

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
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    video_url = serializers.URLField(read_only=True)
    class Meta:
        model = Quiz
        fields = ('id', 'title', 'description', 'created_at', 'updated_at', 'video_url', 'questions')


class QuizUpdateSerializer(serializers.ModelSerializer):
    ''' '''
    questions = QuestionSerializer(source='quiz_question', many=True, read_only=True)
    
    class Meta:
        model = Quiz
        fields = ('id', 'title', 'description', 'created_at', 'updated_at', 'video_url', 'questions')
        
# hier dürfen nur Titel und Beschreibung geändert werden können:
# ... Dafür braucht man keine zusätzliche Methode. 
# ... Im ModelSerializer kann man über read_only_fields innerhalb von Meta festlegen, welche Felder ausschließlich ausgegeben werden dürfen. 
# ... Nur title und description bleiben beschreibbar.

