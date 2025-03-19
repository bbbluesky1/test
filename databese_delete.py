from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import text

app = Flask(__name__)

# PostgreSQLの接続設定
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://test_bein_user:E2XnZwIF1a8w5pYgJpE2728zNbo1LWd4@dpg-cvc6nbd2ng1s73f8acv0-a.oregon-postgres.render.com/test_bein'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# データベースインスタンス
db = SQLAlchemy(app)

# テーブル削除用関数
def drop_tables():
    with app.app_context():
        # テーブル削除: user テーブルをダブルクォートで囲む
        db.session.execute(text('DROP TABLE IF EXISTS "comment", "post", "user" CASCADE;'))  # ダブルクォートで囲む
        db.session.commit()
        print("Tables dropped successfully.")

if __name__ == '__main__':
    drop_tables()  # テーブル削除を実行
