from flask import Flask, render_template, redirect, request, url_for, flash, send_from_directory
from flask_ckeditor import CKEditor
from werkzeug.utils import secure_filename
from flask_bootstrap import Bootstrap
from form import VisistorForm, RegisterForm, LoginForm, UserConditionForm
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from flask_login import UserMixin, LoginManager, login_user, logout_user, login_required, current_user
from datetime import datetime
import os
import json
from glob import glob
from p import _main_
from functions import CalculatePerson, calculate_consumption, get_coordinate, find_food
from functools import wraps

############################### initialize flask app###############

app = Flask(__name__)
app.config['SECRET_KEY'] = 'THISISASECRETKEY'
ckeditor = CKEditor(app)
Bootstrap(app)

###################################################################

#########################set for DB##################################
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///user_food.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

###########################################################################

############################## set for flask-login###########################
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
login_manager.login_message = "請登入你的email和密碼!"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


####################################################################################

##############################CONFIGURE TABLES####################################

class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(200), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    user_name = db.Column(db.String(200), nullable=False)
    condition = relationship("UserCondition", back_populates="user")


class UserCondition(db.Model):
    __tablename__ = "userconditions"
    id = db.Column(db.Integer, primary_key=True)
    gender = db.Column(db.String(5), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    height = db.Column(db.Integer, nullable=False)
    weight = db.Column(db.Float, nullable=False)
    stregnth = db.Column(db.String(5), nullable=False)
    daily_calories_consumption = db.Column(db.Float, nullable=True)
    daily_already_calories_consumption = db.Column(db.Float, nullable=True)
    daily_already_protien_consumption = db.Column(db.Float, nullable=True)
    daily_already_consumption = db.Column(db.String(500), nullable=True)
    english_label_list = db.Column(db.String(500), nullable=True)
    chinese_decided_label = db.Column(db.String(500), nullable=True)
    image_path = db.Column(db.String(500), nullable=True)
    image_analyze_path_list = db.Column(db.String(500), nullable=True)
    time = db.Column(db.String(250), nullable=True)
    comment = db.Column(db.Text, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = relationship("User", back_populates="condition")


class Guest(db.Model):
    __tablename__ = "guest"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(5), nullable=False)
    height = db.Column(db.Integer, nullable=False)
    weight = db.Column(db.Float, nullable=False)
    stregnth = db.Column(db.String(5), nullable=False)
    english_label_list = db.Column(db.String(500), nullable=True)
    image_path = db.Column(db.String(500), nullable=True)
    image_analyze_path_list = db.Column(db.String(500), nullable=True)


db.create_all()
################################################################################################

################set for file upload###############################################################

UPLOAD_FOLDER = "static\\upload_images"
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


#################################################################################################

##############################set for special decorator###########################################
def visitor_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        #If id is not 1 then return abort with 403 error
        if current_user.is_authenticated:
            flash(f"Hi,{current_user.user_name}你不是訪客喔!快來記錄你的日誌吧!", "primary")
            return render_template("userdata.html")
        #Otherwise continue with the route function
        return f(*args, **kwargs)
    return decorated_function



##################################################################################################

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        user_name = form.username.data

        password_salted_and_hashed = generate_password_hash(password, method='pbkdf2:sha256', salt_length=16)
        if not User.query.filter_by(email=email).first():
            new_user = User(
                email=email,
                password=password_salted_and_hashed,
                user_name=user_name,
            )
            db.session.add(new_user)
            db.session.commit()
            flash(f"您好,{new_user.user_name}, 恭喜註冊成功, 麻煩你登入帳號密碼", "success")
            return redirect(url_for("login"))
        else:
            flash("你的郵件已註冊，請重新註冊或登入", "warning")
            return redirect(url_for("register"))
    return render_template("register.html", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):

            login_user(user)
            flash(f"歡迎回來{user.user_name}, 來上傳你今天的攝取的美食吧!", "primary")

            return redirect(url_for("userdata"))
        else:
            flash('你的帳號或密碼錯誤，請重新輸入')
            redirect(url_for("login"))
    return render_template("login.html", form=form)


@app.route('/logout')
def logout():
    logout_user()
    flash('請每天持之以恆的紀錄和控制，期待下次見面!', 'success')
    return redirect(url_for('home'))


h5_list = []
h5_name_list = []

h5_files = glob(r"C:\Users\Casper\Desktop\yolov3\keras-yolo3-master\weights\*")
for h5_file in h5_files:
    h5_list.append(h5_file)
    h5_name = h5_file.split("\\")[-1]
    h5_name_list.append(h5_name)


@app.route("/user_upload", methods=["GET", "POST"])
@login_required
def user_upload():
    form = UserConditionForm()
    method = request.method
    if request.method == 'POST':

        submit = request.form["send"]
        print(submit)

        if submit == '預覽圖片':

            height = form.height.data
            weight = form.weight.data
            age = form.age.data
            gender = form.gender.data
            stregnth = form.stregnth.data
            comment = form.comment.data

            image = form.image.data

            print(height, weight, age, gender, stregnth, comment, image)

            if 'image' not in request.files:
                print(request.files)
                flash('你的圖片格式不符合', 'warning')
                return redirect(request.url)
            file = image
            if file.filename == '':
                flash('沒有選擇圖片,請選擇一張', 'warning')
                return redirect(request.url)
            if file and allowed_file(file.filename):
                print('hello im here------------->', file)
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                print(file_path)
                file.save(file_path)
                flash("圖片上傳成功", "success")
                user_condition = UserCondition(
                    gender=gender,
                    height=height,
                    weight=weight,
                    age=age,
                    stregnth=stregnth,
                    comment=comment,
                    user=current_user,
                    image_path=file_path,
                    time=datetime.today().strftime("%Y/%m/%d %H:%M:%S")
                )
                db.session.add(user_condition)
                db.session.commit()
                print("預覽圖片231")
                print(user_condition.id, 232)
                id = user_condition.id
                return render_template("user_condition.html", form=form, file_path=file_path, method=method, id=id)

        if submit == "重新上傳":
            user_condition = UserCondition.query.get(current_user.condition[-1].id)
            print(user_condition.id)

            image_path = user_condition.image_path
            os.remove(image_path)
            db.session.delete(user_condition)
            db.session.commit()
            flash("請重新選擇要上傳圖片", 'infor')
            return render_template("user_condition.html", form=form, method=method)

        if submit == "確認送出":

            user_condition = UserCondition.query.get(current_user.condition[-1].id)
            print(user_condition.id)
            flash("資料已送出",'success')
            return redirect(url_for('predict', user_id=user_condition.id))

    return render_template("user_condition.html", form=form, method=method)


@app.route("/guest_upload", methods=["GET", "POST"])
@visitor_required
def guest_upload():
    form = VisistorForm()
    method = request.method
    if request.method == 'POST':

        submit = request.form["send"]

        if submit == '預覽圖片':

            name = form.name.data
            height = form.height.data
            weight = form.weight.data
            age = form.age.data
            gender = form.gender.data
            stregnth = form.stregnth.data
            image = form.image.data

            print(name, height, weight, age, gender, stregnth, image)

            if 'image' not in request.files:
                print(request.files)
                flash('不正確的圖片檔案，請重新選擇', 'warining')
                return redirect(request.url)
            file = image
            if file.filename == '':
                flash('沒有選擇圖片，請選擇', 'warining')
                return redirect(request.url)
            if file and allowed_file(file.filename):
                print('hello im here------------->', file)
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                flash('圖片上傳成功', 'success')
                print(file_path)

                visistor = Guest(
                    name=name,
                    height=height,
                    weight=weight,
                    age=age,
                    gender=gender,
                    stregnth=stregnth,
                    image_path=file_path
                )
                db.session.add(visistor)
                db.session.commit()

                # path_list.append(file_path)

                file.save(file_path)

                return render_template("guest.html", form=form, file_path=file_path, method=method)

        if submit == "重新上傳":
            visistor = Guest.query.filter_by(name=form.name.data).first()
            image_path = visistor.image_path
            os.remove(image_path)
            db.session.delete(visistor)
            db.session.commit()
            flash('請重新選擇圖片', 'infor')
            return render_template("guest.html", form=form, method=method)

        if submit == "確認送出":
            visistor = Guest.query.filter_by(name=form.name.data).first()
            flash('資料已送出', 'success')

            return redirect(url_for('predict', user_id=visistor.id))

    return render_template("guest.html", form=form, method=method)


@app.route("/predict", methods=["GET"])
def predict():
    produced_pic_path = []
    produced_content_list = []
    english_label_list = []
    user_id = request.args.get("user_id")
    print("我在predict 328", user_id)
    if current_user.is_authenticated:
        condition = UserCondition.query.get(user_id)
    else:
        condition = Guest.query.get(user_id)



    for i in range(len(h5_list)):
        label_list, save_path = _main_(r"C:\Users\Casper\Desktop\yolov3\config.json",
                                       h5_list[i], condition.image_path)

        print("預測結果: ", label_list)
        print("預測圖片儲存路徑: ", save_path)

        produced_content_list.append(calculate_consumption(label_list)[0])

        english_label_list.append(label_list)
        produced_pic_path.append(save_path)

    labels = produced_content_list
    labels_json = json.dumps(english_label_list)
    pics = produced_pic_path
    pics_json = json.dumps(pics)

    condition.english_label_list = labels_json
    condition.image_analyze_path_list = pics_json
    db.session.commit()

    lens = len(pics)
    h5s = h5_name_list
    return render_template("predict.html", labels=labels, pics=pics, lens=lens, h5s=h5s, user_id=user_id)


@app.route("/analyze")
def analyze():
    pic_id = request.args.get("pic_id")
    user_id = request.args.get("user_id")
    print(pic_id, user_id)

    if current_user.is_authenticated:
        condition = UserCondition.query.get(user_id)
        print("我在這analyze 389", condition.id)
    else:
        condition = Guest.query.get(user_id)

    english_label_list = json.loads(condition.english_label_list)

    user = CalculatePerson(condition)
    BMI_situation = user.calculate_bmi()
    user_daily_calories = user.calculate_calories_daily()
    food_detection, calories_aleady_consumption, protien_already_consumption = \
        calculate_consumption(english_label_list[int(pic_id)])
    user_can_calories = user.calculate_calories(calories_aleady_consumption)
    work_list = user.exercise_caloris_consumption(user_can_calories)
    list_1 = [BMI_situation, user_daily_calories, food_detection, calories_aleady_consumption,
              protien_already_consumption, user_can_calories, work_list]
    print(list_1)

    if current_user.is_authenticated:
        condition.daily_calories_consumption = user_daily_calories
        condition.daily_already_calories_consumption = calories_aleady_consumption
        condition.daily_already_protien_consumption = protien_already_consumption
        condition.chinese_decided_label = food_detection
        db.session.commit()
        print("我被儲存")

    return render_template("analyze.html", list=list_1, condition=condition)


@app.route("/userdata", methods=["GET", "POST"])
@login_required
def userdata():
    totoal_calories_consumption = 0
    total_protrien_consumption = 0
    image_paths = []
    BMI_situations = []

    user_login = User.query.get(current_user.id)
    conditions = user_login.condition
    print(conditions,425)

    if conditions:
        for condition in conditions:
            time = datetime.strptime(condition.time, "%Y/%m/%d %H:%M:%S")
            time_str = time.strftime("%Y/%m/%d")
            today = datetime.today().strftime("%Y/%m/%d")
            print("time = today", time_str == today, 435, "行")
            # if time_str == today:
            user_name = user_login.user_name
            gender = condition.gender
            age = condition.age
            height = condition.height
            weight = condition.weight
            stregnth = condition.stregnth
            daily_calories_consumption = condition.daily_calories_consumption
            daily_already_calories_consumption = condition.daily_already_calories_consumption
            daily_already_protien_consumption = condition.daily_already_protien_consumption
            chinese_decided_label = condition.chinese_decided_label
            image_analyze_path_list = condition.image_analyze_path_list
            comment = condition.comment

            user = CalculatePerson(condition)
            BMI_situation = user.calculate_bmi()
            BMI_situations.append(BMI_situation)

            if condition.image_path:
                image_path = condition.image_path.replace("\\", "/")
                image_paths.append(image_path)
            else:
                image_path = "static/img/calculate.jpg"

            totoal_calories_consumption = totoal_calories_consumption + daily_already_calories_consumption
            total_protrien_consumption = total_protrien_consumption + daily_already_protien_consumption

            print(user_name, gender, age, height, weight, stregnth, daily_calories_consumption,
                  daily_already_calories_consumption, daily_already_protien_consumption, chinese_decided_label,
                  image_path,
                  image_analyze_path_list, time, comment)

        print(conditions[-1])
        user = CalculatePerson(conditions[-1])
        user_can_calories = user.calculate_calories(totoal_calories_consumption)
        work_list = user.exercise_caloris_consumption(user_can_calories)
        lens = len(conditions)

        print(image_paths, BMI_situations, "我在472 userdata")
        return render_template("userdata.html", conditions=conditions, image_paths=image_paths,
                           BMI_situations=BMI_situations, totoal_calories_consumption=totoal_calories_consumption,
                           total_protrien_consumption=total_protrien_consumption,
                           user_can_calories=user_can_calories, work_list=work_list, lens=lens, today=today)

    return render_template("userdata.html", conditions=conditions)


@app.route("/edit_condition/<int:user_id>", methods=["GET", "POST"])
@login_required
def edit_condition(user_id):
    form = UserConditionForm()

    method = request.method
    user_condition = UserCondition.query.get(user_id)

    if request.method == 'POST':

        submit = request.form["send"]

        if submit == '預覽圖片':

            height = form.height.data
            weight = form.weight.data
            age = form.age.data
            gender = form.gender.data
            stregnth = form.stregnth.data
            comment = form.comment.data

            image = form.image.data

            print(height, weight, age, gender, stregnth, comment, image)

            if 'image' not in request.files:
                print(request.files)
                flash('不正確的圖片格式', 'warning')
                return redirect(request.url)
            file = image
            if file.filename == '':
                flash('沒有選擇檔案', 'warning')
                return redirect(request.url)
            if file and allowed_file(file.filename):
                print('hello im here------------->', file)
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)

                user_condition = UserCondition.query.get(user_id)
                user_condition.gender = gender
                user_condition.height = height
                user_condition.weight = weight
                user_condition.age = age
                user_condition.stregnth = stregnth
                user_condition.comment = comment
                user_condition.image_path = file_path

                db.session.commit()
                flash('圖片上傳成功', 'success')
                return render_template("user_condition.html", form=form, file_path=file_path, method=method)

        if submit == "重新上傳":
            user_condition = UserCondition.query.get(user_id)
            image_path = user_condition.image_path
            os.remove(image_path)
            flash('請重新選擇圖片', 'warning')
            return render_template("user_condition.html", form=form, method=method)

        if submit == "確認送出":
            user_condition = UserCondition.query.get(user_id)
            flash("圖片上傳成功", 'success')
            return redirect(url_for('predict', user_id=user_condition.id))

        return render_template("user_condition.html", form=form, method=method)


@app.route("/delete_condition")
def delete_condition():
    user_id = request.args.get("user_id")
    if current_user.is_authenticated:
        condition = UserCondition.query.get(user_id)
        image_path = condition.image_path
        os.remove(image_path)

        image_analyze_path_list = json.loads(condition.image_analyze_path_list)
        for image_analyze_path in image_analyze_path_list:
            os.remove(image_analyze_path)

        db.session.delete(condition)
        db.session.commit()
        flash("資料已刪除", 'success')
        return redirect(url_for("userdata"))

    else:
        guest = Guest.query.get(user_id)

        image_path = guest.image_path
        os.remove(image_path)

        image_analyze_path_list = json.loads(guest.image_analyze_path_list)
        for image_analyze_path in image_analyze_path_list:
            os.remove(image_analyze_path)

        db.session.delete(guest)
        db.session.commit()
        flash("在重新上傳分析吧!", 'infor')
        return redirect(url_for("guest_upload"))


@app.route("/upload_pdf")
def upload_pdf():
    return send_from_directory('static', filename="pdf_file/project2.pdf")


if __name__ == "__main__":
    app.run(debug=True)
