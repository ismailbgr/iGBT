from flask import Flask, render_template, request, redirect, url_for
import tasks
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload_video', methods=['GET', 'POST'])
def upload_video():
    if request.method == 'POST':
        # Check if the post request has the file part
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            return redirect(request.url)
        tasks.handle_video(file)
        return redirect(url_for('index'))
    return render_template('upload_video.html')

@app.route('/upload_text', methods=['GET', 'POST'])
def upload_text():
    if request.method == 'POST':
        text = request.form['text']
        tasks.handle_text(text)
        return redirect(url_for('index'))
    return render_template('upload_text.html')

if __name__ == '__main__':
    app.run(debug=True)
