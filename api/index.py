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

# --- STYLES & ANIMATIONS ---
BASE_CSS = """
<style>
    :root { --bg: #0b0c10; --card: #15171c; --accent: #5865F2; --accent-hover: #4752c4; --text: #dcddde; --text-bright: #ffffff; --sidebar: #111214; }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { background-color: var(--bg); color: var(--text); font-family: 'Segoe UI', 'Helvetica Neue', Helvetica, Arial, sans-serif; line-height: 1.6; overflow-x: hidden; }
    
    /* Animations */
    @keyframes fadeInUp { from { opacity: 0; transform: translate3d(0, 40px, 0); } to { opacity: 1; transform: none; } }
    @keyframes pulseGlow { 0%, 100% { box-shadow: 0 0 20px rgba(88, 101, 242, 0.3); } 50% { box-shadow: 0 0 40px rgba(88, 101, 242, 0.6); } }
    @keyframes gradientShift { 0% { background-position: 0% 50%; } 50% { background-position: 100% 50%; } 100% { background-position: 0% 50%; } }
    .animate-fadeup { animation: fadeInUp 0.8s cubic-bezier(0.16, 1, 0.3, 1) both; }
    .delay-1 { animation-delay: 0.1s; } .delay-2 { animation-delay: 0.2s; } .delay-3 { animation-delay: 0.3s; }

    /* Navbar */
    .nav { display: flex; justify-content: space-between; align-items: center; padding: 20px 50px; background: rgba(11, 12, 16, 0.8); backdrop-filter: blur(12px); border-bottom: 1px solid #1e1f22; position: sticky; top: 0; z-index: 100; }
    .nav-logo { display: flex; align-items: center; gap: 10px; font-size: 1.2rem; font-weight: bold; color: var(--text-bright); text-decoration: none; }
    .btn { background: var(--accent); color: white; padding: 12px 28px; border-radius: 4px; text-decoration: none; font-weight: 600; border: none; cursor: pointer; transition: 0.2s; display: inline-block; }
    .btn:hover { background: var(--accent-hover); transform: translateY(-2px); box-shadow: 0 4px 15px rgba(88, 101, 242, 0.4); }

    /* Hero Section */
    .hero { text-align: center; padding: 120px 20px; background: radial-gradient(circle at top center, #1a1c23 0%, var(--bg) 60%); }
    .hero h1 { font-size: 4rem; color: var(--text-bright); margin-bottom: 20px; letter-spacing: -2px; background: linear-gradient(90deg, #fff, #5865F2, #fff); background-size: 200% auto; -webkit-background-clip: text; -webkit-text-fill-color: transparent; animation: gradientShift 3s ease infinite; }
    .hero p { font-size: 1.2rem; color: #8e9297; max-width: 600px; margin: 0 auto 40px auto; }

    /* Landing Features */
    .features { display: flex; justify-content: center; gap: 20px; flex-wrap: wrap; max-width: 1000px; margin: -60px auto 80px auto; padding: 0 20px; position: relative; z-index: 2; }
    .feature-card { background: var(--card); padding: 30px; border-radius: 8px; border: 1px solid #202225; width: 300px; text-align: left; transition: 0.3s; }
    .feature-card:hover { transform: translateY(-8px); border-color: var(--accent); box-shadow: 0 10px 30px rgba(0,0,0,0.5); }

    /* Dashboard Layout */
    .dash-container { display: flex; min-height: 100vh; }
    .sidebar { width: 260px; background: var(--sidebar); padding: 30px 0; border-right: 1px solid #202225; position: fixed; height: 100vh; overflow-y: auto; }
    .sidebar-item { display: block; padding: 15px 30px; color: #8e9297; text-decoration: none; font-weight: 500; transition: 0.2s; border-left: 3px solid transparent; }
    .sidebar-item:hover { background: #1e1f22; color: #fff; }
    .sidebar-item.active { background: #1e1f22; color: #fff; border-left-color: var(--accent); }
    .dash-content { margin-left: 260px; padding: 40px; width: calc(100% - 260px); }
    .dash-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 40px; padding-bottom: 20px; border-bottom: 1px solid #202225; }

    /* Forms & Cards */
    .settings-card { background: var(--card); padding: 30px; border-radius: 8px; border: 1px solid #202225; margin-bottom: 30px; animation: fadeInUp 0.5s ease; }
    .form-group { margin-bottom: 25px; }
    .form-group label { display: block; margin-bottom: 8px; color: var(--text-bright); font-weight: 600; font-size: 0.9rem; text-transform: uppercase; letter-spacing: 0.5px; }
    .form-group input[type="text"], .form-group select { width: 100%; padding: 12px; border-radius: 4px; border: 1px solid #303136; background: #1e1f22; color: var(--text); font-size: 1rem; transition: 0.2s; }
    .form-group input[type="text"]:focus, .form-group select:focus { outline: none; border-color: var(--accent); box-shadow: 0 0 0 3px rgba(88, 101, 242, 0.2); }

    /* Toggle Switch */
    .switch { position: relative; display: inline-block; width: 50px; height: 28px; float: right; }
    .switch input { opacity: 0; width: 0; height: 0; }
    .slider { position: absolute; cursor: pointer; top: 0; left: 0; right: 0; bottom: 0; background-color: #303136; transition: .4s; border-radius: 28px; }
    .slider:before { position: absolute; content: ""; height: 20px; width: 20px; left: 4px; bottom: 4px; background-color: white; transition: .4s; border-radius: 50%; }
    input:checked + .slider { background-color: var(--accent); }
    input:checked + .slider:before { transform: translateX(22px); }

    .stat-card { background: var(--card); padding: 20px; border-radius: 8px; border: 1px solid #202225; text-align: center; }
    .stat-val { font-size: 2rem; font-weight: bold; color: var(--accent); }
    .stat-label { color: #8e9297; font-size: 0.9rem; }
    .alert { background: #2d3436; padding: 15px; border-radius: 4px; border-left: 4px solid var(--accent); margin-bottom: 20px; color: #fff; }
    .footer { text-align: center; padding: 40px; color: #4f545c; font-size: 0.9rem; }
</style>
"""

