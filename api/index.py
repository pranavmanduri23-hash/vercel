import os
from flask import Flask, redirect, url_for, session, request, render_template_string
from authlib.integrations.flask_client import OAuth
from pymongo import MongoClient

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

# Connect to MongoDB
def get_db():
    client = MongoClient(os.getenv("MONGO_URI"))
    return client.zenith_guard

# --- STYLES (Same as before, condensed for space) ---
BASE_CSS = """
<style>
    :root { --bg: #0b0c10; --card: #15171c; --accent: #5865F2; --accent-hover: #4752c4; --text: #dcddde; --text-bright: #ffffff; --sidebar: #111214; }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { background-color: var(--bg); color: var(--text); font-family: 'Segoe UI', sans-serif; overflow-x: hidden; }
    @keyframes fadeInUp { from { opacity: 0; transform: translate3d(0, 40px, 0); } to { opacity: 1; transform: none; } }
    @keyframes pulseGlow { 0%, 100% { box-shadow: 0 0 20px rgba(88, 101, 242, 0.3); } 50% { box-shadow: 0 0 40px rgba(88, 101, 242, 0.6); } }
    @keyframes gradientShift { 0% { background-position: 0% 50%; } 50% { background-position: 100% 50%; } 100% { background-position: 0% 50%; } }
    .animate-fadeup { animation: fadeInUp 0.8s cubic-bezier(0.16, 1, 0.3, 1) both; }
    .delay-1 { animation-delay: 0.1s; } .delay-2 { animation-delay: 0.2s; } .delay-3 { animation-delay: 0.3s; }
    .nav { display: flex; justify-content: space-between; align-items: center; padding: 20px 50px; background: rgba(11, 12, 16, 0.8); backdrop-filter: blur(12px); border-bottom: 1px solid #1e1f22; position: sticky; top: 0; z-index: 100; }
    .nav-logo { display: flex; align-items: center; gap: 10px; font-size: 1.2rem; font-weight: bold; color: var(--text-bright); text-decoration: none; }
    .btn { background: var(--accent); color: white; padding: 12px 28px; border-radius: 4px; text-decoration: none; font-weight: 600; border: none; cursor: pointer; transition: 0.2s; display: inline-block; }
    .btn:hover { background: var(--accent-hover); transform: translateY(-2px); }
    .hero { text-align: center; padding: 120px 20px; background: radial-gradient(circle at top center, #1a1c23 0%, var(--bg) 60%); }
    .hero h1 { font-size: 4rem; color: var(--text-bright); margin-bottom: 20px; letter-spacing: -2px; background: linear-gradient(90deg, #fff, #5865F2, #fff); background-size: 200% auto; -webkit-background-clip: text; -webkit-text-fill-color: transparent; animation: gradientShift 3s ease infinite; }
    .hero p { font-size: 1.2rem; color: #8e9297; max-width: 600px; margin: 0 auto 40px auto; }
    .dash-container { display: flex; min-height: 100vh; }
    .sidebar { width: 260px; background: var(--sidebar); padding: 30px 0; border-right: 1px solid #202225; position: fixed; height: 100vh; }
    .sidebar-item { display: block; padding: 15px 30px; color: #8e9297; text-decoration: none; font-weight: 500; transition: 0.2s; border-left: 3px solid transparent; }
    .sidebar-item:hover, .sidebar-item.active { background: #1e1f22; color: #fff; border-left-color: var(--accent); }
    .dash-content { margin-left: 260px; padding: 40px; width: calc(100% - 260px); }
    .dash-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 40px; padding-bottom: 20px; border-bottom: 1px solid #202225; }
    .settings-card { background: var(--card); padding: 30px; border-radius: 8px; border: 1px solid #202225; margin-bottom: 30px; animation: fadeInUp 0.5s ease; }
    .form-group { margin-bottom: 25px; }
    .form-group label { display: block; margin-bottom: 8px; color: var(--text-bright); font-weight: 600; font-size: 0.9rem; text-transform: uppercase; letter-spacing: 0.5px; }
    .form-group input[type="text"] { width: 100%; padding: 12px; border-radius: 4px; border: 1px solid #303136; background: #1e1f22; color: var(--text); font-size: 1rem; }
    .switch { position: relative; display: inline-block; width: 50px; height: 28px; float: right; }
    .switch input { opacity: 0; width: 0; height: 0; }
    .slider { position: absolute; cursor: pointer; top: 0; left: 0; right: 0; bottom: 0; background-color: #303136; transition: .4s; border-radius: 28px; }
    .slider:before { position: absolute; content: ""; height: 20px; width: 20px; left: 4px; bottom: 4px; background-color: white; transition: .4s; border-radius: 50%; }
    input:checked + .slider { background-color: var(--accent); }
    input:checked + .slider:before { transform: translateX(22px); }
    .stat-card { background: var(--card); padding: 20px; border-radius: 8px; border: 1px solid #202225; text-align: center; }
    .stat-val { font-size: 2rem; font-weight: bold; color: var(--accent); }
    .alert { background: #2d3436; padding: 15px; border-radius: 4px; border-left: 4px solid var(--accent); margin-bottom: 20px; color: #fff; }
</style>
"""

