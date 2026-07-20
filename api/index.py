import os
from flask import Flask, redirect, url_for, session, request, render_template_string
from authlib.integrations.flask_client import OAuth

# We import these safely in case they aren't installed properly on Vercel
try:
    from pymongo import MongoClient
    from pymongo.errors import PyMongoError, ConfigurationError
except ImportError:
    MongoClient = None
    PyMongoError = Exception
    ConfigurationError = Exception

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

# Connect to MongoDB Globally with MAXIMUM safety
db = None
mongo_uri = os.getenv("MONGO_URI")
if mongo_uri and MongoClient:
    try:
        client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
        db = client.zenith_guard
    except ConfigurationError as e:
        print(f"MongoDB Configuration Error: {e}")
        db = None
    except Exception as e:
        print(f"MongoDB Connection Error: {e}")
        db = None

# Helper function to safely get stats
def get_live_stats():
    if not db: 
        return {"servers": "N/A", "users": "N/A"}
    try:
        stats_doc = db.stats.find_one({"_id": "live_stats"})
        if stats_doc:
            return {"servers": stats_doc.get("servers", 0), "users": stats_doc.get("users", 0)}
    except Exception:
        pass
    return {"servers": 0, "users": 0}

# Helper function to safely get settings
def get_user_settings(user_id):
    if not db:
        return {"prefix": "!", "welcome_message": "Welcome {user}!", "anti_raid": False, "music": True}
    try:
        config_doc = db.config.find_one({"_id": "global"})
        if config_doc:
            return {
                "prefix": config_doc.get("prefix", "!"),
                "welcome_message": config_doc.get("welcome_message", "Welcome!"),
                "anti_raid": config_doc.get("anti_raid", False),
                "music": config_doc.get("music", True)
            }
    except Exception:
        pass
    return {"prefix": "!", "welcome_message": "Welcome {user}!", "anti_raid": False, "music": True}

