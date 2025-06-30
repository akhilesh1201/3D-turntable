python3 -m venv .venv
source .venv/bin/activate

sudo apt install libgpiod-dev
sudo apt install uvicorn

uvicorn turntable_api.py:app --host 0.0.0.0 --port 8000