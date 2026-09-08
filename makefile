.PHONY: install run debug clean lint lint-strict package

install:
	uv sync
	UV_SKIP_WHEEL_FILENAME_CHECK=1 uv pip install mazegenerator-00001-py3-none-any.whl

run:
	uv run python main.py src/jsons/config.json

debug:
	uv run python -m pdb main.py src/jsons/config.json

clean:
	rm -rf __pycache__ src/__pycache__ .mypy_cache .pytest_cache *.egg-info build dist /tmp/flake8_out.txt /tmp/subject_text.txt

lint:
	uv run flake8 src/
	uv run mypy src/ --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	uv run flake8 src/
	uv run mypy src/ --strict

package:
	bash package.sh
