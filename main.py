# Import the required modules
import requests
import random
import string
import time

# Define some constants
BASE_URL = "https://accounts.google.com/signup/v2/webcreateaccount?flowName=GlifWebSignIn&flowEntry=SignUp"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36"}
RECOVERY_DOMAINS = ["@labworld.org", "@vintomaper.com"]

# Define a function to generate a random string of a given length
def random_string(length):
    return "".join(random.choice(string.ascii_lowercase + string.digits) for _ in range(length))

# Define a function to create a Gmail account
def create_gmail_account():
    # Ask the user to input the desired first name, last name, email, password, confirm password, and recovery email
    first_name = input("Desired FirstName: ")
    last_name = input("Desired LastName: ")
    email = input("Desired Email (If skipped, then automatically generate it for the system): ")
    password = input("Desired Password: ")
    confirm_password = input("Confirm Password: ")
    recovery_email = input("Recovery Email (the user will only enter the name of the recovery email with the '@labworld.org' or '@vintomaper.com' and the end of it)(if skipped, then automatically generate one): ")

    # Validate the inputs
    if not first_name or not last_name:
        print("First name and last name are required.")
        return
    if not email:
        # Generate a random email with the first name and last name
        email = first_name.lower() + "." + last_name.lower() + random_string(4) + "@gmail.com"
    if not password or not confirm_password:
        print("Password and confirm password are required.")
        return
    if password != confirm_password:
        print("Password and confirm password do not match.")
        return
    if not recovery_email:
        # Generate a random recovery email with one of the domains
        recovery_email = random_string(8) + random.choice(RECOVERY_DOMAINS)
    elif not recovery_email.endswith(RECOVERY_DOMAINS):
        print("Recovery email must end with '@labworld.org' or '@vintomaper.com'.")
        return

    # Create a session object to maintain cookies
    session = requests.Session()

    # Get the initial page to obtain the flowName and flowEntry parameters
    print("Getting the initial page...")
    response = session.get(BASE_URL + "/SignUp", headers=HEADERS)
    if response.status_code != 200:
        print("Failed to get the initial page. Status code:", response.status_code)
        return
    flow_name = response.url.split("flowName=")[-1].split("&")[0]
    flow_entry = response.url.split("flowEntry=")[-1].split("&")[0]

    # Post the first name, last name, and email to obtain the session id and the next page url
    print("Posting the first name, last name, and email...")
    data = {
        "flowName": flow_name,
        "flowEntry": flow_entry,
        "firstName": first_name,
        "lastName": last_name,
        "Username": email.split("@")[0],
        "specId": "username"
    }
    response = session.get(BASE_URL + "/SignUp", headers=HEADERS, params=data)
    if response.status_code != 200:
        print("Failed to post the first name, last name, and email. Status code:", response.status_code)
        return

    try:
        json_data = response.json()
        session_id = json_data["sessionid"]
        next_page_url = json_data.get("nextPageUrl", "")
    except requests.exceptions.JSONDecodeError:
        print("Failed to parse JSON in the response. Unexpected response format.")
        return

    # Post the password and the recovery email to obtain the next page url
    print("Posting the password and the recovery email...")
    data = {
        "flowName": flow_name,
        "flowEntry": flow_entry,
        "sessionid": session_id,
        "password": password,
        "confirmPasswd": confirm_password,
        "recoveryEmail": recovery_email,
        "specId": "recoveryemail"
    }
    response = session.post(BASE_URL + next_page_url, headers=HEADERS, data=data)
    if response.status_code != 200:
        print("Failed to post the password and the recovery email. Status code:", response.status_code)
        return
    next_page_url = response.json()["nextPageUrl"]

    # Post the date of birth and the gender to obtain the next page url
    print("Posting the date of birth and the gender...")
    data = {
        "flowName": flow_name,
        "flowEntry": flow_entry,
        "sessionid": session_id,
        "birthDay": "1",
        "birthMonth": "1",
        "birthYear": "2000",
        "gender": "OTHER",
        "specId": "birthday"
    }
    response = session.post(BASE_URL + next_page_url, headers=HEADERS, data=data)
    if response.status_code != 200:
        print("Failed to post the date of birth and the gender. Status code:", response.status_code)
        return
    next_page_url = response.json()["nextPageUrl"]

    # Post the terms of service and the privacy policy to obtain the next page url
    print("Posting the terms of service and the privacy policy...")
    data = {
        "flowName": flow_name,
        "flowEntry": flow_entry,
        "sessionid": session_id,
        "termsOfService": "accepted",
        "privacyPolicy": "accepted",
        "specId": "tospp"
    }
    response = session.post(BASE_URL + next_page_url, headers=HEADERS, data=data)
    if response.status_code != 200:
        print("Failed to post the terms of service and the privacy policy. Status code:", response.status_code)
        return
    next_page_url = response.json()["nextPageUrl"]

    # Get the final page to complete the account creation
    print("Getting the final page...")
    response = session.get(BASE_URL + next_page_url, headers=HEADERS)
    if response.status_code != 200:
        print("Failed to get the final page. Status code:", response.status_code)
        return

    # Check if the account was successfully created
    if "Congratulations" in response.text:
        print("Account successfully created:")
        print("Email:", email)
        print("Password:", password)
        print("Recovery email:", recovery_email)
    else:
        print("Something went wrong. Account not created.")

# Call the function to create a Gmail account
create_gmail_account()
