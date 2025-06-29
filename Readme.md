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
5. Create an API key for Gemini AI

## MongoDB Setup

1. Create a MongoDB Atlas account or use a local MongoDB
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
## 🔐 Enable 2-Step Verification

To enhance the security of your Google Account and generate app passwords:

1. Go to [Google Account Security Settings](https://myaccount.google.com/security).
2. Under the **"Signing in to Google"** section, click on **"2-Step Verification"** and follow the on-screen instructions to enable it.

---

## 📲 Create an App Password

Once 2-Step Verification is enabled:

1. Return to the **Security** section.
2. Click on **"App passwords"** (you may be prompted to sign in again).
3. Under **"Select app"**, choose **"Other (Custom name)"** and enter a descriptive name (e.g., `FlaskApp`).
4. Click **"Generate"**.

> ✅ A 16-character app password will be displayed. Save it securely — this will be used by your application.

---

## 📨 Configure Email in Your Application

Set the following environment variables in your operating system or deployment environment:

```bash
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=abcd efgh ijkl mnop  # Use without spaces when setting
```

> 🔒 Ensure the password is used without spaces in the actual configuration:
```bash
abcd efgh ijkl mnop  # Displayed with spaces for readability
```
becomes:
```bash
MAIL_PASSWORD=abcdefghijklmnop
```

---

## 🚀 Redis Server Setup (Recommended for Rate Limiting)

To use Redis for rate limiting in your Flask application:

### Install Redis

- **Linux (Debian/Ubuntu):**
  ```bash
  sudo apt update
  sudo apt install redis
  ```

- **macOS (using Homebrew):**
  ```bash
  brew install redis
  ```

- **Windows:**
  Install [Redis for Windows](https://github.com/microsoftarchive/redis/releases) or use WSL2.

### Start Redis Server

```bash
redis-server
```

Ensure the Redis server is running before starting your Flask application.

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
