SCRIPT=`readlink -f $0`
SCRIPT_PATH=`dirname $SCRIPT`

# setup pip environment variables
export PIP_REQUIRE_VIRTUALENV=true
export PIP_RESPECT_VIRTUALENV=true

if [ -z "$WORKON_HOME" ]; then
    export PIP_VIRTUALENV_BASE=$WORKON_HOME
fi

# run pip
pip install -r $SCRIPT_PATH/requirements_server.txt
