# setup pip environment variables
export PIP_REQUIRE_VIRTUALENV=true
export PIP_RESPECT_VIRTUALENV=true

if [ -z "$WORKON_HOME" ]; then
    export PIP_VIRTUALENV_BASE=$WORKON_HOME
fi

# run pip
pip install -r requirements.txt