# --- TEMPLATES ---
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
        <h1 class="animate-fadeup">ZENITH GUARD</h1>
        <p class="animate-fadeup delay-1">The ultimate shield for your Discord community. Advanced moderation, auto-raid protection, seamless music, and full server management.</p>
        {% if user %}
            <a href="/dashboard" class="btn animate-fadeup delay-2" style="animation: pulseGlow 2s infinite, fadeInUp 0.8s 0.2s both;">Go to Dashboard</a>
        {% else %}
            <a href="/login" class="btn animate-fadeup delay-2" style="animation: pulseGlow 2s infinite, fadeInUp 0.8s 0.2s both;">Get Started</a>
        {% endif %}
    </div>

    <div class="features">
        <div class="feature-card animate-fadeup delay-1">
            <h3 style="color: #fff; margin-bottom: 10px;">🚨 Auto-Moderation</h3>
            <p>Automatically filter spam, links, and toxic messages before they hit your server.</p>
        </div>
        <div class="feature-card animate-fadeup delay-2">
            <h3 style="color: #fff; margin-bottom: 10px;">🛡️ Anti-Raid System</h3>
            <p>Detect and stop malicious raids instantly. Protect your members and server integrity.</p>
        </div>
        <div class="feature-card animate-fadeup delay-3">
            <h3 style="color: #fff; margin-bottom: 10px;">🎵 High-Quality Music</h3>
            <p>Seamless music playback from multiple sources with an advanced queue system.</p>
        </div>
    </div>

    <div class="footer">&copy; 2024 Zenith Guard. All rights reserved.</div>
