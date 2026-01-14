<<<<<<< HEAD
import os
=======
import io
>>>>>>> c594f8b68f2b815bfa0b481812097726e3e52da9
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv 
from config import Config
from services.cv_service import ImageMatcher
from services.ai_service import GeoAnalyzer

load_dotenv()
app = Flask(__name__)
CORS(app)
Config.init_app(app)

matcher = ImageMatcher()
geo_analyzer = GeoAnalyzer(Config.GOOGLE_API_KEY)

@app.route('/api/przetworz', methods=['POST'])
def handle_upload():
<<<<<<< HEAD
    file1 = request.files.getlist('obraz1') # cutout
    file2 = request.files.getlist('obraz2') # ref
    
    if not file1 or not file2:
            return jsonify({"Error": "Brak wymaganych plików"}), 400
    print(file1[0].filename)
    path1 = os.path.join(app.config['UPLOAD_FOLDER'], file1[0].filename)
    # path2 = os.path.join(app.config['UPLOAD_FOLDER'], file2.filename)

    try:
        file1 = file1[0]
        file1.save(path1)
        # file2.save(path2)
        
        # Computer Vision Processing
        # cv_result = matcher.process(path1, path2)
        max_matches = -1
        best_file = None
        paths2 = []
        for i, file2 in enumerate(file2):
            path2 = os.path.join(app.config['UPLOAD_FOLDER'], file2.filename)
            paths2.append(path2)
            file2.save(path2)
            cv_result = matcher.process(path1, path2)
            if "err" in cv_result:
                # print(f"BŁĄD PRZY PRZETWARZANIU OBRAZU: {cv_result['err']}")
                return jsonify({"Error": f"Błąd podczas przetwarzania obrazu {cv_result['err']}"}), 400
=======
    file1 = request.files.getlist('obraz1') 
    file2_list = request.files.getlist('obraz2') 
    
    if not file1 or not file2_list:
        return jsonify({"error": "Brak wymaganych plików"}), 400

    try:
        cutout_bytes = file1[0].read()
        
        max_matches = 0
        best_result = None

        for ref_file in file2_list:
            ref_bytes = ref_file.read()
            cv_result = matcher.process(cutout_bytes, ref_bytes)
            
            if "err" in cv_result:
                continue
>>>>>>> c594f8b68f2b815bfa0b481812097726e3e52da9
            
            current_matches = cv_result.get("matches", 0)
            if current_matches > max_matches:
                max_matches = current_matches
<<<<<<< HEAD
                best_file = cv_result

        ai_result_text = geo_analyzer.analyze_image(path1)

        # ai_result_text = "Lorem"

        final_response = {
            "status": "success",
            "matches": max_matches,
            "result": best_file.get("result_base64", ""),
            "geoInfo": ai_result_text
        }
=======
                best_result = cv_result
    
        ai_result_text = geo_analyzer.analyze_image(cutout_bytes)
        final_response = {
            "status": "success",
            "matches": max_matches,
            "geoInfo": ai_result_text,
            "result": best_result.get("result_base64", "") if best_result else ""
        }
        
        if not best_result:
             final_response["message"] = "Brak dopasowania."
>>>>>>> c594f8b68f2b815bfa0b481812097726e3e52da9

        return jsonify(final_response)

    except Exception as e:
        print(f"Błąd serwera: {str(e)}")
<<<<<<< HEAD
        return jsonify({"Error": str(e)}), 500
        
    finally:
        if os.path.exists(path1): os.remove(path1)
        for path in paths2:
            if os.path.exists(path): os.remove(path)
=======
        return jsonify({"error": str(e)}), 500
>>>>>>> c594f8b68f2b815bfa0b481812097726e3e52da9

if __name__  == '__main__':
    app.run(debug=True, port=5000)