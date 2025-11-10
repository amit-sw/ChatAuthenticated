## Streamlit + Supabase Google Auth

### 1. Configure Google Cloud OAuth credentials

1. Sign in to https://console.cloud.google.com and create/select a project dedicated to your Supabase auth integrations.
2. Go to **APIs & Services → OAuth consent screen** and:
   - Choose **External** user type (unless your Google Workspace requires Internal).
   - Fill in the basic app info (app name, support email, developer contact).
   - Add scopes if you need more than the default basic profile (most cases only need the default).
   - Add any test users while your consent screen is in Testing status.
3. Go to **APIs & Services → Credentials → Create credentials → OAuth client ID** and pick **Web application**.
4. In **Authorized redirect URIs**, enter the Supabase callback URL for your project:
   `https://<your-project-ref>.supabase.co/auth/v1/callback`
   (Supabase shows this exact value under `Authentication → Providers → Google`.)
5. Save and copy the generated **Client ID** and **Client secret** – you will paste them into Supabase in the next section. You do **not** add your Streamlit app URL here; Google must redirect back to Supabase so Supabase can complete the OAuth handshake on your behalf.

### 2. Configure the Supabase project

1. Create a Supabase project (https://supabase.com) or open an existing one.
2. Under **Project Settings → API** note the **Project URL** and **anon/public API key** – these feed the Streamlit app.
3. Navigate to **Authentication → Providers → Google** and:
   - Toggle Google to **Enabled**.
   - Paste the **Client ID** and **Client secret** from Google Cloud.
   - Verify the **Redirect URL** matches the one you registered in Google (`https://<project>.supabase.co/auth/v1/callback`).
4. Under **Authentication → URL Configuration** set:
   - **Site URL** = the URL where users reach your Streamlit app (e.g. `http://localhost:8501` for dev, or your deployed Streamlit domain).
   - **Additional Redirect URLs** = every Streamlit origin you will use (local and production). These URLs are where Supabase is allowed to send users after it finishes the Google OAuth flow.

### 3. Provide credentials to Streamlit

Create `.streamlit/secrets.toml` (not committed to git) with your Supabase settings:

```toml
# .streamlit/secrets.toml
SUPABASE_URL = "https://xyzcompany.supabase.co"
SUPABASE_ANON_KEY = "your-anon-public-key"
SUPABASE_REDIRECT_URL = "http://localhost:8501"  # Matches one of your redirect URLs
```

`SUPABASE_REDIRECT_URL` defaults to `http://localhost:8501`; override it when deploying so Supabase sends traffic back to the correct Streamlit host.

### 4. Run the Streamlit app locally

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

### 5. Login flow recap

- **Continue with Google** opens the Supabase-hosted Google consent screen using Supabase's PKCE flow, so the redirect back to Streamlit carries a short-lived auth code instead of an `#access_token` hash.
- Google redirects to Supabase (`/auth/v1/callback`), Supabase exchanges the code, then forwards the user to your Streamlit URL with a short-lived auth code.
- `app.py` exchanges that code for a Supabase session, stores it in Streamlit `session_state`, and displays profile information.
- **Log out** signs out through Supabase and clears the local session state.

### Troubleshooting tips

- A `Missing configuration` message means Streamlit cannot read `SUPABASE_URL` or `SUPABASE_ANON_KEY`.
- OAuth redirect errors usually mean one of the URLs is missing or mismatched between Google, Supabase, and `SUPABASE_REDIRECT_URL`.
- If the consent screen is still in **Testing**, only listed test users can sign in until Google verifies the app.