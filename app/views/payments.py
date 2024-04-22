from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
import requests
from app.models import Subscription
from app import TOSS_PAYMENTS_CLIENT_KEY, TOSS_PAYMENTS_SECRET_KEY, TOSS_PAYMENTS_API_URL

bp = Blueprint('payments', __name__, url_prefix='/payments')

@bp.route('/subscribe', methods=['GET', 'POST'])
@login_required
def subscribe():
    if request.method == 'POST':
        try:
            # 빌링키 발급 요청
            billing_key_response = requests.post(
                f'{TOSS_PAYMENTS_API_URL}billing/authorizations/issue',
                headers={
                    'Authorization': f'Basic {TOSS_PAYMENTS_SECRET_KEY}',
                    'Content-Type': 'application/json'
                },
                json={
                    'customerKey': current_user.id,
                    'cardNumber': request.form['card_number'],
                    'cardExpirationYear': request.form['exp_year'],
                    'cardExpirationMonth': request.form['exp_month'],
                    'cardPassword': request.form['card_password'],
                    'customerBirthday': request.form['birthday'],
                }
            )
            billing_key = billing_key_response.json()['billingKey']

            # 구독 생성 요청
            subscription_response = requests.post(
                f'{TOSS_PAYMENTS_API_URL}billing/subscriptions',
                headers={
                    'Authorization': f'Basic {TOSS_PAYMENTS_SECRET_KEY}',
                    'Content-Type': 'application/json'
                },
                json={
                    'billingKey': billing_key,
                    'customerKey': current_user.id,
                    'amount': 10000,  # 월 구독 금액
                    'orderId': f'subscription_{current_user.id}',
                    'orderName': '월 구독',
                    'customerEmail': current_user.email,
                }
            )

            if subscription_response.status_code == 200:
                # 구독 정보 저장 (예: 구독 ID, 사용자 ID 등)
                # ...
                subscription = Subscription(user_id=current_user.id)
                db.session.add(subscription)
                db.session.commit()

                flash('구독이 성공적으로 완료되었습니다.', 'success')
                return redirect(url_for('main.index'))
            else:
                flash('구독 생성에 실패하였습니다.', 'error')

        except requests.exceptions.RequestException as e:
            flash(f'결제가 실패하였습니다. 에러 메시지: {str(e)}', 'error')

    return render_template('payment/subscribe.html', client_key=TOSS_PAYMENTS_CLIENT_KEY)