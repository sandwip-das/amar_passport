## Recommended IDE

**PyCharm is recommended for this project.**

The project has been tested in PyCharm, where Bengali text displays correctly in both the Run Console and Terminal.

VS Code may require additional terminal font configuration to display Bengali text correctly.

## Setup and Installation (Windows)

### 1. Install Python

Install Python 3.12 from:

https://www.python.org/downloads/

Verify the installation:

```powershell
python --version
```

### 2. Download the Project

Download the repository from GitHub using **Code → Download ZIP**, extract it, and open the project folder in PyCharm.

Alternatively, clone the repository:

```powershell
git clone YOUR_GITHUB_REPOSITORY_URL
cd YOUR_PROJECT_FOLDER
```

Replace the example URL and folder name with your actual repository details.

### 3. Configure the Python Interpreter

In PyCharm:

1. Open **Settings → Project → Python Interpreter**.
2. Select your Python 3.12 interpreter or create a virtual environment.
3. Open the PyCharm Terminal.

Create a virtual environment if needed:

```powershell
python -m venv .venv
```

Activate it:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 4. Install Dependencies

Ensure `requirements.txt` is present in the project root.

Run:

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 5. Configure the OpenRouter API Key

Create a `.env` file in the project root:

```dotenv
OPENROUTER_API_KEY=your_openrouter_api_key_here
```

Get your API key from:

https://openrouter.ai/keys

Replace the placeholder with your own key.

**Security:** Never commit `.env` or your API key to GitHub. The repository's `.gitignore` should exclude `.env`.

### 6. Run the Project

In PyCharm, open `amar_passport_agent.py` and click **Run**.

Alternatively, run it from the PyCharm Terminal:

```powershell
python amar_passport_agent.py
```

Follow the application's prompts and review the generated output in the Run Console or Terminal.

## Bengali Text Display

PyCharm is recommended because Bengali text displays correctly in its Console and Terminal in the tested setup.

If Bengali text appears incorrectly in another terminal or IDE, try a Bengali-compatible font and UTF-8 configuration. The exact fix may depend on the terminal renderer and installed fonts.

## Troubleshooting

- **Python not found:** Check the configured interpreter in PyCharm.
- **Missing dependencies:** Run `python -m pip install -r requirements.txt`.
- **API authentication error:** Verify your `.env` file, variable name, and OpenRouter API key.
- **Incorrect Bengali rendering:** Try running the project in PyCharm's Run Console or Terminal.
- **Outdated passport information:** Verify fees, requirements, and processing times through official Bangladesh e-Passport sources.

## Important Notes

- Internet access is required for API calls and any implemented live information retrieval.
- OpenRouter usage may incur charges depending on the model and provider.
- Local fallback data may not reflect current official requirements or fees.
- This project is an informational assistant, not an official Bangladesh e-Passport service.
