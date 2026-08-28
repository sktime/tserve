# Adapted from granite-tsfm / Hugging Face transformers:
# https://github.com/huggingface/transformers/tree/main
.PHONY: quality style

check_dirs := src tests

quality:
	uv run ruff check $(check_dirs)
	uv run ruff format --check $(check_dirs)
	uv run ty check

style:
	uv run ruff check $(check_dirs) --fix
	uv run ruff format $(check_dirs)
