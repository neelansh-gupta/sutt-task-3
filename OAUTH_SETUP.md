# Google OAuth Setup Guide for StudyDeck Forum

This guide will help you set up Google OAuth authentication for the StudyDeck Forum.

## Prerequisites
- A Google account (preferably with a BITS Pilani email)
- Access to Google Cloud Console

## Step 1: Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click on the project dropdown at the top
3. Click "New Project"
4. Enter project name: "StudyDeck Forum"
5. Click "Create"

## Step 2: Enable Required APIs

1. In the Google Cloud Console, go to **APIs & Services** → **Library**
2. Search for "Google+ API" or "Google Identity"
3. Click on it and press "Enable"

## Step 3: Create OAuth 2.0 Credentials

1. Go to **APIs & Services** → **Credentials**
2. Click **"+ Create Credentials"** → **"OAuth client ID"**
3. If prompted, configure the OAuth consent screen first:
   - Choose "External" user type
   - Fill in the required fields:
     - App name: "StudyDeck Forum"
     - User support email: your email
     - Developer contact: your email
   - Add scopes: `email`, `profile`, `openid`
   - Add test users if in development

4. Now create the OAuth client ID:
   - Application type: **Web application**
   - Name: "StudyDeck Forum Web Client"
   - Authorized JavaScript origins:
     ```
     http://localhost:8000
     http://127.0.0.1:8000
     ```
   - Authorized redirect URIs:
     ```
     http://localhost:8000/accounts/google/login/callback/
     http://127.0.0.1:8000/accounts/google/login/callback/
     ```
   - For production, add:
     ```
     https://yourdomain.com/accounts/google/login/callback/
     ```

5. Click "Create"
6. Copy the **Client ID** and **Client Secret**

## Step 4: Configure Your Application

### Option A: Using Environment Variables (Recommended)

1. Copy the example environment file:
   ```bash
   cp env.example .env
   ```

2. Edit `.env` and add your credentials:
   ```env
   GOOGLE_CLIENT_ID=your-client-id-here.apps.googleusercontent.com
   GOOGLE_CLIENT_SECRET=your-client-secret-here
   ```

### Option B: Direct Settings Configuration (Not Recommended for Production)

1. Edit `studydeck_forum/settings.py`
2. Find the `SOCIALACCOUNT_PROVIDERS` section
3. Update with your credentials:
   ```python
   SOCIALACCOUNT_PROVIDERS = {
       "google": {
           "APP": {
               "client_id": "your-client-id-here.apps.googleusercontent.com",
               "secret": "your-client-secret-here",
               "key": ""
           }
       }
   }
   ```

### Option C: Using Django Admin (Database)

1. Run the server:
   ```bash
   python manage.py runserver
   ```

2. Go to admin panel: http://localhost:8000/admin/

3. Login with superuser credentials:
   - Email: admin@pilani.bits-pilani.ac.in
   - Password: admin123

4. Navigate to **Sites** → **Sites**:
   - Click on "example.com"
   - Change domain to: `localhost:8000` (or your production domain)
   - Change name to: `StudyDeck Forum`
   - Save

5. Navigate to **Social Accounts** → **Social applications**:
   - Click "Add Social Application"
   - Provider: Google
   - Name: Google OAuth
   - Client ID: `your-client-id-here.apps.googleusercontent.com`
   - Secret key: `your-client-secret-here`
   - Sites: Select your site (localhost:8000)
   - Save

## Step 5: Test the Integration

1. Logout from admin
2. Go to http://localhost:8000/accounts/login/
3. Click "Sign in with Google"
4. You should be redirected to Google's login page
5. After authentication, you'll be redirected back to the forum

## Important Notes

### For Development
- The redirect URI must match exactly what you configured in Google Cloud Console
- Use `http://localhost:8000` for local development
- Make sure your `.env` file is never committed to version control

### For Production
- Use HTTPS for production domains
- Update redirect URIs in Google Cloud Console
- Store credentials securely using environment variables
- Never hardcode credentials in your code

### BITS Email Restriction
The application is configured to only accept BITS Pilani email addresses:
- `@pilani.bits-pilani.ac.in`
- `@goa.bits-pilani.ac.in`
- `@hyderabad.bits-pilani.ac.in`
- `@dubai.bits-pilani.ac.in`

This restriction is enforced in `accounts/adapters.py`.

## Troubleshooting

### "Redirect URI mismatch" Error
- Ensure the redirect URI in Google Cloud Console matches exactly
- Check for trailing slashes
- Verify the protocol (http vs https)

### "Access blocked" Error
- Make sure you've added test users if the app is in testing mode
- Verify the OAuth consent screen is properly configured

### Email Domain Not Allowed
- Check that you're using a BITS Pilani email
- Verify the domain restriction in `accounts/adapters.py`

### Social Application Not Found
- Ensure you've added the social application in Django admin
- Verify the site domain matches your current domain

## Security Best Practices

1. **Never commit credentials to Git**
   - Add `.env` to `.gitignore`
   - Use environment variables for all sensitive data

2. **Use different credentials for development and production**
   - Create separate OAuth clients for each environment

3. **Restrict OAuth scope**
   - Only request necessary permissions (email, profile)

4. **Enable 2FA on your Google Cloud account**
   - Protect your developer account

## Support

If you encounter any issues:
1. Check the Django debug output in the terminal
2. Review the browser console for JavaScript errors
3. Verify all URLs and credentials are correct
4. Check the Django admin for proper configuration
