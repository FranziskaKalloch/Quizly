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

## Technology

- Python and Django
- Django REST Framework and Simple JWT
- django-cors-headers and python-dotenv
- SQLite for local storage
- yt-dlp and a supported JavaScript runtime: Deno or Node.js
- FFmpeg and ffprobe
- OpenAI Whisper, using the local `base` model
- Google Gen AI SDK and Gemini Flash

## System requirements

Check existing installations before installing additional software. Use a Python version compatible with the dependencies pinned in `requirements.txt`.

**FFmpeg and ffprobe must be installed at the operating-system level and available on PATH. Installing Python packages in the virtual environment does not provide these executables.** See the [FFmpeg download page](https://www.ffmpeg.org/download.html) for platform-specific builds.

A supported Deno or Node.js installation must also be available to yt-dlp. An internet connection is required for YouTube access, Gemini requests, and the initial Whisper model download.

Gemini requires an API key and access to the selected model. API availability, quotas, and billing depend on the Google project.

## macOS setup

### 1. Download the backend

Clone your backend repository using VS Code's **Git: Clone** command, or download and extract its ZIP archive. Open the folder containing `manage.py` and open an integrated terminal there. This README does not include a backend clone URL because it has not been supplied.

### 2. Check system tools

Run these commands separately. A version number confirms that the tool is available:

```bash
python3 --version
ffmpeg -version
ffprobe -version
node --version
```

If you use Deno instead of Node.js, check it with:

```bash
deno --version
```

Only one supported JavaScript runtime is needed. If Python is missing, install a compatible version from [python.org](https://www.python.org/downloads/). If you already have Homebrew, install missing FFmpeg or Node.js with the relevant command:

```bash
brew install ffmpeg
brew install node
```

If Homebrew is not installed, follow its [official installation instructions](https://brew.sh/) first, or use the FFmpeg builds and [Node.js installer](https://nodejs.org/en/download). Verify the tools again after installation.

### 3. Create and activate the virtual environment

From the backend root:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

The current dependency file omits two packages imported by the backend. Until that file is corrected, also install:

```bash
python -m pip install djangorestframework djangorestframework-simplejwt
```

In VS Code, select `.venv` through **Python: Select Interpreter**.

### 4. Configure your environment

Create your local environment file only if it does not already exist:

```bash
cp -n .env.example .env
```

Open `.env` in the editor and fill in the values described under **Environment configuration** below. Do this before running Django's management commands.

### 5. Initialize the database and start Django

```bash
python manage.py migrate
python manage.py check
```

Optionally create an administrator account:

```bash
python manage.py createsuperuser
```

Start the local server and leave this terminal running:

```bash
python manage.py runserver 127.0.0.1:8000
```

The backend is available at `http://127.0.0.1:8000`. The administrator login is at `http://127.0.0.1:8000/admin/`. The root URL does not need to display a homepage.

For later sessions, activate the existing environment and start the server again; do not recreate the environment or overwrite `.env`.

## Windows setup

The following commands use **PowerShell** unless stated otherwise.

### 1. Download the backend for Windows

Clone your backend repository with VS Code's **Git: Clone** command, or download and extract its ZIP archive. Open the folder containing `manage.py`, then open a PowerShell terminal there.

### 2. Check and install system tools

Run each command separately:

```powershell
py --version
ffmpeg -version
ffprobe -version
node --version
```

If using Deno instead of Node.js:

```powershell
deno --version
```

If Python is missing, install a compatible version from [python.org](https://www.python.org/downloads/windows/). If `py` is unavailable but `python --version` works, use `python` instead of `py` when creating the environment below.

For FFmpeg, download and extract a Windows build linked from the [official download page](https://www.ffmpeg.org/download.html). Add its `bin` directory, containing both `ffmpeg.exe` and `ffprobe.exe`, to your user PATH. FFmpeg must be accessible outside the virtual environment.

Install a supported runtime through the [Node.js installer](https://nodejs.org/en/download) or the [Deno installation instructions](https://docs.deno.com/runtime/getting_started/installation/) if neither is installed. Reopen VS Code after changing PATH, then verify the tools again.

### 3. Create and activate the virtual environment for Windows

Create a new environment on Windows; do not copy one from macOS:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Until the missing REST dependencies are added to `requirements.txt`, also run:

```powershell
python -m pip install djangorestframework djangorestframework-simplejwt
```

Select `.venv` through **Python: Select Interpreter** in VS Code.

If PowerShell blocks activation, switch to a **Command Prompt** terminal and activate with:

```bat
.venv\Scripts\activate.bat
```

Alternatively, activation is optional if you invoke the environment's interpreter directly. For example, from PowerShell:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Use that interpreter in place of `python` for subsequent commands when working without activation.

### 4. Configure your environment for Windows

If `.env` does not already exist, copy the template:

```powershell
Copy-Item .env.example .env
```

Open `.env` in the editor and fill in the values described below. Do not overwrite an existing populated environment file.

### 5. Initialize the database and start Django for Windows

```powershell
python manage.py migrate
python manage.py check
```

Optionally create an administrator:

```powershell
python manage.py createsuperuser
```

Start the server and leave the terminal running:

```powershell
python manage.py runserver 127.0.0.1:8000
```

The backend is available at `http://127.0.0.1:8000`, and the administrator login is at `http://127.0.0.1:8000/admin/`.

Windows setup has not yet been verified for this project.

## Environment configuration

Copy `.env.example` to a local file named `.env` in the backend root, beside `manage.py`. Replace the placeholders with your own values.

| Variable | Purpose |
| --- | --- |
| `SECRET_KEY` | A private Django secret key. |
| `GEMINI_API_KEY` | Your Google Gemini API key. |
| `GEMINI_MODEL` | The Gemini model identifier used for quiz generation. Choose a model available to your Google project. |

Do not commit the populated `.env` file. Restart the backend after changing environment values.

## Frontend connection

From the parent folder in which you want to store the frontend, clone the provided repository. Git must be installed for this command; alternatively download its ZIP archive from GitHub.

```text
git clone https://github.com/Developer-Akademie-Backendkurs/project.Quizly.git
```

Open the resulting `project.Quizly` folder in a separate VS Code window. Install **Live Server** if it is not already installed, then right-click `index.html` and select **Open with Live Server**. No npm installation or build step is required for this static frontend.

Keep the provided frontend in a separate folder and start it with a local web server such as VS Code Live Server. For the local integration, open it at `http://127.0.0.1:5500` and run Django at `http://127.0.0.1:8000`.

The backend's CORS configuration must allow the frontend origin, including its port, and permit credentialed requests. Place `CorsMiddleware` before `CommonMiddleware`. The frontend must send requests with credentials so the browser can include authentication cookies. See the [django-cors-headers documentation](https://github.com/adamchainz/django-cors-headers#configuration).

Use `127.0.0.1` consistently during local testing. CORS permission alone does not guarantee that cookies will be accepted: cookie attributes and any enforced CSRF checks must also match the browser setup. The current authentication code sets Secure cookies; verify browser cookie handling during local HTTP testing.

## API overview

All paths below are relative to the backend address.

| Method | Path | Purpose |
| --- | --- | --- |
| POST | `/api/register/` | Register a user. |
| POST | `/api/login/` | Log in and set authentication cookies. |
| POST | `/api/logout/` | Log out and remove authentication cookies. |
| POST | `/api/token/refresh/` | Refresh the access-token cookie. |
| POST | `/api/quizzes/` | Generate a quiz from a YouTube URL supplied in the `url` field. |
| GET | `/api/quizzes/` | List the authenticated user's quizzes. |
| GET | `/api/quizzes/{id}/` | Retrieve an owned quiz. |
| PATCH | `/api/quizzes/{id}/` | Update its title and/or description. |
| DELETE | `/api/quizzes/{id}/` | Permanently delete it and its questions. |

Successful creation returns 201. Partial updates return 200. Successful deletion returns 204 with no response body.

## Processing time and troubleshooting

Quiz generation runs synchronously: the HTTP response is returned after downloading, transcription, generation, and database storage finish. In one local test, an eight-minute video took approximately seven minutes to process. This is an observation, not a guaranteed duration.

Whisper downloads its `base` model on first use and caches it locally. Transcription runs on the local computer; Gemini receives the transcript for question generation. See the [Whisper setup documentation](https://github.com/openai/whisper#setup).

- Avoid saving backend files during generation: Django's development autoreloader can restart the process and interrupt the request.
- A completed audio download does not mean the entire quiz is finished; transcription and generation follow it.
- After a connection failure, check the quiz list before retrying. A client disconnect does not by itself prove that server-side processing stopped.
- For an expired access token, use the refresh endpoint or log in again.
- If browser login fails while Postman works, inspect the browser's network requests, CORS errors, and blocked-cookie messages.
- Keep API keys, tokens, and private transcripts out of diagnostic logs.

## Current verification and remaining work

Quiz creation, a PATCH request, and login through the frontend have been verified manually. Complete the remaining endpoint checks, frontend flows, owner-permission checks, and project checklist before submission.

The inspected `requirements.txt` does not list `djangorestframework` or `djangorestframework-simplejwt`, although the backend imports both. Update the dependency list from the working environment before claiming that installation from a clean environment is reproducible. A fresh installation and the Windows instructions still require verification.

Django's development server and the current debug configuration are intended for local development. Production deployment requires separate configuration.
