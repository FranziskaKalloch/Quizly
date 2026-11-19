import re 
from rest_framework import serializers
from urllib.parse import urlparse, parse_qs, urlencode


from ..models import Quiz, Questions
class QuizCreateSerializer(serializers.Serializer):
    """ Validates the video URL submitted to create a quiz. """
    url = serializers.URLField(required=True, allow_blank=False, max_length=200) 
    
    def validate_url(self, value): 
        """ Validates a YouTube video link and returns its canonical URL. """
        parsed_url = urlparse(value) 
        host = parsed_url.hostname 
        
        allowed_hosts = ["youtube.com", "www.youtube.com", "youtu.be"]

        if parsed_url.scheme not in {"http", "https"}:
            raise serializers.ValidationError("Bitte gib einen HTTP- oder HTTPS-Link ein.")
        
        if host not in allowed_hosts:
            raise serializers.ValidationError(
                f"Der Host '{host}' ist nicht erlaubt."
            )
        
        if host == "youtu.be":
            video_ids = [parsed_url.path.removeprefix("/").removesuffix("/")]
        elif parsed_url.path == "/watch":
            query_params = parse_qs(parsed_url.query, keep_blank_values=True)
            video_ids = query_params.get("v", [])
        else:
            raise serializers.ValidationError("Bitte gib einen YouTube Link mit dem Pfad /watch ein")

        if len(video_ids) != 1 or not re.fullmatch(r"[A-Za-z0-9_-]{11}", video_ids[0]):
            raise serializers.ValidationError("Der YouTube-Link muss genau eine gültige Video-ID enthalten.")

        video_id = video_ids[0] 

        query = urlencode({"v": video_id}) 
        return f"https://www.youtube.com/watch?{query}" 
    
    
class QuestionSerializer(serializers.ModelSerializer):
    """ Serializes a quiz question with its answer options, correct answer, and timestamps. """

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
    """ Serializes a quiz and its associated questions. """
    questions = QuestionSerializer(source='quiz_question', many=True, read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    video_url = serializers.URLField(read_only=True)
    class Meta:
        model = Quiz
        fields = ('id', 'title', 'description', 'created_at', 'updated_at', 'video_url', 'questions')
        

