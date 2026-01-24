# Cookie Authentication Setup

## Option 1: Browser DevTools (Recommended)

1. Open X.com in your browser and log in
2. Open DevTools (F12 or Cmd+Option+I)
3. Go to Application > Storage > Cookies > https://x.com
4. Find these cookies and copy their values:
   - `auth_token`
   - `ct0`
5. Create `.cookies.json` in this directory using `.cookies.json.example` as template
6. Paste the cookie values

## Option 2: Browser Extension

1. Install "EditThisCookie" or "Cookie-Editor" extension
2. Visit X.com while logged in
3. Export cookies as JSON
4. Save to `.cookies.json` in this directory

## Security Note

Never commit `.cookies.json` to git. It contains authentication credentials.