</body>
</html>
"""

DASH_HTML = BASE_CSS + """
<!DOCTYPE html>
<html>
<head><title>Dashboard - Zenith Guard</title></head>
<body>
    <div class="dash-container">
        <!-- Sidebar -->
        <div class="sidebar">
            <a href="/dashboard" class="sidebar-item active">📊 Overview</a>
            <a href="/dashboard" class="sidebar-item">🛡️ Moderation</a>
            <a href="/dashboard" class="sidebar-item">🎵 Music</a>
            <a href="/dashboard" class="sidebar-item">📈 Leveling</a>
            <a href="/dashboard" class="sidebar-item">⚙️ General</a>
            <a href="/" class="sidebar-item" style="position: absolute; bottom: 20px; width: 100%;">🏠 Back to Home</a>
        </div>

        <!-- Content -->
        <div class="dash-content">
            <div class="dash-header">
                <div>
                    <h1 style="color: #fff;">Server Overview</h1>
                    <p style="color: #8e9297;">Manage your Zenith Guard settings</p>
                </div>
                <div style="display: flex; align-items: center; gap: 15px;">
                    <img src="https://cdn.discordapp.com/avatars/{{ user.id }}/{{ user.avatar }}.png" width="40" height="40" style="border-radius: 50%;">
                    <a href="/logout" style="color: #8e9297; text-decoration: none;">Logout</a>
                </div>
            </div>

            {% if saved %}<div class="alert animate-fadeup">✅ Settings saved successfully!</div>{% endif %}

            <!-- Stats Grid -->
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 20px; margin-bottom: 30px;">
                <div class="stat-card animate-fadeup delay-1">
                    <div class="stat-val">{{ stats.servers }}</div><div class="stat-label">Servers</div>
                </div>
                <div class="stat-card animate-fadeup delay-2">
                    <div class="stat-val">{{ stats.users }}</div><div class="stat-label">Users</div>
                </div>
                <div class="stat-card animate-fadeup delay-3">
                    <div class="stat-val">{{ stats.commands }}</div><div class="stat-label">Commands</div>
                </div>
            </div>

            <form action="/save_settings" method="POST">
                <!-- General Settings -->
                <div class="settings-card">
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

                <!-- Moderation Toggles -->
                <div class="settings-card">
                    <h3 style="color: #fff; margin-bottom: 20px;">🛡️ Moderation & Protection</h3>
                    <div class="form-group">
                        <label>Enable Anti-Raid System <span class="switch"><input type="checkbox" name="anti_raid" {% if settings.anti_raid %}checked{% endif %}><span class="slider"></span></span></label>
                    </div>
                    <div class="form-group">
                        <label>Auto-Mod (Filter Slurs & Spam) <span class="switch"><input type="checkbox" name="automod" {% if settings.automod %}checked{% endif %}><span class="slider"></span></span></label>
                    </div>
                </div>

                <!-- Music & Leveling -->
                <div class="settings-card">
                    <h3 style="color: #fff; margin-bottom: 20px;">🎵 Music & Leveling</h3>
                    <div class="form-group">
                        <label>Enable Music Module <span class="switch"><input type="checkbox" name="music" {% if settings.music %}checked{% endif %}><span class="slider"></span></span></label>
                    </div>
                    <div class="form-group">
                        <label>Enable Leveling System <span class="switch"><input type="checkbox" name="leveling" {% if settings.leveling %}checked{% endif %}><span class="slider"></span></span></label>
                    </div>
                </div>

                <button type="submit" class="btn" style="width: 100%; padding: 15px; font-size: 1.1rem;">Save All Changes</button>
            </form>
        </div>
    </div>
</body>
</html>
"""

# --- HELPER TO GET DEFAULT SETTINGS ---
def get_default_settings():
    return {
        "prefix": "!",
        "welcome_message": "Welcome to the server, {user}!",
        "anti_raid": True,
        "automod": False,
        "music": True,
        "leveling": False
    }

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
    
    # Load settings from session (In a real bot, you'd load from MongoDB/SQLite here)
    settings = session.get('bot_settings', get_default_settings())
    stats = {"servers": 42, "users": 15000, "commands": 120} # Mocked stats
    
    saved = request.args.get('saved', False)
    return render_template_string(DASH_HTML, user=user, settings=settings, stats=stats, saved=saved)

@app.route("/save_settings", methods=['POST'])
def save_settings():
    user = session.get('user')
    if not user:
        return redirect('/login')
    
    # Save to session (Replace this with your database save logic)
    settings = {
        "prefix": request.form.get('prefix', '!'),
        "welcome_message": request.form.get('welcome_message', 'Welcome!'),
        "anti_raid": 'anti_raid' in request.form,
        "automod": 'automod' in request.form,
        "music": 'music' in request.form,
        "leveling": 'leveling' in request.form
    }
    session['bot_settings'] = settings
    
    # Redirect back to dashboard with success message
    return redirect('/dashboard?saved=true')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
