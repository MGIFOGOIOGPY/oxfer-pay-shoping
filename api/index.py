from flask import Flask, jsonify, request, render_template_string
import random
import string
import re
from datetime import datetime, timedelta
import json

app = Flask(__name__)

# Enhanced country data with extensive name databases
COUNTRIES_DATA = {
    "philippines": {
        "name": "Philippines",
        "flag": "🇵🇭",
        "phone_code": "+63",
        "phone_length": 10,
        "domains": ["gmail.com", "yahoo.com", "outlook.com", "ph", "philcom.com", "smart.com.ph", "globelines.com.ph"],
        "first_names": [
            "Juan", "Jose", "Antonio", "Carlos", "Miguel", "Luis", "Francisco", "Ramon", "Fernando", "Eduardo",
            "Ricardo", "Alberto", "Roberto", "Manuel", "Pedro", "Rafael", "Jorge", "Sergio", "Andres", "Diego",
            "Maria", "Ana", "Carmen", "Rosa", "Teresa", "Isabel", "Elena", "Lucia", "Patricia", "Gabriela",
            "Sofia", "Claudia", "Adriana", "Beatriz", "Raquel", "Monica", "Veronica", "Natalia", "Silvia", "Laura",
            "Andrea", "Paula", "Eva", "Cristina", "Marta", "Angela", "Diana", "Pilar", "Juana", "Margarita",
            "Lourdes", "Concepcion", "Dolores", "Mercedes", "Rosario", "Josefina", "Francisca", "Antonia", "Manuela", "Rita"
        ],
        "last_names": [
            "dela Cruz", "Santos", "Reyes", "Garcia", "Ramos", "Aquino", "Mendoza", "Villanueva", "Castillo", "Fernandez",
            "Bautista", "Torres", "Gonzalez", "Lopez", "Martinez", "Perez", "Sanchez", "Rivera", "Castro", "Romero",
            "Flores", "Morales", "Ortiz", "Gutierrez", "Alvarez", "Ruiz", "Vargas", "Jimenez", "Moreno", "Herrera",
            "Medina", "Aguilar", "Dominguez", "Rojas", "Mendez", "Salazar", "Guerrero", "Ortega", "Cortez", "Navarro",
            "Silva", "Del Rosario", "Marquez", "Villegas", "Cabrera", "Peralta", "Valdez", "Peña", "Rios", "Miranda",
            "Cordero", "Figueroa", "Solis", "Espinoza", "Chavez", "Velasco", "Aragon", "Molina", "Serrano", "Campos"
        ],
        "cities": ["Manila", "Quezon City", "Cebu City", "Davao City", "Makati", "Pasig", "Taguig", "Mandaluyong", "Pasay", "Valenzuela"],
        "states": ["Metro Manila", "Cebu", "Davao del Sur", "Cavite", "Laguna", "Bulacan", "Rizal", "Pampanga", "Batangas", "Iloilo"]
    },
    "india": {
        "name": "India",
        "flag": "🇮🇳",
        "phone_code": "+91",
        "phone_length": 10,
        "domains": ["gmail.com", "yahoo.com", "outlook.com", "in", "rediffmail.com", "hotmail.com", "indiatimes.com"],
        "first_names": [
            "Raj", "Amit", "Rahul", "Vikram", "Sanjay", "Arjun", "Rohan", "Karan", "Vivek", "Ankit",
            "Suresh", "Mahesh", "Dinesh", "Naresh", "Pradeep", "Sunil", "Manoj", "Alok", "Vishal", "Gaurav",
            "Priya", "Anjali", "Sonia", "Meera", "Kavita", "Neha", "Pooja", "Divya", "Shreya", "Anita",
            "Sunita", "Rekha", "Madhu", "Suman", "Lata", "Geeta", "Ritu", "Nisha", "Preeti", "Swati",
            "Aditi", "Roshni", "Tanvi", "Isha", "Riya", "Simran", "Kriti", "Mona", "Seema", "Ankita",
            "Deepak", "Harish", "Nitin", "Ramesh", "Sandeep", "Yogesh", "Ashok", "Bharat", "Chandan", "Dheeraj"
        ],
        "last_names": [
            "Sharma", "Kumar", "Singh", "Patel", "Gupta", "Verma", "Malhotra", "Reddy", "Choudhury", "Jain",
            "Yadav", "Thakur", "Pandey", "Mishra", "Joshi", "Saxena", "Trivedi", "Tiwari", "Mehta", "Bansal",
            "Agarwal", "Garg", "Goel", "Rastogi", "Bhatia", "Chauhan", "Rathore", "Srivastava", "Nair", "Menon",
            "Iyer", "Pillai", "Shukla", "Bose", "Banerjee", "Mukherjee", "Das", "Roy", "Sinha", "Ghosh",
            "Chakraborty", "Basu", "Sen", "Dutta", "Sarkar", "Pal", "Biswas", "Rao", "Naik", "Prabhu",
            "Shetty", "Khan", "Hussain", "Ali", "Ahmed", "Shaikh", "Ansari", "Pathan", "Malik", "Qureshi"
        ],
        "cities": ["Mumbai", "Delhi", "Bangalore", "Hyderabad", "Chennai", "Kolkata", "Pune", "Ahmedabad", "Jaipur", "Lucknow"],
        "states": ["Maharashtra", "Karnataka", "Tamil Nadu", "Uttar Pradesh", "Gujarat", "Rajasthan", "West Bengal", "Bihar", "Madhya Pradesh", "Punjab"]
    },
    "israel": {
        "name": "Israel",
        "flag": "🇮🇱",
        "phone_code": "+972",
        "phone_length": 9,
        "domains": ["gmail.com", "yahoo.com", "outlook.com", "walla.co.il", "012.net.il", "bezeqint.net"],
        "first_names": [
            "David", "Moshe", "Yosef", "Avraham", "Yakov", "Daniel", "Michael", "Ariel", "Eli", "Yonatan",
            "Shlomo", "Yehuda", "Benjamin", "Itamar", "Tzvi", "Menachem", "Yisrael", "Shimon", "Levi", "Refael",
            "Sarah", "Rachel", "Leah", "Rivka", "Miriam", "Esther", "Chana", "Tova", "Yaffa", "Malka",
            "Deborah", "Naomi", "Tamar", "Yael", "Shoshana", "Aviva", "Batya", "Gila", "Hannah", "Ruth",
            "Adi", "Noa", "Maya", "Talia", "Shira", "Noya", "Romi", "Lior", "Yuval", "Gal",
            "Amit", "Omer", "Ron", "Guy", "Ido", "Eyal", "Tom", "Nimrod", "Asaf", "Ori"
        ],
        "last_names": [
            "Cohen", "Levi", "Mizrahi", "Peretz", "Katz", "Friedman", "Goldberg", "Rosenberg", "Weiss", "Stein",
            "Avraham", "Shapiro", "Horowitz", "Segal", "Gross", "Klein", "Schwartz", "Berger", "Finkelstein", "Katzir",
            "Baruch", "Eisenberg", "Feinstein", "Golan", "Hirsch", "Isaacson", "Jacobs", "Kahn", "Lerner", "Mendel",
            "Nissan", "Oren", "Pinsky", "Rabin", "Silver", "Tessler", "Uziel", "Vardi", "Wachs", "Zucker",
            "Adler", "Benzion", "Carmel", "Dagan", "Eliyahu", "Feldman", "Green", "Hasson", "Ivry", "Jaffe"
        ],
        "cities": ["Jerusalem", "Tel Aviv", "Haifa", "Beersheba", "Netanya", "Ashdod", "Rishon LeZion", "Petah Tikva", "Holon", "Bnei Brak"],
        "states": ["Jerusalem District", "Tel Aviv District", "Haifa District", "Central District", "Southern District", "Northern District"]
    },
    "ukraine": {
        "name": "Ukraine",
        "flag": "🇺🇦",
        "phone_code": "+380",
        "phone_length": 9,
        "domains": ["gmail.com", "yahoo.com", "outlook.com", "ukr.net", "i.ua", "meta.ua", "bigmir.net"],
        "first_names": [
            "Oleksandr", "Andriy", "Serhiy", "Mykola", "Viktor", "Ivan", "Yuriy", "Petro", "Pavlo", "Dmytro",
            "Volodymyr", "Bohdan", "Taras", "Roman", "Maksym", "Artem", "Vladyslav", "Yaroslav", "Ihor", "Vasyl",
            "Olena", "Natalia", "Iryna", "Tetiana", "Olga", "Yana", "Kateryna", "Anastasiia", "Valentyna", "Svitlana",
            "Marina", "Lydia", "Galyna", "Vira", "Zoya", "Nina", "Raisa", "Larisa", "Tamara", "Valeria",
            "Sophia", "Alina", "Viktoriia", "Daria", "Anna", "Maria", "Yulia", "Elena", "Inna", "Liudmyla",
            "Mariia", "Khrystyna", "Veronika", "Angelina", "Diana", "Evgenia", "Karina", "Lilia", "Nadiia", "Polina"
        ],
        "last_names": [
            "Koval", "Melnyk", "Bondarenko", "Tkachenko", "Kravchenko", "Shevchenko", "Kovalchuk", "Polishchuk", "Savchenko", "Lysenko",
            "Boyko", "Kovalenko", "Oliynyk", "Shevchuk", "Rudenko", "Moroz", "Marchenko", "Petrenko", "Klymenko", "Pavlenko",
            "Vasylenko", "Levchenko", "Kharchenko", "Sydorenko", "Gonchar", "Kuzmenko", "Ponomarenko", "Savchuk", "Melnichuk", "Shvets",
            "Fedorenko", "Yurchenko", "Tkachuk", "Bilyk", "Taran", "Osipenko", "Kravets", "Zayets", "Romanenko", "Serdyuk",
            "Voloshyn", "Tereshchenko", "Shcherbak", "Moskalenko", "Kornienko", "Hryhor", "Zakharchenko", "Kostenko", "Vovk", "Vynnyk"
        ],
        "cities": ["Kyiv", "Kharkiv", "Odesa", "Dnipro", "Lviv", "Zaporizhzhia", "Vinnytsia", "Kryvyi Rih", "Mykolaiv", "Chernihiv"],
        "states": ["Kyiv City", "Kharkiv Oblast", "Odesa Oblast", "Lviv Oblast", "Dnipropetrovsk Oblast", "Donetsk Oblast", "Zaporizhzhia Oblast"]
    },
    "cambodia": {
        "name": "Cambodia",
        "flag": "🇰🇭",
        "phone_code": "+855",
        "phone_length": 8,
        "domains": ["gmail.com", "yahoo.com", "outlook.com", "kh", "online.com.kh"],
        "first_names": [
            "Sok", "Chan", "Kong", "Rith", "Sophea", "Srey", "Bopha", "Sopheap", "Kunthea", "Ratha",
            "Dara", "Vannak", "Samnang", "Sothy", "Vichet", "Bunthoeun", "Chantha", "Sokha", "Mony", "Phalla",
            "Sophat", "Sovann", "Ratanak", "Sopheak", "Kosal", "Samedy", "Vuthy", "Sokhom", "Serey", "Phirum",
            "Sokun", "Sopheng", "Rithy", "Sokheng", "Sopheap", "Sopanha", "Sophea", "Sophat", "Sopheap", "Sopheng",
            "Sreyneath", "Sreypov", "Sreyroth", "Sreymom", "Sreyneath", "Sreypich", "Sreyroth", "Sreymey", "Sreyhak", "Sreytoch",
            "Sopheap", "Sopheng", "Sophat", "Sophea", "Sopanha", "Sopheap", "Sophat", "Sophea", "Sopanha", "Sopheap"
        ],
        "last_names": [
            "Sok", "Chan", "Kong", "Rith", "Sophea", "Srey", "Bopha", "Sopheap", "Kunthea", "Ratha",
            "Dara", "Vannak", "Samnang", "Sothy", "Vichet", "Bunthoeun", "Chantha", "Sokha", "Mony", "Phalla",
            "Sophat", "Sovann", "Ratanak", "Sopheak", "Kosal", "Samedy", "Vuthy", "Sokhom", "Serey", "Phirum",
            "Sokun", "Sopheng", "Rithy", "Sokheng", "Sopheap", "Sopanha", "Sophea", "Sophat", "Sopheap", "Sopheng",
            "Sreyneath", "Sreypov", "Sreyroth", "Sreymom", "Sreyneath", "Sreypich", "Sreyroth", "Sreymey", "Sreyhak", "Sreytoch",
            "Sopheap", "Sopheng", "Sophat", "Sophea", "Sopanha", "Sopheap", "Sophat", "Sophea", "Sopanha", "Sopheap"
        ],
        "cities": ["Phnom Penh", "Siem Reap", "Battambang", "Sihanoukville", "Poipet", "Kampong Cham", "Kampot", "Takeo", "Kratie", "Koh Kong"],
        "states": ["Phnom Penh", "Siem Reap", "Battambang", "Kampong Cham", "Kandal", "Preah Sihanouk", "Kampot", "Takeo", "Kratie", "Koh Kong"]
    }
}

