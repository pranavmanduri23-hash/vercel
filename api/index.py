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

# --- STYLES & TEMPLATES ---
BASE_CSS = """
<style>
    :root { --bg: #0b0c10; --card: #15171c; --accent: #5865F2; --accent-hover: #4752c4; --text: #dcddde; --text-bright: #ffffff; }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { background-color: var(--bg); color: var(--text); font-family: 'Segoe UI', 'Helvetica Neue', Helvetica, Arial, sans-serif; line-height: 1.6; }
    .nav { display: flex; justify-content: space-between; align-items: center; padding: 20px 50px; background: rgba(11, 12, 16, 0.8); backdrop-filter: blur(10px); border-bottom: 1px solid #1e1f22; position: sticky; top: 0; z-index: 100; }
    .nav-logo { display: flex; align-items: center; gap: 10px; font-size: 1.2rem; font-weight: bold; color: var(--text-bright); text-decoration: none; }
    .btn { background: var(--accent); color: white; padding: 10px 24px; border-radius: 4px; text-decoration: none; font-weight: 600; border: none; cursor: pointer; transition: 0.2s; display: inline-block; }
    .btn:hover { background: var(--accent-hover); transform: translateY(-2px); }
    .hero { text-align: center; padding: 100px 20px; background: radial-gradient(circle at top center, #1a1c23 0%, var(--bg) 60%); }
    .hero h1 { font-size: 3.5rem; color: var(--text-bright); margin-bottom: 20px; letter-spacing: -1px; }
    .hero p { font-size: 1.2rem; color: #8e9297; max-width: 600px; margin: 0 auto 40px auto; }
    .features { display: flex; justify-content: center; gap: 20px; flex-wrap: wrap; max-width: 1000px; margin: -60px auto 80px auto; padding: 0 20px; position: relative; z-index: 2; }
    .feature-card { background: var(--card); padding: 30px; border-radius: 8px; border: 1px solid #202225; width: 300px; text-align: left; transition: transform 0.2s; }
    .feature-card:hover { transform: translateY(-5px); }
    .feature-card h3 { color: var(--text-bright); margin-bottom: 10px; }
    .settings-box { background: var(--card); max-width: 500px; margin: 80px auto; padding: 40px; border-radius: 8px; border: 1px solid #202225; box-shadow: 0 10px 40px rgba(0,0,0,0.3); }
    .form-group { margin-bottom: 20px; }
    .form-group label { display: block; margin-bottom: 8px; color: var(--text-bright); font-weight: 600; font-size: 0.9rem; text-transform: uppercase; letter-spacing: 0.5px; }
    .form-group input { width: 100%; padding: 12px; border-radius: 4px; border: 1px solid #303136; background: #1e1f22; color: var(--text); font-size: 1rem; }
    .form-group input:focus { outline: none; border-color: var(--accent); }
    .footer { text-align: center; padding: 40px; color: #4f545c; font-size: 0.9rem; }
</style>
"""

HOME_HTML = BASE_CSS + """
<!DOCTYPE html>
<html>
<head><title>Zenith Guard Dashboard</title></head>
<body>
    <nav class="nav">
        <a href="/" class="nav-logo">🛡️ Zenith Guard</a>
        {% if user %}
            <div style="display: flex; align-items: center; gap: 15px;">
                <img src="https://cdn.discordapp.com/avatars/{{ user.id }}/{{ user.avatar }}.png" width="32" height="32" style="border-radius: 50%;">
                <a href="/logout" style="color: #8e9297; text-decoration: none;">Logout</a>
            </div>
        {% else %}
            <a href="/login" class="btn">Login with Discord</a>
        {% endif %}
    </nav>

    <div class="hero">
        <h1>ZENITH GUARD</h1>
        <p>The ultimate shield for your Discord community. Advanced moderation, auto-raid protection, and seamless server management.</p>
        {% if user %}
            <a href="/settings" class="btn">Manage Settings</a>
        {% else %}
            <a href="/login" class="btn">Get Started</a>
        {% endif %}
    </div>

    <div class="features">
        <div class="feature-card">
            <h3>🚨 Auto-Moderation</h3>
            <p>Automatically filter spam, links, and toxic messages before they hit your server.</p>
        </div>
        <div class="feature-card">
            <h3>🛡️ Anti-Raid System</h3>
            <p>Detect and stop malicious raids instantly. Protect your members and server integrity.</p>
        </div>
        <div class="feature-card">
            <h3>⚙️ Custom Settings</h3>
            <p>Easily configure prefixes, welcome messages, and mod-logs from a sleek dashboard.</p>
        </div>
    </div>

    <div class="footer">
        &copy; 2024 Zenith Guard. All rights reserved.
    </div>
</body>
</html>
"""

SETTINGS_HTML = BASE_CSS + """
<!DOCTYPE html>
<html>
<head><title>Server Settings - Zenith Guard</title></head>
<body>
    <nav class="nav">
        <a href="/" class="nav-logo">🛡️ Zenith Guard</a>
        <div style="display: flex; align-items: center; gap: 15px;">
            <img src="https://cdn.discordapp.com/avatars/{{ user.id }}/{{ user.avatar }}.png" width="32" height="32" style="border-radius: 50%;">
            <a href="/logout" style="color: #8e9297; text-decoration: none;">Logout</a>
        </div>
    </nav>

    <div class="settings-box">
        <h2 style="color: var(--text-bright); margin-bottom: 30px; border-bottom: 1px solid #202225; padding-bottom: 15px;">Configure Bot</h2>
        
        <form action="/save_settings" method="POST">
            <div class="form-group">
                <label>Command Prefix</label>
                <input type="text" name="prefix" value="!" maxlength="3" required>
            </div>
            
            <div class="form-group">
                <label>Welcome Message</label>
                <input type="text" name="welcome_message" value="Welcome to the server!" required>
            </div>
            
            <button type="submit" class="btn" style="width: 100%; margin-top: 10px;">Save Settings</button>
        </form>
        <br>
        <a href="/" style="color: #8e9297; text-decoration: none; display: block; text-align: center;">&larr; Back to Home</a>
    </div>

    <div class="footer">
        &copy; 2024 Zenith Guard. All rights reserved.
    </div>
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
    
    return f"<h2 style='color:white; text-align:center; margin-top:100px; font-family:sans-serif;'>Settings saved! Prefix is now {prefix}</h2><br><a href='/' style='color:#5865F2; display:block; text-align:center; text-decoration:none;'>Go Home</a>"
