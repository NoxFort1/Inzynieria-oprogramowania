from google import genai
from google.genai import types

class GeoAnalyzer:
    def __init__(self, api_key):
        self.api_key = api_key
        self.client = None
        if api_key:
            self.client = genai.Client(api_key=api_key)

<<<<<<< HEAD
    def analyze_image(self, image_path):
=======
    def analyze_image(self, image_data):
>>>>>>> c594f8b68f2b815bfa0b481812097726e3e52da9
        if not self.client:
            return "Błąd: Brak klucza API Gemini."

        try:
<<<<<<< HEAD
            with open(image_path, 'rb') as f:
                image_bytes = f.read()

=======
>>>>>>> c594f8b68f2b815bfa0b481812097726e3e52da9
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
<<<<<<< HEAD
                model='gemini-2.5-flash',
                config=types.GenerateContentConfig(temperature=0.4),
                contents=[
                    types.Part.from_bytes(data=image_bytes, mime_type='image/jpeg'),
=======
                model='gemini-2.0-flash', # Zmieniłem na 2.0-flash (jest stabilny, 2.5 to literówka?)
                config=types.GenerateContentConfig(temperature=0.4),
                contents=[
                    # TU BYŁ BŁĄD: Przekazujemy surowe image_data, a nie obiekt Image
                    types.Part.from_bytes(data=image_data, mime_type='image/jpeg'),
>>>>>>> c594f8b68f2b815bfa0b481812097726e3e52da9
                    geo_prompt
                ]
            )
            return response.text
<<<<<<< HEAD
=======
            
>>>>>>> c594f8b68f2b815bfa0b481812097726e3e52da9
        except Exception as e:
            return f"Błąd Gemini API: {str(e)}"