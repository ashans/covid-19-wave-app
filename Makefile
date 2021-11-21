WAVE_URL:=https://github.com/h2oai/wave/releases/download/v0.19.0/wave-0.19.0-darwin-amd64.tar.gz
WAVE_DIR:=$(shell pwd)/wave

venv:
	python3 -m venv venv
	./venv/bin/python3 -m pip install --upgrade pip

.PHONY: setup
setup: venv
	./venv/bin/pip3 install -r requirements.txt

wave:
	wget -O wave.tgz $(WAVE_URL)
	tar xzf wave.tgz
	mv wave-*-*-* wave
	rm -rf wave.tgz

# macOS specific:
.PHONY: run-wave
run-wave:
	osascript -e 'tell application "Terminal" to do script "cd $(WAVE_DIR) ; ./waved"'

.PHONY: run
run:
	./venv/bin/wave run app