# --- PREMIUM BLUE / WHITE / GOLD CSS ---
BASE_CSS = """
<style>
    :root { --bg: #050810; --bg-2: #0a0f1c; --card: rgba(15, 23, 42, 0.6); --gold: #fbbf24; --gold-glow: rgba(251, 191, 36, 0.4); --blue: #3b82f6; --blue-glow: rgba(59, 130, 246, 0.4); --text: #e2e8f0; --text-bright: #ffffff; --glass-border: rgba(255, 255, 255, 0.1); }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    html { scroll-behavior: smooth; }
    body { background-color: var(--bg); color: var(--text); font-family: 'Inter', 'Segoe UI', sans-serif; overflow-x: hidden; line-height: 1.6; position: relative; }
    
    /* Tech Grid Background */
    body::before { content: ''; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background-image: linear-gradient(rgba(59, 130, 246, 0.03) 1px, transparent 1px), linear-gradient(90deg, rgba(59, 130, 246, 0.03) 1px, transparent 1px); background-size: 40px 40px; z-index: -2; pointer-events: none; }
    
    /* Keyframes */
    @keyframes fadeInUp { from { opacity: 0; transform: translate3d(0, 60px, 0) scale(0.95); } to { opacity: 1; transform: none; } }
    @keyframes float { 0%, 100% { transform: translateY(0) rotate(0deg); } 50% { transform: translateY(-20px) rotate(5deg); } }
    @keyframes shimmer { 0% { background-position: -200% center; } 100% { background-position: 200% center; } }
    @keyframes glowPulse { 0%, 100% { box-shadow: 0 0 30px var(--blue-glow); } 50% { box-shadow: 0 0 60px var(--gold-glow); } }
    
    .animate-up { animation: fadeInUp 1s cubic-bezier(0.16, 1, 0.3, 1) both; }
    .d-1 { animation-delay: 0.2s; } .d-2 { animation-delay: 0.4s; } .d-3 { animation-delay: 0.6s; } .d-4 { animation-delay: 0.8s; }

    /* Navbar */
    .nav { display: flex; justify-content: space-between; align-items: center; padding: 20px 50px; background: rgba(5, 8, 16, 0.8); backdrop-filter: blur(16px); border-bottom: 1px solid var(--glass-border); position: fixed; width: 100%; top: 0; z-index: 1000; }
    .nav-logo { display: flex; align-items: center; gap: 10px; font-size: 1.3rem; font-weight: 800; color: var(--text-bright); text-decoration: none; letter-spacing: -0.5px; }
    .nav-logo span { color: var(--gold); }
    .btn { background: var(--blue); color: white; padding: 12px 30px; border-radius: 8px; text-decoration: none; font-weight: 600; border: none; cursor: pointer; transition: 0.3s; display: inline-block; }
    .btn:hover { background: #2563eb; transform: translateY(-3px); box-shadow: 0 10px 25px var(--blue-glow); }
    .btn-gold { background: linear-gradient(135deg, var(--gold), #f59e0b); color: #050810; font-weight: 800; }
    .btn-gold:hover { box-shadow: 0 10px 25px var(--gold-glow); }
    .btn-ghost { background: rgba(255,255,255,0.05); border: 1px solid var(--glass-border); color: #fff; }
    .btn-ghost:hover { background: rgba(255,255,255,0.1); box-shadow: none; }

    /* Hero Section */
    .hero { min-height: 100vh; display: flex; align-items: center; justify-content: center; position: relative; text-align: center; padding: 100px 20px 0 20px; overflow: hidden; }
    .orb { position: absolute; border-radius: 50%; filter: blur(100px); z-index: -1; }
    .orb-blue { width: 500px; height: 500px; background: rgba(59, 130, 246, 0.15); top: 10%; left: 10%; animation: float 8s ease-in-out infinite; }
    .orb-gold { width: 400px; height: 400px; background: rgba(251, 191, 36, 0.1); bottom: 10%; right: 10%; animation: float 10s ease-in-out infinite reverse; }
    
    .hero-content { max-width: 800px; }
    .hero-badge { display: inline-block; padding: 8px 16px; background: rgba(251, 191, 36, 0.1); border: 1px solid rgba(251, 191, 36, 0.3); border-radius: 20px; font-size: 0.9rem; color: var(--gold); margin-bottom: 24px; }
    .hero h1 { font-size: 4.5rem; font-weight: 800; color: var(--text-bright); margin-bottom: 24px; letter-spacing: -3px; line-height: 1.1; }
    .gradient-text { background: linear-gradient(90deg, #ffffff, #3b82f6, #fbbf24, #ffffff); background-size: 200% auto; -webkit-background-clip: text; -webkit-text-fill-color: transparent; animation: shimmer 3s linear infinite; }
    .hero p { font-size: 1.25rem; color: #94a3b8; max-width: 600px; margin: 0 auto 40px auto; }
    .hero-btns { display: flex; gap: 15px; justify-content: center; margin-bottom: 60px; }
    .shield-graphic { font-size: 6rem; margin-bottom: 40px; display: inline-block; animation: float 4s ease-in-out infinite; filter: drop-shadow(0 0 20px var(--blue-glow)); }

    /* Live Stats Bar */
    .stats-bar { display: flex; justify-content: center; gap: 60px; padding: 40px 0; border-top: 1px solid var(--glass-border); border-bottom: 1px solid var(--glass-border); background: rgba(0,0,0,0.3); backdrop-filter: blur(8px); }
    .stat-item h2 { font-size: 2.5rem; font-weight: 800; color: var(--text-bright); margin-bottom: 5px; }
    .stat-item h2 span { color: var(--gold); }
    .stat-item p { font-size: 0.9rem; color: #94a3b8; letter-spacing: 1px; text-transform: uppercase; }

    /* Features */
    .features-section { padding: 100px 20px; max-width: 1200px; margin: 0 auto; }
    .section-title { text-align: center; font-size: 2.5rem; color: var(--text-bright); margin-bottom: 20px; font-weight: 800; }
    .grid-3 { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 24px; }
    .glass-card { background: var(--card); backdrop-filter: blur(16px); border: 1px solid var(--glass-border); padding: 32px; border-radius: 16px; transition: 0.3s; position: relative; overflow: hidden; }
    .glass-card::before { content: ''; position: absolute; top: 0; left: 0; width: 100%; height: 2px; background: linear-gradient(90deg, transparent, var(--gold), transparent); opacity: 0; transition: 0.3s; }
    .glass-card:hover { transform: translateY(-8px); border-color: rgba(251, 191, 36, 0.3); }
    .glass-card:hover::before { opacity: 1; }
    .card-icon { width: 50px; height: 50px; background: rgba(59, 130, 246, 0.1); border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 1.5rem; margin-bottom: 20px; border: 1px solid var(--glass-border); }
    
    /* Dashboard Layout */
    .dash-container { display: flex; min-height: 100vh; }
    .sidebar { width: 260px; background: var(--bg-2); padding: 30px 0; border-right: 1px solid var(--glass-border); position: fixed; height: 100vh; }
    .sidebar-item { display: block; padding: 15px 30px; color: #94a3b8; text-decoration: none; font-weight: 500; transition: 0.2s; border-left: 3px solid transparent; }
    .sidebar-item:hover, .sidebar-item.active { background: rgba(255,255,255,0.03); color: #fff; border-left-color: var(--gold); }
    .dash-content { margin-left: 260px; padding: 40px; width: calc(100% - 260px); }
    .dash-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 40px; padding-bottom: 20px; border-bottom: 1px solid var(--glass-border); }
    .settings-card { background: var(--card); backdrop-filter: blur(16px); padding: 30px; border-radius: 12px; border: 1px solid var(--glass-border); margin-bottom: 30px; }
    .form-group { margin-bottom: 25px; }
    .form-group label { display: block; margin-bottom: 8px; color: var(--text-bright); font-weight: 600; font-size: 0.9rem; text-transform: uppercase; letter-spacing: 0.5px; }
    .form-group input[type="text"] { width: 100%; padding: 12px; border-radius: 8px; border: 1px solid #303136; background: var(--bg); color: var(--text); font-size: 1rem; transition: 0.2s; }
    .form-group input[type="text"]:focus { outline: none; border-color: var(--gold); box-shadow: 0 0 0 3px var(--gold-glow); }
    .switch { position: relative; display: inline-block; width: 50px; height: 28px; float: right; }
    .switch input { opacity: 0; width: 0; height: 0; }
    .slider { position: absolute; cursor: pointer; top: 0; left: 0; right: 0; bottom: 0; background-color: #303136; transition: .4s; border-radius: 28px; }
    .slider:before { position: absolute; content: ""; height: 20px; width: 20px; left: 4px; bottom: 4px; background-color: white; transition: .4s; border-radius: 50%; }
    input:checked + .slider { background-color: var(--blue); box-shadow: 0 0 10px var(--blue-glow); }
    input:checked + .slider:before { transform: translateX(22px); background: var(--gold); }
    .stat-card { background: var(--card); backdrop-filter: blur(16px); padding: 24px; border-radius: 12px; border: 1px solid var(--glass-border); text-align: center; }
    .alert { background: rgba(251, 191, 36, 0.1); padding: 15px; border-radius: 8px; border: 1px solid var(--gold); margin-bottom: 20px; color: var(--gold); }
</style>
"""

