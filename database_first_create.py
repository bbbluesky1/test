from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

# PostgreSQLの接続設定
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://test_bein_user:E2XnZwIF1a8w5pYgJpE2728zNbo1LWd4@dpg-cvc6nbd2ng1s73f8acv0-a.oregon-postgres.render.com/test_bein'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# データベースインスタンス
db = SQLAlchemy(app)

# ユーザーモデル（テーブル名を変更）
class User(db.Model):
    __tablename__ = 'users'  # テーブル名を明示的に指定
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    posts = db.relationship('Post', backref='author', lazy=True)
    comments = db.relationship('Comment', backref='author', lazy=True)

    def __repr__(self):
        return f'<User {self.username}>'

# 投稿モデル
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # users.idに変更
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)
    comments = db.relationship('Comment', backref='post', lazy=True)

    def __repr__(self):
        return f'<Post {self.title}>'

# コメントモデル
class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # users.idに変更
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Comment {self.id}>'

# データベースを作成する関数
def create_db():
    with app.app_context():
        db.create_all()  # テーブルを作成
        print("Tables created successfully.")

if __name__ == '__main__':
    create_db()  # アプリケーション起動時にデータベースを作成
    app.run(debug=True)