def generate_phone_number(country_code, length):
    """Generate a valid phone number for the specified country"""
    number = ''.join([str(random.randint(0, 9)) for _ in range(length)])
    return f"{country_code}{number}"

def generate_email(first_name, last_name, domains):
    """Generate a realistic email address"""
    domain = random.choice(domains)
    
    # Various email formats for realism
    formats = [
        f"{first_name.lower()}.{last_name.lower().replace(' ', '')}",
        f"{first_name.lower()}{last_name.lower().replace(' ', '')}",
        f"{first_name.lower()[0]}{last_name.lower().replace(' ', '')}",
        f"{first_name.lower()}{random.randint(10, 999)}",
        f"{first_name.lower()}.{last_name.lower().split()[0] if ' ' in last_name else last_name.lower()}",
        f"{first_name.lower()}_{last_name.lower().replace(' ', '')}",
        f"{first_name.lower()}{last_name.lower()[0]}",
        f"{first_name.lower()}.{random.randint(1970, 2005)}"
    ]
    
    username = random.choice(formats)
    return f"{username}@{domain}"

def generate_address(country_data):
    """Generate a realistic address"""
    street_number = random.randint(1, 9999)
    street_names = ["Main", "Oak", "Maple", "Cedar", "Pine", "Elm", "Washington", "Lincoln", "Jefferson", "Park", "Broadway", "First", "Second", "Third"]
    street_type = ["St", "Ave", "Rd", "Blvd", "Dr", "Ln", "Way", "Court", "Plaza"]
    
    street = f"{street_number} {random.choice(street_names)} {random.choice(street_type)}"
    city = random.choice(country_data["cities"])
    state = random.choice(country_data["states"])
    
    # Generate postal code based on country
    postal_codes = {
        "philippines": f"{random.randint(1000, 9999)}",
        "india": f"{random.randint(100000, 999999)}",
        "israel": f"{random.randint(10000, 99999)}",
        "ukraine": f"{random.randint(10000, 99999)}",
        "cambodia": f"{random.randint(10000, 99999)}"
    }
    
    return {
        "street": street,
        "city": city,
        "state": state,
        "postal_code": postal_codes.get(country_data["name"].lower(), "00000"),
        "country": country_data["name"]
    }