# --- HTML TEMPLATES ---
HOME_HTML = BASE_CSS + """
<!DOCTYPE html>
<html>
<head><title>Zenith Guard - Ultimate Discord Protection</title></head>
<body>
    <nav class="nav">
        <a href="/" class="nav-logo">🛡️ Zenith <span>Guard</span></a>
        <div style="display: flex; gap: 15px; align-items: center;">
            {% if user %}
                <img src="https://cdn.discordapp.com/avatars/{{ user.id }}/{{ user.avatar }}.png" width="32" height="32" style="border-radius: 50%;">
                <a href="/dashboard" class="btn">Dashboard</a>
            {% else %}
                <a href="/login" class="btn">Login with Discord</a>
            {% endif %}
        </div>
    </nav>

    <div class="hero">
        <div class="orb orb-blue"></div>
        <div class="orb orb-gold"></div>
        
        <div class="hero-content">
            <div class="shield-graphic animate-up">🛡️</div>
            <div class="hero-badge animate-up d-1">✨ Next-Gen Discord Security</div>
            <h1 class="animate-up d-2"><span class="gradient-text">Zenith Guard</span><br>Ultimate Protection</h1>
            <p class="animate-up d-3">Empower your community with advanced AI moderation, instant anti-raid defense, and seamless server management. Zenith Guard keeps your server safe 24/7.</p>
            <div class="hero-btns animate-up d-4">
                <a href="https://discord.com/oauth2/authorize?client_id=YOUR_BOT_ID_HERE&permissions=8&scope=bot" class="btn btn-gold">Invite to Discord</a>
                {% if user %}
                <a href="/dashboard" class="btn btn-ghost">Go to Dashboard</a>
                {% else %}
                <a href="/login" class="btn btn-ghost">Learn More</a>
                {% endif %}
            </div>
        </div>
    </div>

    <div class="stats-bar animate-up d-4">
        <div class="stat-item">
            <h2><span>{{ stats.servers }}</span></h2>
            <p>Active Servers</p>
        </div>
        <div class="stat-item">
            <h2><span>{{ stats.users }}</span></h2>
            <p>Users Protected</p>
        </div>
        <div class="stat-item">
            <h2><span>24/7</span></h2>
            <p>Uninterrupted</p>
        </div>
        <div class="stat-item">
            <h2><span>100%</span></h2>
            <p>Free Forever</p>
        </div>
    </div>

    <div class="features-section">
        <h2 class="section-title animate-up">Why choose <span style="color: var(--gold);">Zenith Guard</span>?</h2>
        <div class="grid-3" style="margin-top: 40px;">
            <div class="glass-card animate-up d-1">
                <div class="card-icon">🚨</div>
                <h3 style="color: #fff; margin-bottom: 10px; font-size: 1.2rem;">AI Auto-Moderation</h3>
                <p>Our advanced AI filters spam, links, and toxic messages in real-time before they hit your server.</p>
            </div>
            <div class="glass-card animate-up d-2">
                <div class="card-icon">🛡️</div>
                <h3 style="color: #fff; margin-bottom: 10px; font-size: 1.2rem;">Instant Anti-Raid</h3>
                <p>Detect and stop malicious raids instantly. Auto-lockdown protects your members and server integrity.</p>
            </div>
            <div class="glass-card animate-up d-3">
                <div class="card-icon">🎵</div>
                <h3 style="color: #fff; margin-bottom: 10px; font-size: 1.2rem;">High-Quality Music</h3>
                <p>Seamless music playback from multiple sources with an advanced queue and audio filters system.</p>
            </div>
        </div>
    </div>
</body>
</html>
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
            <a href="/dashboard" class="sidebar-item">🛡️ Moderation</a>
            <a href="/dashboard" class="sidebar-item">🎵 Music</a>
            <a href="/" class="sidebar-item" style="position: absolute; bottom: 20px; width: 100%;">🏠 Back to Home</a>
        </div>
        <div class="dash-content">
            <div class="dash-header">
                <div>
                    <h1 style="color: #fff;">Server Overview</h1>
                    <p style="color: #94a3b8;">Real-time data directly from your bot</p>
                </div>
                <div style="display: flex; align-items: center; gap: 15px;">
                    <img src="https://cdn.discordapp.com/avatars/{{ user.id }}/{{ user.avatar }}.png" width="40" height="40" style="border-radius: 50%;">
                    <a href="/logout" style="color: #94a3b8; text-decoration: none;">Logout</a>
                </div>
            </div>

            {% if saved %}<div class="alert animate-up">✅ Settings saved! The bot will update within 60 seconds.</div>{% endif %}

            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 20px; margin-bottom: 30px;">
                <div class="stat-card animate-up d-1">
                    <h2 style="color: var(--blue); margin-bottom: 5px;">{{ stats.servers }}</h2>
                    <p style="color: #94a3b8; font-size: 0.9rem; text-transform: uppercase;">Live Servers</p>
                </div>
                <div class="stat-card animate-up d-2">
                    <h2 style="color: var(--gold); margin-bottom: 5px;">{{ stats.users }}</h2>
                    <p style="color: #94a3b8; font-size: 0.9rem; text-transform: uppercase;">Live Users</p>
                </div>
            </div>

            <form action="/save_settings" method="POST">
                <div class="settings-card animate-up d-1">
                    <h3 style="color: #fff; margin-bottom: 20px;">⚙️ General Configuration</h3>
                    <div class="form-group">
                        <label>Command Prefix</label>
                        <input type="text" name="prefix" value="{{ settings.prefix }}" maxlength="3" required>
                    </div>
                    <div class="form-group">
                        <label>Welcome Message (Use {user} for new members)</label>
                        <input type="text" name="welcome_message" value="{{ settings.welcome_message }}" required>
                    </div>
                </div>
                <div class="settings-card animate-up d-2">
                    <h3 style="color: #fff; margin-bottom: 20px;">🛡️ Modules</h3>
                    <div class="form-group">
                        <label>Anti-Raid System <span class="switch"><input type="checkbox" name="anti_raid" {% if settings.anti_raid %}checked{% endif %}><span class="slider"></span></span></label>
                    </div>
                    <div class="form-group">
                        <label>Music Player <span class="switch"><input type="checkbox" name="music" {% if settings.music %}checked{% endif %}><span class="slider"></span></span></label>
                    </div>
                </div>
                <button type="submit" class="btn btn-gold animate-up d-3" style="width: 100%; padding: 15px; font-size: 1.1rem;">Save All Changes</button>
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
    stats = get_live_stats()
    return render_template_string(HOME_HTML, user=user, stats=stats)

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
    
    stats = get_live_stats()
    settings = get_user_settings(user['id'])
    
    saved = request.args.get('saved', False)
    return render_template_string(DASH_HTML, user=user, settings=settings, stats=stats, saved=saved)

@app.route("/save_settings", methods=['POST'])
def save_settings():
    user = session.get('user')
    if not user:
        return redirect('/login')
    
    if not db:
        return "Database not connected", 500
        
    new_settings = {
        "prefix": request.form.get('prefix', '!'),
        "welcome_message": request.form.get('welcome_message', 'Welcome!'),
        "anti_raid": 'anti_raid' in request.form,
        "music": 'music' in request.form
    }
    
    try:
        db.config.update_one({"_id": "global"}, {"$set": new_settings}, upsert=True)
    except Exception:
        pass
    
    return redirect('/dashboard?saved=true')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
