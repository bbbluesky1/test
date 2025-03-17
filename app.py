from flask import Flask, render_template, request, jsonify
import stripe
import random

app = Flask(__name__)

# Stripe APIキー（テストキーを使用）
stripe.api_key = "sk_test_51R3LQwR8IZpCrBoe1Nk9eAjMidDgeluoHErD0O69R1T7b3QW0nsWpC0h79d3aqqrtoD1T67Dx1WnYbxYKzFqGs6D00zZGlkA20"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/create-checkout-session', methods=['POST'])
def create_checkout_session():
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {'name': 'Game Credits'},
                    'unit_amount': 500,
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url='http://localhost:5000/success',
            cancel_url='http://localhost:5000/cancel',
        )
        return jsonify({'id': session.id})
    except Exception as e:
        return jsonify(error=str(e)), 403

@app.route('/success')
def success():
    return "<h1>Payment successful! Credits added.</h1>"

@app.route('/cancel')
def cancel():
    return "<h1>Payment canceled.</h1>"

@app.route('/slot')
def slot():
    return render_template('slot.html')

@app.route('/spin', methods=['POST'])
def spin():
    symbols = ['🍒', '🍋', '🔔', '💎', '🍉']
    result = [random.choice(symbols) for _ in range(3)]
    win = len(set(result)) == 1
    return jsonify({'result': result, 'win': win})

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=10000)
