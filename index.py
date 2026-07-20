import os
from flask import Flask, redirect, url_for, session, request, render_template_string
from authlib.integrations.flask_client import OAuth

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET", "super-secret-random-string")

# Setup Discord OAuth2
oauth = OAuth(app)
discord = oauth.register(
    name='discord',
    client_id=os.getenv('DISCORD_CLIENT_ID'),
    client_secret=os.getenv('DISCORD_CLIENT_SECRET'),
    access_token_url='https://discord.com/api/oauth2/token',
    authorize_url='https://discord.com/api/oauth2/authorize',
    api_base_url='https://discord.com/api/',
    client_kwargs={'scope': 'identify guilds'}
)

# --- HTML TEMPLATES ---
HOME_HTML = """
<!DOCTYPE html>
<html>
<head><title>Bot Dashboard</title></head>
<body style="font-family: Arial; text-align: center; margin-top: 50px;">
    {% if user %}
        <h1>Welcome, {{ user.username }}!</h1>
        <img src="https://cdn.discordapp.com/avatars/{{ user.id }}/{{ user.avatar }}.png" width="100" style="border-radius: 50%;"><br><br>
        <a href="/settings">Go to Server Settings</a><br><br>
        <a href="/logout">Logout</a>
    {% else %}
        <h1>Welcome to the Bot Dashboard</h1>
        <p>Please login with Discord to manage your bot settings.</p>
        <a href="/login"><button style="padding: 10px 20px; background-color: #5865F2; color: white; border: none; cursor: pointer;">Login with Discord</button></a>
    {% endif %}
</body>
</html>
"""

SETTINGS_HTML = """
<!DOCTYPE html>
<html>
<head><title>Server Settings</title></head>
<body style="font-family: Arial; max-width: 500px; margin: 50px auto; text-align: center;">
    <h1>Configure Bot</h1>
    <p>Logged in as {{ user.username }}</p>
    
    <form action="/save_settings" method="POST" style="margin-top: 20px; text-align: left;">
        <label>Server Prefix:</label><br>
        <input type="text" name="prefix" value="!" style="width: 100%; padding: 8px; margin-bottom: 15px;"><br>
        
        <label>Welcome Message:</label><br>
        <input type="text" name="welcome_message" value="Welcome to the server!" style="width: 100%; padding: 8px; margin-bottom: 15px;"><br>
        
        <button type="submit" style="padding: 10px 20px; background-color: #5865F2; color: white; border: none; cursor: pointer;">Save Settings</button>
    </form>
    <br><a href="/">Back Home</a>
</body>
</html>
"""

# --- ROUTES ---
@app.route("/")
def home():
    user = session.get('user')
    return render_template_string(HOME_HTML, user=user)

@app.route("/login")
def login():
    redirect_uri = url_for('callback', _external=True)
    return discord.authorize_redirect(redirect_uri)

@app.route("/callback")
def callback():
    token = discord.authorize_access_token()
    resp = discord.get('users/@me', token=token)
    session['user'] = resp.json()
    return redirect('/')

@app.route("/logout")
def logout():
    session.clear()
    return redirect('/')

@app.route("/settings")
def settings():
    user = session.get('user')
    if not user:
        return redirect('/login')
    return render_template_string(SETTINGS_HTML, user=user)

@app.route("/save_settings", methods=['POST'])
def save_settings():
    user = session.get('user')
    if not user:
        return redirect('/login')
    
    prefix = request.form.get('prefix')
    
    # HERE: Save this to your database (MongoDB, SQLite, etc.)
    
    return f"<h2>Settings saved! Prefix is now {prefix}</h2><br><a href='/'>Go Home</a>"
