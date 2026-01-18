from google import genai
from google.genai import types

class GeoAnalyzer:
    def __init__(self, api_key):
        self.api_key = api_key
        self.client = None
        if api_key:
            self.client = genai.Client(api_key=api_key)

    def analyze_image(self, image_path):
        if not self.client:
            return "Błąd: Brak klucza API Gemini."

        try:
            with open(image_path, 'rb') as f:
                image_bytes = f.read()

            geo_prompt = """
            Jesteś ekspertem od geolokalizacji i analizy obrazu (OSINT). 
            Twoim zadaniem jest przeanalizowanie zdjęcia i określenie jego lokalizacji.

            1. ANALIZA: Przyjrzyj się architekturze, roślinności, znakom, ludziom i krajobrazowi.
            2. OPIS: Stwórz krótki, wciągający opis dla użytkownika, wskazując detale zdradzające miejsce.
            3. WERDYKT: Określ najbardziej prawdopodobną lokalizację.

            SFORMATUJ ODPOWIEDŹ W NASTĘPUJĄCY SPOSÓB:

            [OPIS]
            (Tutaj 2-3 zdania opisu dla użytkownika)

            [LOKALIZACJA]
            Kraj: ...
            Miasto/Region: ...
            Konkretne miejsce: ...
            Poziom pewności (Wysoki/Średni/Niski): ...

            [SŁOWA KLUCZOWE]
            (5-7 tagów oddzielonych przecinkami do wyszukiwarki, np.: góry, zima, jezioro)
            """

            response = self.client.models.generate_content(
                model='gemini-2.5-flash',
                config=types.GenerateContentConfig(temperature=0.4),
                contents=[
                    types.Part.from_bytes(data=image_bytes, mime_type='image/jpeg'),
                    geo_prompt
                ]
            )
            return response.text
        except Exception as e:
            return f"Błąd Gemini API: {str(e)}"
