# Import necessary modules
import cv2
import os
from werkzeug.utils import secure_filename
from flask import Flask, request, render_template, redirect, url_for, send_from_directory

# Set the upload folder and allowed file extensions
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

# Initialize the Flask application
app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = "secret key"

# Define a function to check if a file has an allowed extension
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

# Define a function to convert an image to a sketch
def make_sketch(img):
    grayed = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    inverted = cv2.bitwise_not(grayed)
    blurred = cv2.GaussianBlur(inverted, (19, 19), sigmaX=0, sigmaY=0)
    final_result = cv2.divide(grayed, 255 - blurred, scale=256)
    return final_result

# Define a route for the home page
@app.route('/')
def home():
    return render_template('home.html')


# Define a route for the sketch page
@app.route('/sketch', methods=['POST'])
def sketch():
    download_url = None  # Initialize download_url
    if 'file' not in request.files:
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        img = cv2.imread(UPLOAD_FOLDER+'/'+filename)
        sketch_img = make_sketch(img)
        sketch_img_name = filename.split('.')[0]+"_sketch.jpg"
        _ = cv2.imwrite(UPLOAD_FOLDER+'/'+sketch_img_name, sketch_img)
        download_url = url_for('download', filename=sketch_img_name)  # Set download_url
        return render_template('home.html', org_img_name=filename, sketch_img_name=sketch_img_name, download_url=download_url)
    else:
        return render_template('home.html')


# Define a route for the download page
@app.route('/download/<path:filename>')
def download(filename):
    return send_from_directory('static/uploads', filename, as_attachment=True)

# Start the Flask development server
if __name__ == '__main__':
    app.run(debug=True)

# if __name__ == '__main__':
#     app.run(host='192.168.82.207', port=8080, debug=True)
