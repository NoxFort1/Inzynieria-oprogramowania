import cv2
import numpy as np
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import base64

def alg(img1, img2): #img1 - cutout, img2 - ref
    print(img1)
    try:
        cutoutColor = cv2.imread(f'./uploads/{img1}')
        refColor = cv2.imread(f'./uploads/{img2}')

        if refColor is None or cutoutColor is None:
            return {"err": "Failed to load images"}
            exit()

        refGray = cv2.cvtColor(refColor, cv2.COLOR_BGR2GRAY)
        cutoutGray = cv2.cvtColor(cutoutColor, cv2.COLOR_BGR2GRAY)

    except cv2.error as err:
        return {"err": "Image processing error"}
        exit()

    # SIFT
    sift = cv2.SIFT_create()

    keyPointsRef, desRef = sift.detectAndCompute(refGray, None)
    keyPointsCutout, desCutout = sift.detectAndCompute(cutoutGray, None)

    if desRef is None or desCutout is None or len(keyPointsRef) == 0 or len(keyPointsCutout) == 0:
        return {"err": "No key points detected in images"}
        exit()

    # Matching feature
    matcher = cv2.BFMatcher(cv2.NORM_L2)

    # knnMatches
    knnMatches = matcher.knnMatch(desCutout, desRef, k=2)

    good = []
    rThresh = 0.75

    for matchPair in knnMatches:
        if len(matchPair) == 2:
            m, n = matchPair  # m to pierwsze najlepsze dopasowanie a n to drugie
            if m.distance < rThresh * n.distance:  # Jeśli m jest znacznie lepsze niż n (o 25%) to je  akceptujemy
                good.append(m)


    # RANSAC
    minMatchCount = 10

    if len(good) > minMatchCount:
        # Współrzędne punktów z 'cutout' (obraz "query")
        srcPts = np.float32([keyPointsCutout[m.queryIdx].pt for m in good]).reshape(-1, 1, 2)
        # Współrzędne punktów z 'ref' (obraz "train")
        dstPts = np.float32([keyPointsRef[m.trainIdx].pt for m in good]).reshape(-1, 1, 2)

        # homografia RANSAC
        M, mask = cv2.findHomography(srcPts, dstPts, cv2.RANSAC, 5.0)

        if M is None:
            print("Failed to find homography.")
            return {"err": "Failed to find homography"}
            exit()

        # Maska inliers
        matchesMask = mask.ravel().tolist()

        # Pobranie wymiarow obrazu  aby narysować ramkę
        h, w = cutoutGray.shape
        #  rogi obrazu 'cutout'
        pts = np.float32([[0, 0], [0, h - 1], [w - 1, h - 1], [w - 1, 0]]).reshape(-1, 1, 2)

        # Przekształcenie rogow wycinka do perspektywy obrazu ref używając homografii M
        dst = cv2.perspectiveTransform(pts, M)
    # ramka
        refColorWithBox = cv2.polylines(refColor.copy(), [np.int32(dst)], True, (0, 255, 255), 3, cv2.LINE_AA)
        draw_params = dict(matchColor=(0, 255, 0),  # Zielone linie dla "inliers"
                        singlePointColor=None,
                        matchesMask=matchesMask,  # dopasowania z maski RANSAC
                        flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS)

        # finalny obraz z dopasowaniami (tylko inliers)
        imgMatches = cv2.drawMatches(cutoutColor, keyPointsCutout, refColorWithBox, keyPointsRef, good, None, **draw_params)

        success, buffer = cv2.imencode('.png', imgMatches)
        if not success:
            return {"err": "Failed to encode output image"}

        imgBase64 = base64.b64encode(buffer).decode('utf-8')

        # cv2.imshow('Wynik dopasowania', imgMatches)
        # cv2.waitKey(0)
        return {
                    "status": "success",
                    "matches": len(good),
                    "result": imgBase64
                }
    else:
        return {"err": f"Insufficient number of matches. Found {len(good)}, required {minMatchCount}."}


app = Flask(__name__)
CORS(app)

uploadFolder = 'uploads'
if not  os.path.exists(uploadFolder):
    os.makedirs(uploadFolder)

app.config['uploadFolder'] = uploadFolder
#ENDPOINT
@app.route('/api/przetworz', methods=['POST'])
def handleUpload():
    try:
        file1 = request.files['obraz1'] # cutout
        file2 = request.files['obraz2'] # ref
        path1 = os.path.join(app.config['uploadFolder'], file1.filename)
        path2 = os.path.join(app.config['uploadFolder'], file2.filename)
        file1.save(path1)
        file2.save(path2)
        
        result = alg(file1.filename, file2.filename)

        os.remove(path1)
        os.remove(path2)

        return jsonify(result)
    

    except Exception:
        return jsonify({"Error": str(Exception)}, 500)
    

if __name__  == '__main__':
    # server start
    app.run(debug=True, port=5000)