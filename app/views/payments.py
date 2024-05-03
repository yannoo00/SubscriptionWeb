from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from flask_wtf.csrf import validate_csrf
from app.models import Subscription
from app import db, TOSSPAYMENTS_CLIENT_KEY, TOSSPAYMENTS_SECRET_KEY
import requests
import base64

bp = Blueprint('payments', __name__, url_prefix='/payments')

@bp.route('/complete', methods=['POST'])
@login_required
def complete():
    order_id = request.args.get('orderId')
    amount = request.args.get('amount')
    payment_key = request.args.get('paymentKey')

    # 액세스 토큰 발급 받기
    url = "https://api.tosspayments.com/v1/payments/confirm"
    secret_key = f"{TOSSPAYMENTS_SECRET_KEY}:"
    encoded_secret_key = base64.b64encode(secret_key.encode('utf-8')).decode('utf-8')
    headers = {
        "Authorization": f"Basic {encoded_secret_key}",
        "Content-Type": "application/json"
    }
    data = {
        "paymentKey": payment_key,
        "orderId": order_id,
        "amount": amount
    }
    res = requests.post(url, headers=headers, json=data)
    payment_data = res.json()
    print(payment_data)

    if 'paymentKey' in payment_data and 'orderId' in payment_data:
        # 구독 정보 저장
        subscription = Subscription(user_id=current_user.id)
        db.session.add(subscription)
        db.session.commit()
        flash('구독이 성공적으로 완료되었습니다.', 'success')
    else:
        flash('결제가 실패하였습니다.', 'error')
    return redirect(url_for('main.index'))

@bp.route('/subscribe', methods=['GET', 'POST'])
@login_required
def subscribe():
    if request.method == 'POST':
        csrf_token = request.form.get('csrf_token')
        try:
            validate_csrf(csrf_token)
        except:
            flash('유효하지 않은 CSRF 토큰입니다.', 'error')
            return redirect(url_for('payments.subscribe'))

    is_subscribed = current_user.subscription is not None
    return render_template('payment/subscribe.html', client_key=TOSSPAYMENTS_CLIENT_KEY, is_subscribed = is_subscribed)

@bp.route('/success', methods=['GET'])
@login_required
def success():
    order_id = request.args.get('orderId')
    amount = request.args.get('amount')
    payment_key = request.args.get('paymentKey')

    # 액세스 토큰 발급 받기
    url = "https://api.tosspayments.com/v1/payments/confirm"
    secret_key = f"{TOSSPAYMENTS_SECRET_KEY}:"
    encoded_secret_key = base64.b64encode(secret_key.encode('utf-8')).decode('utf-8')
    headers = {
        "Authorization": f"Basic {encoded_secret_key}",
        "Content-Type": "application/json"
    }
    data = {
        "paymentKey": payment_key,
        "orderId": order_id,
        "amount": amount
    }
    res = requests.post(url, headers=headers, json=data)
    payment_data = res.json()
    print(payment_data)

    if 'paymentKey' in payment_data and 'orderId' in payment_data:
        # 구독 정보 저장
        subscription = Subscription(user_id=current_user.id)
        db.session.add(subscription)
        db.session.commit()
        flash('구독이 성공적으로 완료되었습니다.', 'success')
    else:
        flash('결제가 실패하였습니다.', 'error')

    return redirect(url_for('main.index'))