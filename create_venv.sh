if [ ! -e .venv ]
then
    python -m venv ./.venv
fi

. ./.venv/bin/activate

python -m pip install -r backend/requirements.txt
