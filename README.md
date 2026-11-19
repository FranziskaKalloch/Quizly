# Quizly Backend

Quizly is a Django REST API that generates quizzes from YouTube videos. It downloads the audio with yt-dlp, processes it with FFmpeg, transcribes it locally with OpenAI Whisper, and uses Google's Gemini API to generate a quiz containing ten questions with four answer options each.

The frontend is provided separately: [Quizly Frontend](https://github.com/Developer-Akademie-Backendkurs/project.Quizly).

## Features

- User registration, login, logout, and access-token refresh.
- JWT authentication using HttpOnly cookies.
- Quiz generation from YouTube URLs.
- Listing and retrieving the authenticated user's quizzes.
- Partial updates to quiz titles and descriptions.
- Deletion of quizzes and their associated questions.
- Owner-based permissions for quiz detail operations.

## System requirements

Check existing installations before installing additional software. Use a Python version compatible with the dependencies pinned in `requirements.txt`.

**FFmpeg and ffprobe must be installed at the operating-system level and available on PATH. Installing Python packages in the virtual environment does not provide these executables.** See the [FFmpeg download page](https://www.ffmpeg.org/download.html) for platform-specific builds.

A supported Deno or Node.js installation must also be available to yt-dlp. An internet connection is required for YouTube access, Gemini requests, and the initial Whisper model download.

Gemini requires an API key and access to the selected model. API availability, quotas, and billing depend on the Google project.

## macOS Setup

### 1. Download the project and check system tools

Clone or download this repository. Open a terminal in the backend folder containing `manage.py`.

```bash
python3 --version
ffmpeg -version
ffprobe -version
node --version
```

If you use Deno instead of Node.js:

```bash
deno --version
```

Install missing tools using [Python downloads](https://www.python.org/downloads/), [FFmpeg downloads](https://www.ffmpeg.org/download.html), and [Node.js downloads](https://nodejs.org/en/download). If Homebrew is already installed, missing FFmpeg and Node.js can be installed with:

```bash
brew install ffmpeg
brew install node
```

### 2. Install Python dependencies

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

### 3. Configure environment variables

Create `.env` from the template, then replace its placeholders as described under **Environment Variables**.

```bash
cp -n .env.example .env
```

### 4. Initialize and start the backend

```bash
python manage.py migrate
python manage.py check
python manage.py createsuperuser
python manage.py runserver 127.0.0.1:8000
```

The superuser account provides access to Django Admin. Keep the server terminal running.

## Windows Setup

Use PowerShell in the backend folder containing `manage.py`.

### 1. Check system tools

```powershell
py --version
ffmpeg -version
ffprobe -version
node --version
```

If you use Deno instead of Node.js:

```powershell
deno --version
```

Install missing tools using [Python downloads](https://www.python.org/downloads/windows/), [FFmpeg downloads](https://www.ffmpeg.org/download.html), and [Node.js downloads](https://nodejs.org/en/download). Add FFmpeg's `bin` folder, containing `ffmpeg.exe` and `ffprobe.exe`, to your user PATH. Reopen the terminal after installation.

### 2. Install Python dependencies (Windows)

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

If PowerShell blocks activation, open Command Prompt and activate the environment there:

```bat
.venv\Scripts\activate.bat
```

### 3. Configure environment variables (Windows)

If `.env` does not already exist, copy the template. Replace its placeholders as described below.

```powershell
Copy-Item .env.example .env
```

### 4. Initialize and start the backend (Windows)

```powershell
python manage.py migrate
python manage.py check
python manage.py createsuperuser
python manage.py runserver 127.0.0.1:8000
```

Windows setup has not yet been verified for this project.

## Environment Variables

Edit `.env` before running Django management commands.

| Variable | Value |
| --- | --- |
| `SECRET_KEY` | Your private Django secret key. |
| `GEMINI_API_KEY` | Your Google Gemini API key. |
| `GEMINI_MODEL` | A Gemini Flash model identifier available to your Google project. |

Do not commit `.env`. Restart Django after changing these values.

## Local Addresses

- Backend: <http://127.0.0.1:8000>
- Django Admin: <http://127.0.0.1:8000/admin/>
- Frontend: <http://127.0.0.1:5500>

For later sessions, activate the existing virtual environment and start Django again.

## Frontend

The [provided frontend](https://github.com/Developer-Akademie-Backendkurs/project.Quizly) is maintained separately. Download it or clone it into a separate folder:

```bash
git clone https://github.com/Developer-Akademie-Backendkurs/project.Quizly.git
```

Open that folder in VS Code. Install the **Live Server** extension, then right-click `index.html` and select **Open with Live Server**. No npm installation is required.

Use `127.0.0.1` consistently for frontend and backend. The frontend origin must match the backend's allowed CORS origins, including port `5500`.

## API Overview

All paths are relative to the backend address.

| Method | Endpoint | Purpose |
| --- | --- | --- |
| POST | `/api/register/` | Register a user. |
| POST | `/api/login/` | Log in and set authentication cookies. |
| POST | `/api/logout/` | Log out and remove authentication cookies. |
| POST | `/api/token/refresh/` | Refresh the access token. |
| POST | `/api/quizzes/` | Generate a quiz from a YouTube URL in the `url` field. |
| GET | `/api/quizzes/` | List your quizzes. |
| GET | `/api/quizzes/{id}/` | Retrieve a quiz. |
| PATCH | `/api/quizzes/{id}/` | Update its title or description. |
| DELETE | `/api/quizzes/{id}/` | Delete a quiz and its questions. |

## Notes

- Quiz generation can take several minutes. Whisper downloads its local `base` model on first use.
- Avoid editing backend files during generation: Django's automatic restart can interrupt processing.
- If browser login fails, check CORS settings and blocked-cookie messages in the browser developer tools.
- This setup uses Django's development server and is intended for local use.
