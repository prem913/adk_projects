# Project for developing adk agents

* Install python latest version
* Install poetry on your system
* Run `poetry install`
* To activate the virtual environment run `poetry env activate`
* To run the application use `poetry run python src/launch.py`
* Or use `python src/launch.py` if venv is already activated

## API KEYS

* Create a .env file in root directory with following contents

```text
GOOGLE_API_KEY="<api_key>"
GOOGLE_GENAI_USE_VERTEXAI=FALSE
```