def generate_birth_date():
    """Generate a random birth date (18-65 years old)"""
    end_date = datetime.now() - timedelta(days=365*18)
    start_date = end_date - timedelta(days=365*47)  # 18-65 years old
    
    random_date = start_date + timedelta(
        days=random.randint(0, (end_date - start_date).days)
    )
    
    return random_date.strftime("%Y-%m-%d")

def generate_user_info(country):
    """Generate comprehensive user information for the specified country"""
    if country not in COUNTRIES_DATA:
        return {"error": "Country not supported"}
    
    country_data = COUNTRIES_DATA[country]
    
    first_name = random.choice(country_data["first_names"])
    last_name = random.choice(country_data["last_names"])
    
    phone_number = generate_phone_number(country_data["phone_code"], country_data["phone_length"])
    email = generate_email(first_name, last_name, country_data["domains"])
    address = generate_address(country_data)
    birth_date = generate_birth_date()
    age = datetime.now().year - datetime.strptime(birth_date, "%Y-%m-%d").year
    
    # Generate username
    username = f"{first_name.lower()}{last_name.lower().replace(' ', '')}{random.randint(10, 999)}"
    
    # Generate password
    password_length = random.randint(12, 16)
    password = ''.join(random.choices(string.ascii_letters + string.digits + "!@#$%^&*", k=password_length))
    
    # Generate credit card info (fake, for demonstration only)
    credit_card_types = ["Visa", "MasterCard", "American Express", "Discover"]
    credit_card_type = random.choice(credit_card_types)
    
    credit_card = {
        "type": credit_card_type,
        "number": generate_credit_card_number(credit_card_type),
        "expiry": f"{random.randint(1, 12):02d}/{random.randint(23, 30)}",
        "cvv": f"{random.randint(100, 999)}",
        "holder_name": f"{first_name} {last_name}"
    }
    
    # Generate additional realistic information
    occupations = ["Software Engineer", "Doctor", "Teacher", "Accountant", "Manager", "Sales Executive", "Designer", "Nurse", "Engineer", "Consultant"]
    companies = ["Tech Solutions Inc", "Global Enterprises", "Innovation Labs", "City Hospital", "National Bank", "Creative Designs", "Smart Systems"]
    
    return {
        "personal_info": {
            "first_name": first_name,
            "last_name": last_name,
            "full_name": f"{first_name} {last_name}",
            "birth_date": birth_date,
            "age": age,
            "gender": random.choice(["Male", "Female"]),
            "occupation": random.choice(occupations),
            "company": random.choice(companies)
        },
        "contact_info": {
            "phone": phone_number,
            "email": email,
            "address": address
        },
        "account_info": {
            "username": username,
            "password": password,
            "member_since": (datetime.now() - timedelta(days=random.randint(30, 365*5))).strftime("%Y-%m-%d")
        },
        "financial_info": {
            "credit_card": credit_card,
            "bank_account": f"{random.randint(10000000, 99999999)}",
            "routing_number": f"{random.randint(100000000, 999999999)}",
            "account_type": random.choice(["Checking", "Savings"])
        },
        "digital_info": {
            "ip_address": f"{random.randint(192, 223)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}",
            "user_agent": random.choice([
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
            ]),
            "device": random.choice(["Desktop", "Mobile", "Tablet"])
        },
        "country_info": {
            "country": country_data["name"],
            "flag": country_data["flag"],
            "country_code": country,
            "timezone": generate_timezone(country)
        },
        "timestamp": datetime.now().isoformat(),
        "transaction_id": f"TXN{random.randint(1000000000, 9999999999)}"
    }

