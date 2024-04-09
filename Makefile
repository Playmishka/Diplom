all: run

run:
	uvicorn main:app --reload
