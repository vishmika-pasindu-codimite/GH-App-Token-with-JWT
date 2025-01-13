import jwt
import time
import requests

# Your GitHub App credentials
APP_ID = "12345"  # Replace with your GitHub App ID
PRIVATE_KEY_PATH = "your-kye-file-path-private-key.pem" # Replace with the path to your private key


def create_jwt(app_id, private_key_path):
    """Generate a JWT for GitHub App authentication."""
    with open(private_key_path, "r") as key_file:
        private_key = key_file.read()
    now = int(time.time())
    payload = {
        "iat": now,             # Issued at time
        "exp": now + 600,       # Expires in 10 minutes
        "iss": int(app_id)      # GitHub App ID must be an integer
    }
    return jwt.encode(payload, private_key, algorithm="RS256")


def list_installations(jwt_token):
    """List all installations of the GitHub App."""
    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Accept": "application/vnd.github+json"
    }
    url = "https://api.github.com/app/installations"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        installations = response.json()
        print("Installations:")
        for installation in installations:
            print(f"Installation ID: {installation['id']}, Account: {installation['account']['login']}")
        return installations
    else:
        raise Exception(f"Failed to list installations: {response.status_code} {response.text}")


def get_installation_token(jwt_token, installation_id):
    """Request an access token for the app's installation."""
    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Accept": "application/vnd.github+json"
    }
    url = f"https://api.github.com/app/installations/{installation_id}/access_tokens"
    response = requests.post(url, headers=headers)
    if response.status_code == 201:
        return response.json()["token"]
    else:
        raise Exception(f"Failed to get token: {response.status_code} {response.text}")


# Main script
if __name__ == "__main__":
    try:
        # Step 1: Generate the JWT
        jwt_token = create_jwt(APP_ID, PRIVATE_KEY_PATH)
        print(f"JWT Token: {jwt_token}\n")

        # Step 2: List installations to get the Installation ID
        installations = list_installations(jwt_token)
        if not installations:
            print("No installations found for this GitHub App.")
            exit(1)

        # If you already know your installation ID, set it here
        INSTALLATION_ID = installations[0]["id"]  # Use the first installation ID in the list
        print(f"Using Installation ID: {INSTALLATION_ID}\n")

        # Step 3: Get the access token for the installation
        access_token = get_installation_token(jwt_token, INSTALLATION_ID)
        print(f"GitHub Access Token: {access_token}")

    except Exception as e:
        print(f"Error: {e}")
