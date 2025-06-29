# AI Chatbot with Google Authentication

A modern web-based chatbot application powered by Google's Gemini AI, featuring user authentication, chat history management, and a beautiful user interface.

## Features

- 🤖 **AI Chat Interface**: Powered by Google's Gemini AI model
- 🔐 **Authentication System**:
  - Traditional username/password login
  - Google OAuth integration
  - Admin user support
- 💬 **Chat Management**:
  - Real-time chat interface
  - Chat history preservation
  - Multiple chat sessions
  - Markdown support in responses
- 👥 **Contact Form**: For user inquiries and feedback
- 👨‍💼 **Admin Dashboard**: For managing user contacts
- 🎨 **Modern UI**: Built with TailwindCSS
- 🔒 **Secure**: Password hashing and JWT authentication
- 📱 **Responsive Design**: Works on all devices

## Prerequisites

- Python 3.8 or higher
- MongoDB database
- Google Cloud Platform account (for OAuth and Gemini AI)
- Node.js and npm (for TailwindCSS)

## Environment Setup

1. Clone the repository:
```bash
git clone <your-repository-url>
cd Nova
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
# On Windows
.venv\Scripts\activate
# On Unix or MacOS
source .venv/bin/activate
```
 
3. Install Python dependencies:
```bash
pip install -r requirements.txt
```

4. Install TailwindCSS:
```bash
npm install -D tailwindcss
```

5. Create a `.env` file in the root directory with the following variables:
```env
SECRET_KEY=your-very-secure-secret-key-here
ADMIN_SECRET_CODE=your-admin-code-here
MONGODB_URI=your-mongodb-connection-string
GEMINI_API_KEY=your-gemini-api-key
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
GOOGLE_REDIRECT_URI=http://127.0.0.1:5000/login/google/authorize
```

## Google Cloud Platform Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable the following APIs:
   - Gemini API
   - Google OAuth2 API
4. Create OAuth 2.0 credentials:
   - Set authorized redirect URI to: `http://127.0.0.1:5000/login/google/authorize`
   - Set authorized JavaScript origins to: `http://127.0.0.1:5000`
5. Create API key for Gemini AI

## MongoDB Setup

1. Create a MongoDB Atlas account or use local MongoDB
2. Create a new database named "chatbot"
3. Get your connection string and add it to the `.env` file

## Running the Application

1. Start the TailwindCSS compiler in watch mode:
```bash
npx tailwindcss -i .venv/static/css/main.css -o .venv/static/css/output.css --watch
```

2. In a new terminal, run the Flask application:
```bash
flask --app app:create_app --debug run
```

3. Open your browser and navigate to:
```
http://127.0.0.1:5000
```

## Usage Guide

### For Users

1. **Registration**:
   - Click "Register" to create a new account
   - Fill in your details and choose a strong password
   - Or use Google login for quick access

2. **Chatting**:
   - Log in to your account
   - Navigate to the dashboard
   - Start chatting with the AI
   - Your chat history will be saved automatically

3. **Contact Form**:
   - Use the contact page to send messages to administrators
   - Fill in your details and message
   - Submit the form

### For Administrators

1. **Admin Access**:
   - Register with the admin secret code
   - You'll get access to the admin dashboard

2. **Managing Contacts**:
   - View all contact form submissions
   - Delete unwanted messages
   - Track user inquiries

## Security Notes

- Never commit your `.env` file
- Keep your API keys and secrets secure
- Regularly update dependencies
- Use strong passwords
- Enable HTTPS in production

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, please open an issue in the repository or contact the maintainers.

## As of May 30, 2022, Google has discontinued the "Less Secure Apps" feature, which previously allowed applications to connect using just a username and password. Now, if your account has 2-Step Verification enabled, you need to create an App Password to allow less secure apps or devices to access your Google Account. ​

Solution: Generating an App Password

To resolve this issue, follow these steps to generate an App Password for your application:

## Enable 2-Step Verification:

Go to your Google Account Security Settings.​

Find the "Signing in to Google" section.​
Gist

Click on "2-Step Verification" and follow the prompts to enable it.​

Create an App Password:

After enabling 2-Step Verification, return to the "Security" section.​

Click on "App Passwords."​

You might be prompted to sign in again.​

In the "Select app" dropdown, choose "Other (Custom name)" and enter a name that helps you remember the purpose (e.g., "FlaskApp").​

Click "Generate."​
Medium

A 16-character password will appear. Note this down securely; this is the password your application will use.​
Invoice Ninja Forum
Then, set the environment variables MAIL_USERNAME and MAIL_PASSWORD in your operating system or deployment environment.

MAIL_PASSWORD=abcd efgh ijkl mnop  # No spaces when used

Redis server (recommended for rate limiting)
Make sure you have Redis installed and running. If you haven't:

For Windows: Install Redis for Windows

For Linux/macOS: Use sudo apt install redis or brew install redis

Then start Redis:
redis-server
