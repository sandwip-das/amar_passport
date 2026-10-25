# Amar Passport Agent

An AI-powered Bangladesh e-Passport information assistant built with Python and CrewAI.

## 1. Prerequisites

Before running this project, install:

- **Python 3.12** — [Download Python](https://www.python.org/downloads/)
- **Git** (optional) — [Download Git](https://git-scm.com/downloads/)
- An **OpenRouter API key** — [Get API Key](https://openrouter.ai/keys)

During Python installation on Windows, select **Add Python to PATH**.

## 2. Download the Project

### Option A: Download ZIP

1. Open this project's GitHub repository.
2. Click **Code → Download ZIP**.
3. Extract the ZIP file.
4. Open the extracted project folder in VS Code.

### Option B: Clone with Git

Open PowerShell and run:

```powershell
git clone YOUR_GITHUB_REPOSITORY_URL
cd YOUR_PROJECT_FOLDER
```

Replace the example repository URL and folder name with the actual values.

## 3. Verify Python Installation

Open the project folder in VS Code and open its terminal.

Run:

```powershell
python --version
```

The expected version is Python 3.12.x.

If `python` is not recognized, try:

```powershell
py -3.12 --version
```

If neither command works, install Python 3.12 and ensure it is available in PATH.

## 4. Create a Virtual Environment

Run these commands from the project folder:

```powershell
python -m venv .venv
```

Activate it:

```powershell
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, you can use the environment's Python directly without changing execution policies:

```powershell
.\.venv\Scripts\python.exe -m pip install --upgrade pip
```

## 5. Install Dependencies

Make sure the repository contains `requirements.txt`.

With the virtual environment activated, run:

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## 6. Configure the API Key

Create a file named `.env` in the project root directory.

Add your own OpenRouter API key:

```dotenv
OPENROUTER_API_KEY=your_openrouter_api_key_here
```

Replace the placeholder with your actual API key.

**Security:** Never upload your `.env` file or API key to GitHub. Add `.env` to `.gitignore`.

## 7. Run the Application

From the project root directory, run:

```powershell
python amar_passport_agent.py
```

Follow the application's prompts to enter the required passport information.

The application may use local fallback data when live information retrieval is unavailable. Verify important fees, requirements, and processing times through official Bangladesh e-Passport sources.

## 8. Troubleshooting

### Python is not recognized

Try:

```powershell
py -3.12 -m pip --version
```

### Dependency installation fails

Confirm that the virtual environment is activated, then run:

```powershell
python -m pip install -r requirements.txt
```

### API key or authentication error

- Confirm that `.env` is in the project root.
- Check that the variable name matches the one used in the source code.
- Verify that your OpenRouter API key is valid and has the necessary credits or access.

### Bengali text displays incorrectly

Try UTF-8 settings in PowerShell:

```powershell
chcp 65001
$env:PYTHONUTF8 = "1"
$env:PYTHONIOENCODING = "utf-8"
```

You may also need a Bengali-compatible terminal font.

## 9. Important Notes

- Internet access may be required for AI model calls and live information retrieval.
- API usage may incur charges depending on the selected model and provider.
- Local fallback data may not reflect current official rules or fees.
- This project is an informational assistant, not an official Bangladesh e-Passport service.
- Never commit API keys, passwords, or other secrets to the repository.

## License

Add your chosen open-source license before distributing this project publicly.