def generate_credit_card_number(card_type):
    """Generate valid-looking credit card numbers"""
    if card_type == "Visa":
        return f"4{random.randint(100, 999)} {random.randint(1000, 9999)} {random.randint(1000, 9999)} {random.randint(1000, 9999)}"
    elif card_type == "MasterCard":
        return f"5{random.randint(100, 999)} {random.randint(1000, 9999)} {random.randint(1000, 9999)} {random.randint(1000, 9999)}"
    elif card_type == "American Express":
        return f"3{random.randint(100, 999)} {random.randint(100000, 999999)} {random.randint(10000, 99999)}"
    else:  # Discover
        return f"6{random.randint(100, 999)} {random.randint(1000, 9999)} {random.randint(1000, 9999)} {random.randint(1000, 9999)}"

def generate_timezone(country):
    """Generate timezone based on country"""
    timezones = {
        "philippines": "Asia/Manila",
        "india": "Asia/Kolkata",
        "israel": "Asia/Jerusalem",
        "ukraine": "Europe/Kyiv",
        "cambodia": "Asia/Phnom_Penh"
    }
    return timezones.get(country, "UTC")

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Fake  Information 🏴</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        :root {
            --primary: #667eea;
            --primary-dark: #5a6fd8;
            --secondary: #764ba2;
            --accent: #f093fb;
            --success: #10b981;
            --warning: #f59e0b;
            --error: #ef4444;
            --dark: #1f2937;
            --light: #f8fafc;
            --gray: #6b7280;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
            min-height: 100vh;
            color: var(--dark);
            padding: 20px;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
        }

        .app-wrapper {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(20px);
            border-radius: 24px;
            overflow: hidden;
            box-shadow: 0 25px 50px rgba(0, 0, 0, 0.15);
            border: 1px solid rgba(255, 255, 255, 0.2);
        }

        .header {
            background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }

        .logo {
            font-size: 3rem;
            margin-bottom: 15px;
        }

        .title {
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 10px;
        }

        .subtitle {
            font-size: 1.1rem;
            opacity: 0.9;
            margin-bottom: 20px;
        }

        .bio {
            background: rgba(255, 255, 255, 0.2);
            padding: 12px 24px;
            border-radius: 50px;
            display: inline-block;
            font-weight: 600;
            backdrop-filter: blur(10px);
        }

        .content {
            padding: 40px;
        }

        .country-selector {
            text-align: center;
            margin-bottom: 40px;
        }

        .selector-title {
            font-size: 1.5rem;
            margin-bottom: 20px;
            color: var(--dark);
        }

        .country-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin: 30px 0;
        }

        .country-card {
            background: white;
            border: 2px solid #e5e7eb;
            border-radius: 16px;
            padding: 20px;
            text-align: center;
            cursor: pointer;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }

        .country-card:hover {
            transform: translateY(-5px);
            border-color: var(--primary);
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
        }

        .country-card.active {
            border-color: var(--primary);
            background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
            color: white;
        }

        .country-flag {
            font-size: 2.5rem;
            margin-bottom: 10px;
        }

        .country-name {
            font-weight: 600;
            font-size: 1.1rem;
        }

        .action-buttons {
            display: flex;
            gap: 15px;
            justify-content: center;
            margin: 30px 0;
        }

        .btn {
            padding: 15px 30px;
            border: none;
            border-radius: 12px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            display: inline-flex;
            align-items: center;
            gap: 10px;
        }

        .btn-primary {
            background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
            color: white;
        }

        .btn-secondary {
            background: var(--light);
            color: var(--dark);
            border: 2px solid #e5e7eb;
        }

        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
        }

        .result-container {
            background: white;
            border-radius: 16px;
            padding: 30px;
            margin-top: 30px;
            border: 1px solid #e5e7eb;
            display: none;
        }

        .result-header {
            display: flex;
            justify-content: between;
            align-items: center;
            margin-bottom: 20px;
        }

        .result-title {
            font-size: 1.5rem;
            font-weight: 700;
            color: var(--dark);
        }

        .copy-btn {
            background: var(--success);
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 8px;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .data-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
        }

        .data-section {
            background: var(--light);
            border-radius: 12px;
            padding: 20px;
        }

        .section-title {
            font-size: 1.1rem;
            font-weight: 600;
            margin-bottom: 15px;
            color: var(--primary);
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .data-item {
            margin-bottom: 10px;
            padding-bottom: 10px;
            border-bottom: 1px solid #e5e7eb;
        }

        .data-label {
            font-weight: 600;
            color: var(--gray);
            font-size: 0.9rem;
        }

        .data-value {
            color: var(--dark);
            margin-top: 5px;
        }

        .footer {
            text-align: center;
            padding: 30px;
            background: var(--light);
            border-top: 1px solid #e5e7eb;
        }

        .telegram-btn {
            background: #0088cc;
            color: white;
            padding: 12px 25px;
            border-radius: 50px;
            text-decoration: none;
            font-weight: 600;
            display: inline-flex;
            align-items: center;
            gap: 10px;
            transition: all 0.3s ease;
        }

        .telegram-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0, 136, 204, 0.4);
        }

        .loading {
            display: none;
            text-align: center;
            padding: 20px;
        }

        .spinner {
            border: 4px solid #f3f3f3;
            border-top: 4px solid var(--primary);
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 0 auto 15px;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        @media (max-width: 768px) {
            .country-grid {
                grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            }
            
            .title {
                font-size: 2rem;
            }
            
            .action-buttons {
                flex-direction: column;
            }
            
            .btn {
                width: 100%;
                justify-content: center;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="app-wrapper">
            <div class="header">
                <div class="logo">
                    <i class="fas fa-user-secret"></i>
                </div>
                <h1 class="title">Fake Information Generator</h1>
                <div class="bio">Advanced Data Generation • Multi-Country Support • Realistic Profiles</div>
            </div>

            <div class="content">
                <div class="country-selector">
                    <h2 class="selector-title">Select a Country</h2>
                    <div class="country-grid" id="countryGrid">
                        {% for country_code, country_data in countries_data.items() %}
                        <div class="country-card" data-country="{{ country_code }}">
                            <div class="country-flag">{{ country_data.flag }}</div>
                            <div class="country-name">{{ country_data.name }}</div>
                        </div>
                        {% endfor %}
                    </div>
                    
                    <div class="action-buttons">
                        <button class="btn btn-primary" onclick="generateUserData()">
                            <i class="fas fa-user-plus"></i>
                            Generate User Data
                        </button>
                        <button class="btn btn-secondary" onclick="generateRandomUser()">
                            <i class="fas fa-random"></i>
                            Random Country
                        </button>
                    </div>
                </div>

                <div class="loading" id="loading">
                    <div class="spinner"></div>
                    <p>Generating realistic user data...</p>
                </div>

                <div class="result-container" id="resultContainer">
                    <div class="result-header">
                        <h3 class="result-title">Generated User Profile</h3>
                        <button class="copy-btn" onclick="copyToClipboard()">
                            <i class="fas fa-copy"></i>
                            Copy JSON
                        </button>
                    </div>
                    <div class="data-grid" id="userData">
                        <!-- User data will be displayed here -->
                    </div>
                </div>
            </div>

            <div class="footer">
                <p>© 2025/2026  Data Generator | BY : @NaN_xax</p>
                <a href="https://t.me/+LPjSsuJXV7owMGVk" class="telegram-btn" target="_blank">
                    <i class="fab fa-telegram"></i>
                    Join Our Telegram Channel
                </a>
                <p style="margin-top: 15px; color: var(--gray); font-size: 0.9rem;">

                </p>
            </div>
        </div>
    </div>

    <script>
        let selectedCountry = 'philippines';
        let currentUserData = null;

        // Initialize country selection
        document.querySelectorAll('.country-card').forEach(card => {
            card.addEventListener('click', function() {
                document.querySelectorAll('.country-card').forEach(c => c.classList.remove('active'));
                this.classList.add('active');
                selectedCountry = this.dataset.country;
            });
        });

        // Set first country as active by default
        document.querySelector('.country-card').classList.add('active');

        async function generateUserData() {
            const loading = document.getElementById('loading');
            const resultContainer = document.getElementById('resultContainer');
            
            loading.style.display = 'block';
            resultContainer.style.display = 'none';

            try {
                const response = await fetch(`/api/user/${selectedCountry}`);
                const data = await response.json();
                
                currentUserData = data;
                displayUserData(data);
                
            } catch (error) {
                console.error('Error:', error);
                alert('Error generating user data. Please try again.');
            } finally {
                loading.style.display = 'none';
                resultContainer.style.display = 'block';
            }
        }

        async function generateRandomUser() {
            const loading = document.getElementById('loading');
            const resultContainer = document.getElementById('resultContainer');
            
            loading.style.display = 'block';
            resultContainer.style.display = 'none';

            try {
                const response = await fetch('/api/user/random');
                const data = await response.json();
                
                // Update selected country
                document.querySelectorAll('.country-card').forEach(c => c.classList.remove('active'));
                document.querySelector(`[data-country="${data.country_info.country_code}"]`).classList.add('active');
                selectedCountry = data.country_info.country_code;
                
                currentUserData = data;
                displayUserData(data);
                
            } catch (error) {
                console.error('Error:', error);
                alert('Error generating random user data. Please try again.');
            } finally {
                loading.style.display = 'none';
                resultContainer.style.display = 'block';
            }
        }

        function displayUserData(data) {
            const container = document.getElementById('userData');
            
            const sections = {
                'personal_info': { icon: 'fas fa-user', title: 'Personal Information' },
                'contact_info': { icon: 'fas fa-address-book', title: 'Contact Information' },
                'account_info': { icon: 'fas fa-key', title: 'Account Information' },
                'financial_info': { icon: 'fas fa-credit-card', title: 'Financial Information' },
                'digital_info': { icon: 'fas fa-laptop', title: 'Digital Information' },
                'country_info': { icon: 'fas fa-globe', title: 'Country Information' }
            };

            let html = '';

            for (const [sectionKey, sectionMeta] of Object.entries(sections)) {
                if (data[sectionKey]) {
                    html += `
                        <div class="data-section">
                            <h4 class="section-title">
                                <i class="${sectionMeta.icon}"></i>
                                ${sectionMeta.title}
                            </h4>
                    `;

                    for (const [key, value] of Object.entries(data[sectionKey])) {
                        if (typeof value === 'object') {
                            html += `<div class="data-item">
                                <div class="data-label">${formatKey(key)}</div>
                                ${Object.entries(value).map(([subKey, subValue]) => `
                                    <div style="margin-left: 15px;">
                                        <div class="data-label" style="font-size: 0.8rem;">${formatKey(subKey)}</div>
                                        <div class="data-value" style="font-size: 0.9rem;">${subValue}</div>
                                    </div>
                                `).join('')}
                            </div>`;
                        } else {
                            html += `
                                <div class="data-item">
                                    <div class="data-label">${formatKey(key)}</div>
                                    <div class="data-value">${value}</div>
                                </div>
                            `;
                        }
                    }

                    html += `</div>`;
                }
            }

            container.innerHTML = html;
            
            // Scroll to results
            document.getElementById('resultContainer').scrollIntoView({ 
                behavior: 'smooth' 
            });
        }

        function formatKey(key) {
            return key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
        }

        function copyToClipboard() {
            if (!currentUserData) return;
            
            const jsonString = JSON.stringify(currentUserData, null, 2);
            navigator.clipboard.writeText(jsonString).then(() => {
                const btn = document.querySelector('.copy-btn');
                const originalText = btn.innerHTML;
                btn.innerHTML = '<i class="fas fa-check"></i> Copied!';
                btn.style.background = 'var(--success)';
                
                setTimeout(() => {
                    btn.innerHTML = originalText;
                    btn.style.background = '';
                }, 2000);
            });
        }

        // Generate initial data for default country
        window.addEventListener('load', function() {
            generateUserData();
        });
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    """Main page with country selector and user interface"""
    return render_template_string(HTML_TEMPLATE, countries_data=COUNTRIES_DATA)

@app.route('/api/user/<country>')
def generate_user(country):
    """Generate user information for the specified country"""
    user_info = generate_user_info(country.lower())
    return jsonify(user_info)

@app.route('/api/user/random')
def generate_random_user():
    """Generate user information for a random country"""
    country = random.choice(list(COUNTRIES_DATA.keys()))
    user_info = generate_user_info(country)
    return jsonify(user_info)

@app.route('/api/countries')
def get_countries():
    """Get list of all supported countries"""
    countries_list = []
    for code, data in COUNTRIES_DATA.items():
        countries_list.append({
            "code": code,
            "name": data["name"],
            "flag": data["flag"],
            "phone_code": data["phone_code"],
            "sample_size": f"{len(data['first_names'])} names"
        })
    return jsonify(countries_list)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
