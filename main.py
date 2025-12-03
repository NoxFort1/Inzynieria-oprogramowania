import cv2
import numpy as np
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import base64
from google import genai
from google.genai import types

UPLOAD_FOLDER = 'uploads'
GOOGLE_API_KEY = "AIzaSyBVV1mBYTKHxTUBnXM0GBsPnSfz1sNWZek" 

def googleApi(image_bytes):
    try:
        if not GOOGLE_API_KEY:
            return "Błąd: Brak klucza API Gemini."

        client = genai.Client(api_key=GOOGLE_API_KEY)

        # Define the geolocation analysis prompt
        geoPrompt = """
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

        response = client.models.generate_content(
            model='gemini-2.5-flash',  
            config=types.GenerateContentConfig(
                temperature=0.4,
            ),
            contents=[
                types.Part.from_bytes(
                    data=image_bytes,
                    mime_type='image/jpeg',
                ),
                geoPrompt
            ]
        )
        return response.text
    except Exception as e:
        return f"Błąd Gemini API: {str(e)}"

def alg(img1_name, img2_name): # img1_name - cutout (plik), img2_name - ref (plik)
    try:
        path_cutout = os.path.join(UPLOAD_FOLDER, img1_name)
        path_ref = os.path.join(UPLOAD_FOLDER, img2_name)

        cutoutColor = cv2.imread(path_cutout)
        refColor = cv2.imread(path_ref)

        if refColor is None or cutoutColor is None:
            return {"err": "Failed to load images"}

        refGray = cv2.cvtColor(refColor, cv2.COLOR_BGR2GRAY)
        cutoutGray = cv2.cvtColor(cutoutColor, cv2.COLOR_BGR2GRAY)

        # CLAHE
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        refGray = clahe.apply(refGray)
        cutoutGray = clahe.apply(cutoutGray)

    except cv2.error as err:
        return {"err": "Image processing error"}

    # SIFT
    sift = cv2.SIFT_create()

    keyPointsRef, desRef = sift.detectAndCompute(refGray, None)
    keyPointsCutout, desCutout = sift.detectAndCompute(cutoutGray, None)

    if desRef is None or desCutout is None or len(keyPointsRef) == 0 or len(keyPointsCutout) == 0:
        return {"err": "No key points detected in images"}

    # Matching feature
    matcher = cv2.BFMatcher(cv2.NORM_L2)

    # knnMatches
    knnMatches = matcher.knnMatch(desCutout, desRef, k=2)

    good = []
    rThresh = 0.75

    for matchPair in knnMatches:
        if len(matchPair) == 2:
            m, n = matchPair
            if m.distance < rThresh * n.distance:
                good.append(m)

    # RANSAC
    minMatchCount = 10

    if len(good) > minMatchCount:
        srcPts = np.float32([keyPointsCutout[m.queryIdx].pt for m in good]).reshape(-1, 1, 2)
        dstPts = np.float32([keyPointsRef[m.trainIdx].pt for m in good]).reshape(-1, 1, 2)

        M, mask = cv2.findHomography(srcPts, dstPts, cv2.RANSAC, 5.0)

        if M is None:
            return {"err": "Failed to find homography"}

        matchesMask = mask.ravel().tolist()

        h, w = cutoutGray.shape
        pts = np.float32([[0, 0], [0, h - 1], [w - 1, h - 1], [w - 1, 0]]).reshape(-1, 1, 2)
        dst = cv2.perspectiveTransform(pts, M)

        # Ramka
        refColorWithBox = cv2.polylines(refColor.copy(), [np.int32(dst)], True, (0, 255, 255), 3, cv2.LINE_AA)
        
        draw_params = dict(matchColor=(0, 255, 0),
                        singlePointColor=None,
                        matchesMask=matchesMask,
                        flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS)

        imgMatches = cv2.drawMatches(cutoutColor, keyPointsCutout, refColorWithBox, keyPointsRef, good, None, **draw_params)

        success, buffer = cv2.imencode('.png', imgMatches)
        if not success:
            return {"err": "Failed to encode output image"}

        imgBase64 = base64.b64encode(buffer).decode('utf-8')

        try:
            path_to_read = os.path.join(UPLOAD_FOLDER, img2_name) 
            with open(path_to_read, 'rb') as f:
                ref_image_bytes = f.read()
            
            gemini_response_text = googleApi(ref_image_bytes)
        except Exception as api_err:
            gemini_response_text = f"Błąd podczas wywoływania AI: {str(api_err)}"
            print(gemini_response_text)

        return {
            "status": "success",
            "matches": len(good),
            "result": imgBase64,
            "geoInfo": gemini_response_text
        }
    else:
        return {"err": f"Insufficient number of matches. Found {len(good)}, required {minMatchCount}."}


# FLASK APP
app = Flask(__name__)
CORS(app)

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['uploadFolder'] = UPLOAD_FOLDER

@app.route('/api/przetworz', methods=['POST'])
def handleUpload():
    path1 = ""
    path2 = ""
    try:
        if 'obraz1' not in request.files or 'obraz2' not in request.files:
            return jsonify({"Error": "Brak plików obraz1 lub obraz2"}), 400

        file1 = request.files['obraz1'] # cutout
        file2 = request.files['obraz2'] # ref
        
        path1 = os.path.join(app.config['uploadFolder'], file1.filename)
        path2 = os.path.join(app.config['uploadFolder'], file2.filename)
        
        file1.save(path1)
        file2.save(path2)
        
        result = alg(file1.filename, file2.filename)

        if os.path.exists(path1): os.remove(path1)
        if os.path.exists(path2): os.remove(path2)

        return jsonify(result)

    except Exception as e:
        if os.path.exists(path1): os.remove(path1)
        if os.path.exists(path2): os.remove(path2)
        print(f"BŁĄD SERWERA: {str(e)}") 
        return jsonify({"Error": str(e)}), 500

if __name__  == '__main__':
    app.run(debug=True, port=5000)