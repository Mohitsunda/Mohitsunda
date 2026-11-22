.PHONY: install demo full test check app notebooks

install:
	python -m pip install -r requirements-dev.txt
	python -m pip install -e . --no-deps

demo:
	portfolio build --source demo

full:
	portfolio build --source full

test:
	pytest -q

check:
	ruff check .
	ruff format --check .
	pytest -q

app:
	streamlit run streamlit_app.py

notebooks:
	python scripts/execute_notebooks.py
