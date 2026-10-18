.PHONY: download-data download-data-full validate pack clean

download-data:
	./scripts/download_data.sh

download-data-full:
	./scripts/download_data.sh --full

validate:
	python3 scripts/validate_submission.py

pack: validate
	python3 scripts/pack_submission.py

clean:
	rm -f submission.zip
