from flask import Flask, render_template, redirect, url_for, request, session
from flask_sqlalchemy import SQLAlchemy
import os

model_directory = "/home/fareeha/face-recognition-with-liveness-web-login/face_recognition_and_liveness/face_liveness_detection"
model_path = os.path.join(model_directory, "liveness.model.h5")

# Print the model path to verify
# print('Model Path:', model_path)

# import our model from folder
from face_recognition_and_liveness.face_liveness_detection.face_recognition_liveness_app import recognition_liveness

app = Flask(__name__)
app.secret_key = 'web_app_for_face_recognition_and_liveness' # something super secret
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Users(db.Model):
    username = db.Column(db.String(100), primary_key=True)
    name = db.Column(db.String(100))
    password = db.Column(db.String(100))

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        session.pop('name', None)
        username = request.form['username']
        password = request.form['password']
        user = Users.query.filter_by(username=username).first()
        print(user)
        if user is not None and user.password == password:
            session['name'] = user.name # store variable in session
            detected_name, label_name = recognition_liveness('/home/fareeha/face-recognition-with-liveness-web-login/face_recognition_and_liveness/face_liveness_detection/liveness.model.h5',
                                                    '/home/fareeha/face-recognition-with-liveness-web-login/face_recognition_and_liveness/face_liveness_detection/label_encoder.pickle',
                                                    '/home/fareeha/face-recognition-with-liveness-web-login/face_recognition_and_liveness/face_liveness_detection/face_detector',
                                                    '/home/fareeha/face-recognition-with-liveness-web-login/face_recognition_and_liveness/face_recognition/encoded_faces.pickle',
                                                    confidence=0.5)
            if user.name == detected_name and label_name == 'real':
                return redirect(url_for('main'))
            else:
                return render_template('login_page.html', invalid_user=True, username=username, name=user.name)
        else:
            return render_template('login_page.html', incorrect=True)

    return render_template('login_page.html')

@app.route('/main', methods=['GET'])
def main():
    name = session['name']
    return render_template('main_page.html', name=name)

# if __name__ == '__main__':
#     with app.app_context():
#         db.create_all()

#         # add users to database

#         new_user = Users(username='afrah', password='123456789', name='afrah')
#         db.session.add(new_user)

#         new_user_2 = Users(username='faizfareeha', password='123456789', name='Fareeha')
#         db.session.add(new_user_2)

#         app.run(debug=True)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()

        # Check if a user exists before adding
        def add_user_if_not_exists(username, password, name):
            if not Users.query.filter_by(username=username).first():
                new_user = Users(username=username, password=password, name=name)
                db.session.add(new_user)

        # Add users if they don't exist
        add_user_if_not_exists('afrah', '123456789', 'afrah')
        add_user_if_not_exists('faizfareeha', '123456789', 'Fareeha')

        db.session.commit()  # Save changes to the database
        app.run(debug=True)