DASH_HTML = BASE_CSS + """
<!DOCTYPE html>
<html>
<head><title>Dashboard - Zenith Guard</title></head>
<body>
    <div class="dash-container">
        <div class="sidebar">
            <a href="/dashboard" class="sidebar-item active">📊 Overview</a>
            <a href="/dashboard" class="sidebar-item">⚙️ General</a>
            <a href="/" class="sidebar-item" style="position: absolute; bottom: 20px; width: 100%;">🏠 Back to Home</a>
        </div>
        <div class="dash-content">
            <div class="dash-header">
                <div>
                    <h1 style="color: #fff;">Live Server Overview</h1>
                    <p style="color: #8e9297;">Real-time data directly from your bot</p>
                </div>
                <div style="display: flex; align-items: center; gap: 15px;">
                    <img src="https://cdn.discordapp.com/avatars/{{ user.id }}/{{ user.avatar }}.png" width="40" height="40" style="border-radius: 50%;">
                    <a href="/logout" style="color: #8e9297; text-decoration: none;">Logout</a>
                </div>
            </div>

            {% if saved %}<div class="alert animate-fadeup">✅ Settings saved successfully to the database!</div>{% endif %}

            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 20px; margin-bottom: 30px;">
                <div class="stat-card animate-fadeup delay-1">
                    <div class="stat-val">{{ stats.servers }}</div><div class="stat-label">Live Servers</div>
                </div>
                <div class="stat-card animate-fadeup delay-2">
                    <div class="stat-val">{{ stats.users }}</div><div class="stat-label">Live Users</div>
                </div>
            </div>

            <form action="/save_settings" method="POST">
                <div class="settings-card">
                    <h3 style="color: #fff; margin-bottom: 20px;">⚙️ General Configuration</h3>
                    <div class="form-group">
                        <label>Command Prefix</label>
                        <input type="text" name="prefix" value="{{ settings.prefix }}" maxlength="3" required>
                    </div>
                    <div class="form-group">
                        <label>Welcome Message</label>
                        <input type="text" name="welcome_message" value="{{ settings.welcome_message }}" required>
                    </div>
                </div>
                <div class="settings-card">
                    <h3 style="color: #fff; margin-bottom: 20px;">🛡️ Modules</h3>
                    <div class="form-group">
                        <label>Anti-Raid <span class="switch"><input type="checkbox" name="anti_raid" {% if settings.anti_raid %}checked{% endif %}><span class="slider"></span></span></label>
                    </div>
                    <div class="form-group">
                        <label>Music <span class="switch"><input type="checkbox" name="music" {% if settings.music %}checked{% endif %}><span class="slider"></span></span></label>
                    </div>
                </div>
                <button type="submit" class="btn" style="width: 100%; padding: 15px;">Save All Changes</button>
            </form>
        </div>
    </div>
</body>
</html>
"""

# --- ROUTES ---
@app.route("/")
def home():
    user = session.get('user')
    if user:
        return f"<h1 style='color:white;text-align:center;margin-top:100px;font-family:sans-serif;'>Welcome {user['username']}!</h1><br><div style='text-align:center;'><a href='/dashboard' class='btn'>Go to Dashboard</a></div>"
    return f"<h1 style='color:white;text-align:center;margin-top:100px;font-family:sans-serif;'>Zenith Guard</h1><br><div style='text-align:center;'><a href='/login' class='btn'>Login</a></div>"

@app.route("/login")
def login():
    redirect_uri = url_for('callback', _external=True)
    return discord.authorize_redirect(redirect_uri)

@app.route("/callback")
def callback():
    token = discord.authorize_access_token()
    resp = discord.get('users/@me', token=token)
    session['user'] = resp.json()
    return redirect('/dashboard')

@app.route("/logout")
def logout():
    session.clear()
    return redirect('/')

@app.route("/dashboard")
def dashboard():
    user = session.get('user')
    if not user:
        return redirect('/login')
    
    db = get_db()
    
    # 1. Fetch LIVE Bot Stats
    stats_doc = db.bot_stats.find_one({"_id": "live_stats"})
    if stats_doc:
        stats = {"servers": stats_doc.get("servers", 0), "users": stats_doc.get("users", 0)}
    else:
        stats = {"servers": "N/A", "users": "N/A"} # Shows N/A until the bot sends data

    # 2. Fetch Real User Settings from DB
    settings_doc = db.user_settings.find_one({"user_id": user['id']})
    if not settings_doc:
        settings = {"prefix": "!", "welcome_message": "Welcome {user}!", "anti_raid": False, "music": True}
    else:
        settings = {
            "prefix": settings_doc.get("prefix", "!"),
            "welcome_message": settings_doc.get("welcome_message", "Welcome!"),
            "anti_raid": settings_doc.get("anti_raid", False),
            "music": settings_doc.get("music", True)
        }
    
    saved = request.args.get('saved', False)
    return render_template_string(DASH_HTML, user=user, settings=settings, stats=stats, saved=saved)

@app.route("/save_settings", methods=['POST'])
def save_settings():
    user = session.get('user')
    if not user:
        return redirect('/login')
    
    db = get_db()
    
    # Save REAL settings to the database
    new_settings = {
        "user_id": user['id'],
        "prefix": request.form.get('prefix', '!'),
        "welcome_message": request.form.get('welcome_message', 'Welcome!'),
        "anti_raid": 'anti_raid' in request.form,
        "music": 'music' in request.form
    }
    
    db.user_settings.update_one({"user_id": user['id']}, {"$set": new_settings}, upsert=True)
    
    return redirect('/dashboard?saved=true')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
