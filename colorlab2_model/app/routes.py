from flask import render_template, request, session, redirect, url_for, jsonify
import os
from app import app
from emotion import emotion
import numpy as np

AUDIO_PATH = os.path.realpath('./app/static/audio')
SURVEY_PATH = os.path.realpath('./app/static/survey')

# TODO: page -> folder per msg
def load_pages(fname):
    with open(fname) as f:
        lines = f.read().splitlines()
    pages = {}
    for idx, line in enumerate(lines):
        # line = "page index,first page,second page"
        pages[idx+1] = line.split(',')
    return pages

pages = load_pages('pages.csv')
labels = load_pages('emotion_labels.csv')

@app.route('/')
@app.route('/index')
def index():
    session.clear()
    return render_template('start.html', title='Home')


@app.route('/question/<int:idx>', methods=['GET', 'POST'])
def question(idx):
    global pages

    if request.method == 'GET':
        if 'username' not in session:
            return redirect(url_for('index'))
        name = session['username']
    else:
        name = request.form['name']
        if not name:
            return redirect(url_for('index'))
        if 'username' not in session:
            session['username'] = name

    # done.
    if idx > len(pages):
        return render_template('end.html', title='Home')

    path = os.path.join(str(idx), pages[idx][1])
    print(path)
    return render_template(path, username=name, question_no=idx)


@app.route('/upload/<int:idx>', methods=['POST'])
def upload(idx):
    if 'username' not in session:
        return jsonify(success=False)

    name = session['username']
    dir_name = os.path.join(AUDIO_PATH, name)
    os.makedirs(dir_name, exist_ok=True)
    file_name = os.path.join(dir_name, '{}.wav'.format(idx))
    if 'file' not in request.files:
        return jsonify(success=False)

    request.files['file'].save(file_name)
    # TODO: keep the audio information so that the client would not fetch it.`
    # For this, we need to transfer the html data into the current page, not
    # rendering a new page.
    # TODO: process machine learning asyncronously after upload.
    return jsonify(response=True)


@app.route('/survey/<int:idx>', methods=['GET', 'POST'])
def survey(idx):
    global pages, labels

    if 'username' not in session:
        return redirect(url_for('index'))

    name = session['username']
    if request.method == 'GET':
        dir_name = os.path.join(AUDIO_PATH, name)
        file_name = os.path.join(dir_name, '{}.wav'.format(idx))
        if not os.path.exists(file_name):
            return redirect(url_for('question'))

        # Process wav file
        results = emotion.run(file_name)
        file_name = os.path.join(dir_name, '{}_softmax.txt'.format(idx))
        with open(file_name, 'w') as f:
            f.write(str(results))

        # this fetches the index of the maximum softmax value.
        emotion_idx = np.argmax(results)

        _, emotion_name, emotion_path = labels[emotion_idx]
        print("DEBUG: %s -> %s (%s)" % (file_name, emotion_name, emotion_path))

        file_name = file_name[file_name.index('/static'):]
        path = os.path.join(str(idx), pages[idx][2])
        return render_template(path, username=name, question_no=idx,
                               file_name=file_name, emotion_path=emotion_path)

    # POST
    else:
        if not request.form:
            return redirect(url_for('question'))

        ans_no = pages[idx][0]
        s = [ans_no]
        for key, val in request.form.items():
            s.append(key)
            s.append(val)
        s = ','.join(s) + '\n'

        os.makedirs(SURVEY_PATH, exist_ok=True)
        file_name = os.path.join(SURVEY_PATH, '{}.csv'.format(name))
        with open(file_name, 'a') as f:
            f.write(s)

        # done.
        if idx >= len(pages):
            return render_template('end.html', title='Home')
        else:
            return redirect(url_for('question', idx=idx+1))
