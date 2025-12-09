# Projekt: Dopasowanie Wycinka do Obrazu (Image Matching)

Aplikacja webowa służąca do znajdowania lokalizacji małego wycinka obrazu (np. fragmentu mapy, zdjęcia przedmiotu) na większym obrazie referencyjnym. Wykorzystuje zaawansowane algorytmy Computer Vision (OpenCV) do precyzyjnego dopasowania oraz Google Gemini AI do analizy kontekstowej znalezionego miejsca.

## Funkcjonalności

* **Precyzyjne dopasowanie obrazu (Feature Matching):**
    * Użytkownik przesyła wycinek (Cropped Image) oraz jeden lub wiele obrazów referencyjnych (Reference Images).
    * Backend analizuje obrazy używając algorytmu **SIFT (OpenCV)**, aby wykryć kluczowe cechy i deskryptory, niezależne od skali czy obrotu.
    * Następuje dopasowanie cech między wycinkiem a obrazami referencyjnymi (BFMatcher z testem proporcji Lowe'a).
    * Zastosowanie algorytmu **RANSAC** pozwala na odfiltrowanie błędnych dopasowań (outliers) i precyzyjne wyznaczenie homografii (położenia wycinka).
    * Aplikacja automatycznie wybiera obraz referencyjny z największą liczbą poprawnych dopasowań.
    * Wynikiem jest obraz referencyjny z wyraźnie zaznaczonym (obramowanym) obszarem, w którym znaleziono wycinek.
* **Analiza AI (Google Gemini):**
    * Po skutecznym znalezieniu dopasowania, wycinek jest wysyłany do modelu **Google Gemini Pro Vision**.
    * Sztuczna inteligencja analizuje zawartość wycinka, dostarczając dodatkowe informacje kontekstowe (geoInfo), np. opis geograficzny, historyczny lub identyfikację widocznych obiektów.
* **Obsługa wielu plików:**
    * Intuicyjny interfejs Drag & Drop pozwala na łatwe przesyłanie plików.
    * Możliwość przesłania wielu obrazów referencyjnych jednocześnie – system automatycznie znajdzie najlepsze dopasowanie wśród wszystkich przesłanych plików.

## Technologie

### Frontend
* **React:** Biblioteka do budowy dynamicznego interfejsu użytkownika.
* **CSS/SCSS:** Stylowanie komponentów.

### Backend
* **Python (Flask):** Lekki framework webowy do obsługi API REST.
* **OpenCV (cv2):** Główna biblioteka do przetwarzania obrazów i implementacji algorytmów SIFT i RANSAC.
* **Google Generative AI (Gemini API, model: gemini-2.5-flash):** Integracja z multimodalnym modelem AI do analizy treści obrazów.
* **Flask-CORS:** Obsługa zapytań Cross-Origin między frontendem a backendem.

## Instalacja i Uruchomienie

### Wymagania Wstępne
* Python 3.8+
* Node.js i npm (lub yarn)
* Aktywny klucz API Google Cloud (dla usługi Gemini Pro Vision)

### Krok 1: Konfiguracja Backendu (Flask)

1.  Przejdź do katalogu `backend`:
    ```bash
    cd backend
    ```
2.  (Zalecane) Utwórz i aktywuj wirtualne środowisko Python:
    ```bash
    # Windows
    python -m venv venv
    venv\Scripts\activate

    # macOS/Linux
    python3 -m venv venv
    source venv/bin/activate
    ```
3.  Zainstaluj wymagane biblioteki:
    ```bash
    pip install -r requirements.txt
    ```
4.  Skonfiguruj zmienne środowiskowe:
    * Utwórz plik `.env` wewnątrz katalogu `backend`.
    * Dodaj swój klucz API Google oraz ścieżkę do folderu tymczasowego:
        ```env
        GOOGLE_API_KEY=Twoj_Klucz_API_Tutaj
        ```
    * Upewnij się, że folder `backend/uploads` istnieje (jeśli nie, utwórz go).
5.  Uruchom serwer deweloperski:
    ```bash
    python app.py
    ```
    Serwer będzie działał pod adresem `http://127.0.0.1:5000`.

### Krok 2: Konfiguracja Frontendu (React)

1.  Otwórz nowy terminal i przejdź do katalogu `frontend`:
    ```bash
    cd frontend
    ```
2.  Zainstaluj zależności projektu:
    ```bash
    npm install
    # lub jeśli używasz yarn: yarn install
    ```
3.  Uruchom aplikację:
    ```bash
    npm start
    # lub: yarn start
    ```
    Aplikacja powinna automatycznie otworzyć się w przeglądarce pod adresem `http://localhost:3000`.

## Jak używać aplikacji

1.  Upewnij się, że oba serwery (backend i frontend) są uruchomione.
2.  W przeglądarce, w polu **Cropped Image** (po lewej), prześlij mały wycinek obrazu, którego szukasz.
3.  W polu **Reference Image** (po prawej), prześlij jeden lub więcej dużych obrazów, na których system ma szukać wycinka. Możesz zaznaczyć wiele plików naraz (używając Ctrl/Cmd lub przeciągając je).
4.  Gdy oba pola będą uzupełnione, kliknij przycisk **"Process image"**.
5.  Po zakończeniu przetwarzania zobaczysz:
    * Obraz referencyjny z zaznaczonym najlepszym dopasowaniem.
    * Liczbę znalezionych punktów charakterystycznych (matches).
    * Opis wygenerowany przez AI (geoInfo).
