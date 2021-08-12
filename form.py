from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, PasswordField, SubmitField, IntegerField, FloatField, SelectField, RadioField
from flask_ckeditor import CKEditorField
from wtforms.validators import InputRequired, Email, Length, NumberRange, DataRequired, EqualTo


class VisistorForm(FlaskForm):
    name = StringField(label="姓名", validators=[InputRequired(), Length(min=3, max=100)], render_kw={"value": "Visistor"})
    height = FloatField(label="身高", validators=[InputRequired(), NumberRange(min=0)],
                        render_kw={"placeholder": "請輸入您的身高(cm)"})
    weight = FloatField(label="體重", validators=[InputRequired(), NumberRange(min=0)],
                       render_kw={"placeholder": "請輸入您的體重(kg)"})
    age = IntegerField(label="年齡", validators=[InputRequired(), NumberRange(min=0, max=120)],
                       render_kw={"placeholder": "請輸入您的年齡"})
    gender = SelectField(label="性別", choices=[("男", "男"), ("女", "女")], validators=[DataRequired()])
    stregnth = SelectField(label="運動強度", choices=[('1', '弱'), ('2', '中等'), ('3', '強')], validators=[DataRequired()])
    image = FileField(label="菜色圖片上傳", validators=[FileRequired()])
    submit= SubmitField("確認送出")


class RegisterForm(FlaskForm):
    email = StringField(label="郵件", validators=[InputRequired("請填寫此欄位"), Email("請輸入正確email格式")],
                        render_kw={"placeholder": "請輸入你的email"})
    password = PasswordField(label="密碼", validators=[InputRequired("請填寫此欄位"), Length(min=8, message="密碼最少8位")],
                             render_kw={"placeholder": "請輸入你的密碼,最短8位"})
    password_confirmed = PasswordField(label="確認密碼", validators=[InputRequired("請填寫此欄位"),
                EqualTo("password_confirmed", "你的確認密碼和你設定的密碼不符合")], render_kw={"placeholder": "確認你註冊密碼"})
    username = StringField(label="用戶名稱", validators=[InputRequired("請填寫此欄位"), Length(min=3, message="最少三位")],
                           render_kw={"placeholder": "請輸入你的用戶名稱,最短3位"})
    submit = SubmitField(label="註冊")


class LoginForm(FlaskForm):
    email = StringField(label="郵件", validators=[InputRequired(), Email()], render_kw={"placeholder": "請輸入你的email"})
    password = PasswordField(label="密碼", validators=[InputRequired(), Length(min=8)],
                             render_kw={"placeholder": "請輸入你的密碼,最短8位"})
    submit = SubmitField(label="登入")


class UserConditionForm(FlaskForm):
    gender = SelectField(label="性別", choices=[("男", "男"), ("女", "女")], validators=[DataRequired("請選擇男性或女性")])
    age = IntegerField(label="年齡", validators=[InputRequired(), NumberRange(min=0, max=120)],
                       render_kw={"placeholder": "請輸入您的年齡"})
    height = FloatField(label="身高", validators=[InputRequired(), NumberRange(min=0)],
                        render_kw={"placeholder": "請輸入您的身高(cm)"})
    weight = FloatField(label="體重", validators=[InputRequired(), NumberRange(min=0)],
                        render_kw={"placeholder": "請輸入您的體重(kg)"})

    stregnth = SelectField(label="運動強度", choices=[('1', '弱'), ('2', '中等'), ('3', '強')], validators=[DataRequired()])
    image = FileField(label="菜色圖片上傳", validators=[FileRequired()])
    comment = CKEditorField(label="其他備註", render_kw={"placeholder": "其他備註事項"}, validators=[DataRequired()])
    submit = SubmitField("確認送出")


