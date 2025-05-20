# Google OAuth Setup Guide

This guide will help you set up Google OAuth credentials for the LearnMore application.

## 1. Create a Google Cloud Project

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Click on "Select a project" at the top of the page
3. Click "New Project"
4. Enter a project name (e.g., "LearnMore")
5. Click "Create"

## 2. Configure OAuth Consent Screen

1. In the Google Cloud Console, go to "APIs & Services" > "OAuth consent screen"
2. Select "External" user type (unless you have a Google Workspace organization)
3. Click "Create"
4. Fill in the required information:
   - App name: "LearnMore"
   - User support email: Your email address
   - Developer contact information: Your email address
5. Click "Save and Continue"
6. Add the following scopes:
   - `.../auth/userinfo.email`
   - `.../auth/userinfo.profile`
7. Click "Save and Continue"
8. Add test users (your email address)
9. Click "Save and Continue"

## 3. Create OAuth 2.0 Client ID

1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth client ID"
3. Select "Web application" as the application type
4. Name: "LearnMore Web Client"
5. Add Authorized JavaScript origins:
   ```
   http://localhost:3000
   http://127.0.0.1:3000
   ```
6. Add Authorized redirect URIs:
   ```
   http://localhost:3000/auth/google/callback
   http://127.0.0.1:3000/auth/google/callback
   ```
7. Click "Create"

## 4. Configure Environment Variables

Add the following to your `.env` file:

```ini
GOOGLE_OAUTH_CLIENT_ID=your_client_id_here
GOOGLE_OAUTH_CLIENT_SECRET=your_client_secret_here
```

Replace `your_client_id_here` and `your_client_secret_here` with the values from your OAuth 2.0 Client ID.

## 5. Frontend Integration

In your frontend application, you'll need to:

1. Install the Google OAuth client library:
   ```bash
   npm install @react-oauth/google
   # or
   yarn add @react-oauth/google
   ```

2. Initialize the Google OAuth client:
   ```javascript
   import { GoogleOAuthProvider } from '@react-oauth/google';

   function App() {
     return (
       <GoogleOAuthProvider clientId="your_client_id_here">
         {/* Your app components */}
       </GoogleOAuthProvider>
     );
   }
   ```

3. Implement the login button:
   ```javascript
   import { GoogleLogin } from '@react-oauth/google';

   function LoginButton() {
     const handleSuccess = async (credentialResponse) => {
       // Send the credential to your backend
       const response = await fetch('/api/users/google-auth/', {
         method: 'POST',
         headers: {
           'Content-Type': 'application/json',
         },
         body: JSON.stringify({
           credential: credentialResponse.credential,
         }),
       });
       const data = await response.json();
       // Handle the response (store tokens, redirect, etc.)
     };

     return (
       <GoogleLogin
         onSuccess={handleSuccess}
         onError={() => console.log('Login Failed')}
       />
     );
   }
   ```

## 6. Testing

1. Start your development server
2. Try logging in with Google
3. Verify that:
   - The OAuth consent screen appears
   - You can successfully log in
   - The user profile is created/updated in your database
   - JWT tokens are received and stored

## Troubleshooting

1. **Invalid redirect URI**
   - Make sure the redirect URI in your Google Cloud Console matches exactly what your frontend is using
   - Check for trailing slashes and protocol (http vs https)

2. **OAuth consent screen not configured**
   - Verify that you've completed all steps in the OAuth consent screen setup
   - Check that you've added your email as a test user

3. **Invalid client ID**
   - Double-check that you've copied the correct client ID to your `.env` file
   - Verify that the client ID is being properly loaded in your application

4. **CORS issues**
   - Ensure your backend CORS settings include your frontend origin
   - Check that the Google OAuth client is initialized with the correct client ID

## Security Considerations

1. Never commit your OAuth credentials to version control
2. Use environment variables for sensitive information
3. Implement proper token storage and refresh mechanisms
4. Set appropriate session timeouts
5. Monitor OAuth usage for suspicious activity 