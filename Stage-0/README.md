# Personal Profile API with Cat Facts

A Flask-based REST API that returns your personal profile information along with random cat facts fetched from the Cat Facts API.

## 🚀 Live Demo

[Deploy on Railway](#deployment) | [Test the API](https://my-internship-project-at-hng-2025-production.up.railway.app/me)

## 📋 Features

- **GET /me** endpoint that returns a 200 OK status
- Personal profile information (name, email, stack)
- Real-time cat facts from external API
- Dynamic timestamp in ISO 8601 format
- Proper error handling with fallback messages
- Comprehensive test coverage
- CORS enabled for web applications

## 🛠️ Tech Stack

- **Backend**: Python 3.12 + Flask
- **External API**: Cat Facts API (https://catfact.ninja/fact)
- **Testing**: Python unittest with mocking
- **Environment Management**: python-dotenv
- **Deployment**: Railway

## 📁 Project Structure

```
├── main.py              # Flask application
├── test_main.py         # Test suite
├── .env                 # Environment variables
├── requirements.txt     # Python dependencies
├── README.md           # This file
└── venv/               # Virtual environment
```

## 🔧 Installation & Setup

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Local Development

1. **Clone the repository**
   ```bash
   git clone <your-github-repo-url>
   cd <repository-name>
   ```

2. **Create and activate virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp env.example .env
   ```
   
   Edit `.env` file with your information:
   ```env
   USER_NAME=Your Name
   USER_EMAIL=your.email@example.com
   USER_STACK=Your Tech Stack
   PORT=5000
   ```

5. **Run the application**
   ```bash
   python main.py
   ```

6. **Test the API**
   ```bash
   curl http://localhost:5000/me
   ```

### Running Tests

```bash
# Run all tests
python test_main.py

# Run with verbose output
python test_main.py -v
```

## 🚀 Deployment on Railway

Railway is a modern deployment platform that makes it easy to deploy your Flask applications.

### Step 1: Prepare for Deployment

1. **Create requirements.txt** (if not exists):
   ```bash
   pip freeze > requirements.txt
   ```

2. **Create Procfile** (Railway auto-detects Python apps, but you can create one):
   ```bash
   echo "web: python main.py" > Procfile
   ```

### Step 2: Deploy to Railway

1. **Sign up/Login to Railway**
   - Go to [railway.app](https://railway.app)
   - Sign up with GitHub

2. **Connect your repository**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your repository

3. **Configure Environment Variables**
   - In Railway dashboard, go to your project
   - Click on "Variables" tab
   - Add the following environment variables:
     ```
     USER_NAME=Your Name
     USER_EMAIL=your.email@example.com
     USER_STACK=Your Tech Stack
     PORT=5000
     ```

4. **Deploy**
   - Railway will automatically detect your Python app
   - It will install dependencies from requirements.txt
   - Your app will be deployed and get a public URL

5. **Test your deployment**
   ```bash
   curl https://your-app-name.railway.app/me
   ```

### Railway Configuration Tips

- Railway automatically sets the `PORT` environment variable
- Update your main.py to use: `port = int(os.getenv("PORT", 5000))`
- Railway provides HTTPS by default
- Automatic deployments on git push to main branch

## 📚 API Documentation

### Endpoint: GET /me

Returns personal profile information with a random cat fact.

**URL**: `/me`  
**Method**: `GET`  
**Content-Type**: `application/json`

#### Response Format

```json
{
  "status": "success",
  "user": {
    "email": "your.email@example.com",
    "name": "Your Name",
    "stack": "Your Tech Stack"
  },
  "timestamp": "2025-10-19T06:16:21.549803Z",
  "fact": "Random cat fact from external API"
}
```

#### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `status` | string | Always "success" |
| `user` | object | User profile information |
| `user.email` | string | User's email address |
| `user.name` | string | User's full name |
| `user.stack` | string | User's technology stack |
| `timestamp` | string | Current UTC time in ISO 8601 format |
| `fact` | string | Random cat fact from Cat Facts API |

#### Example Response

```json
{
  "status": "success",
  "user": {
    "email": "gbolagadaramola765@gmail.com",
    "name": "Omogbolaga Daramola",
    "stack": "Python/Flask"
  },
  "timestamp": "2025-10-19T06:16:21.549803Z",
  "fact": "Researchers are unsure exactly how a cat purrs. Most veterinarians believe that a cat purrs by vibrating vocal folds deep in the throat."
}
```

#### Error Handling

The API includes robust error handling:
- If the Cat Facts API is unavailable, returns a fallback message
- Handles timeout errors gracefully
- Maintains consistent response format even during failures

## 🧪 Testing

The project includes comprehensive tests covering:

- ✅ Successful profile retrieval
- ✅ API failure handling
- ✅ Timeout scenarios
- ✅ HTTP error responses
- ✅ Timestamp format validation
- ✅ Cat fact function testing
- ✅ Missing data handling

### Test Coverage

- **Unit Tests**: Individual function testing
- **Integration Tests**: Full endpoint testing
- **Mock Testing**: External API simulation
- **Error Scenario Testing**: Failure handling

## 🔒 Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `USER_NAME` | Your full name | "Your Name" | Yes |
| `USER_EMAIL` | Your email address | "your.email@example.com" | Yes |
| `USER_STACK` | Your technology stack | "Python/Flask" | Yes |
| `PORT` | Server port | 5000 | No |

## 📦 Dependencies

- **Flask**: Web framework
- **Flask-CORS**: Cross-origin resource sharing
- **requests**: HTTP library for external API calls
- **python-dotenv**: Environment variable management
- **datetime**: Timestamp generation

## 🎯 Acceptance Criteria Compliance

✅ **Working GET /me endpoint** - Returns 200 OK status  
✅ **Correct JSON schema** - Follows defined response structure  
✅ **Required fields present** - status, user, timestamp, fact  
✅ **User object structure** - email, name, stack fields  
✅ **ISO 8601 timestamp** - Current UTC time format  
✅ **Dynamic timestamp** - Updates with every request  
✅ **Cat facts integration** - Fetches from external API  
✅ **No caching** - New fact on every request  
✅ **Correct Content-Type** - application/json header  
✅ **Best practices** - Well-structured, documented code  

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

**Omogbolaga Daramola**
- Email: gbolagadaramola765@gmail.com
- Stack: Python/Flask

## 🙏 Acknowledgments

- [Cat Facts API](https://catfact.ninja/) for providing random cat facts
- [Railway](https://railway.app) for hosting platform
- Flask community for excellent documentation

---

**Made with ❤️ and lots of ☕**
