from flask import Flask, render_template, Response, redirect, url_for, request
import cv2
from orbfunction import findDes, findID, record_consecutive_appearances, import_images, make_noise
from exts import db
from models import BookModel
import config
import speech_recognition as sr

app=Flask(__name__)

app.config.from_object(config)

db.init_app(app)

camera = cv2.VideoCapture(0)
# stop_camera = True # Initialize the flag to False
appearance_counter = {}
finalbook = None


def generate_frames():
    images, classNames = import_images('static/ImageQuery')


    desList = findDes(images)

    while True:
        ## read the camera frame
        success, frame = camera.read()
        frame_original = frame.copy()

        frame_original = cv2.cvtColor(frame_original, cv2.COLOR_BGR2GRAY)
        id = findID(frame_original, desList)

        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg',frame)
            frame = buffer.tobytes()

        yield(b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

        if id != -1:

            theresult = record_consecutive_appearances(classNames[id], appearance_counter)

            if theresult:
                make_noise()
                global finalbook
                finalbook = classNames[id]
                print("now is : ",finalbook)

    camera.release()


@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/')
def index():
    # global stop_camera
    # stop_camera = True
    return render_template('index.html')

@app.route('/video')
def video():
    # global stop_camera
    # stop_camera = False
    return render_template('video.html')


@app.route('/result')
def result():
    user = BookModel.query.filter_by(book = finalbook).first()
    return render_template('result.html', user=user)

@app.route('/audioresult')
def audioresult():
    user = BookModel.query.filter_by(book = finalbook).first()
    return render_template('audioresult.html', user=user)


@app.route("/audio", methods=["GET", "POST"])
def audio():
    transcript = ""
    if request.method == "POST":
        print("FORM DATA RECEIVED")

        if "file" not in request.files:
            return redirect(request.url)

        file = request.files["file"]
        if file.filename == "":
            return redirect(request.url)

        if file:
            recognizer = sr.Recognizer()
            audioFile = sr.AudioFile(file)
            with audioFile as source:
                data = recognizer.record(source)
            transcript = recognizer.recognize_google(data, language='en-IN')

    global finalbook
    finalbook = transcript
    print("now is : ", finalbook)
    return render_template('audio.html', transcript=transcript)



if __name__=="__main__":
    app.run(debug=True, threaded=True)

