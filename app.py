import stripe
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from models import db, User, bcrypt
import random

app = Flask(__name__)
app.config['SECRET_KEY'] = 'sk_test_51R3LQwR8IZpCrBoe1Nk9eAjMidDgeluoHErD0O69R1T7b3QW0nsWpC0h79d3aqqrtoD1T67Dx1WnYbxYKzFqGs6D00zZGlkA20'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://test_bein_user:E2XnZwIF1a8w5pYgJpE2728zNbo1LWd4@dpg-cvc6nbd2ng1s73f8acv0-a.oregon-postgres.render.com/test_bein'

db.init_app(app)
bcrypt.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # ユーザー名が既にデータベースに存在するか確認
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('そのユーザー名はすでに登録されています。別の名前を選んでください。', 'danger')
            return redirect(url_for('register'))

        # ユーザーが存在しない場合、新規ユーザーを作成
        user = User(username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash('登録が完了しました！', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('dashboard'))
        flash('ログインに失敗しました')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')


app.config.from_object('config')

stripe.api_key = app.config['STRIPE_SECRET_KEY']

@app.route('/buy_coins', methods=['POST'])
@login_required
def buy_coins():
    try:
        data = request.get_json()  # JSONデータを受け取る
        if not data or "amount" not in data:
            return jsonify({"error": "Invalid request, missing amount"}), 400
        
        amount = int(data["amount"])  # JSON から amount を取得
        total_price = amount * app.config['COIN_PRICE']

        # Debugging log
        print(f"Received request: amount={amount}, total_price={total_price}")

        # Stripeで支払いIntentを作成
        intent = stripe.PaymentIntent.create(
            amount=total_price,
            currency="jpy",
            payment_method_types=["card"]
        )

        return jsonify({"clientSecret": intent.client_secret})

    except Exception as e:
        print(f"Error in buy_coins: {str(e)}")
        return jsonify({"error": str(e)}), 400


@app.route('/confirm_payment', methods=['POST'])
@login_required
def confirm_payment():
    try:
        data = request.get_json()  # JSONデータを受け取る
        payment_id = data.get('payment_id')  # フロントエンドから渡されるStripeの支払いID
        
        # すでに支払いが成功しているかチェック
        payment_intent = stripe.PaymentIntent.retrieve(payment_id)
        if payment_intent.status != "succeeded":
            return jsonify({'error': '支払いが完了していません。'}), 400

        # コインを増やす
        amount = int(data.get('amount'))
        current_user.coins += amount
        db.session.commit()

        return jsonify({'message': '購入成功', 'new_coins': current_user.coins})
    except Exception as e:
        return jsonify({'error': str(e)}), 400
    
@app.route('/buy_coins_page')
@login_required
def buy_coins_page():
    return render_template('buy_coins.html', public_key=app.config['STRIPE_PUBLIC_KEY'])

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/play_slot')
@login_required
def play_slot():
    return render_template('play_slot.html')

@app.route('/spin_slot', methods=['POST'])
@login_required
def spin_slot():
    if current_user.coins <= 0:
        return jsonify({"message": "コインが足りません", "result": ["🍒", "🔔", "⭐"]}), 400

    symbols = ["🍒", "🔔", "⭐", "🍋", "🍉"]
    result = [random.choice(symbols) for _ in range(3)]

    if result[0] == result[1] == result[2]:
        winnings = 10
        message = f"🎉 {''.join(result)} - おめでとう！{winnings}コイン獲得！"
    else:
        winnings = -1
        message = f"{''.join(result)} - はずれ！"

    current_user.coins += winnings
    db.session.commit()

    return jsonify({"message": message, "new_coins": current_user.coins, "result": result})


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
