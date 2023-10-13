from flask import Flask, render_template, request
import subprocess

app = Flask(__name__)

# Ana sayfa
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        youtube_url = request.form['youtube_url']
        
        # Python scriptinizi çalıştırın ve çıktısını alın

        command = ["python",
        "main_local.py",
        youtube_url
        ]
        result = subprocess.run(command, shell=True, text=True, stdout=subprocess.PIPE,check=True)
        result = result.stdout

        return render_template('index.html', result=result)

    return render_template('index.html', result=None)

if __name__ == '__main__':
    app.run(debug=True)
