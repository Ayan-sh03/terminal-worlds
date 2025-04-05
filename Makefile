# Makefile to run story_cli_groq.py

PYTHON := python
SCRIPT := main.py

run:
	$(PYTHON) $(SCRIPT)

.PHONY: run