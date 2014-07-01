
#!/usr/bin/env bash
#
# push message files to Transifex.
#
# run once for a batch of jobs, and only on master branch
echo $TRAVIS_JOB_NUMBER | grep "\.1$"
if [ $? -eq 0 ] && [ $TRAVIS_BRANCH == master ]; then
    echo "Submitting translation files to Transifex”
    cd tendenci
    django-admin.py makemessages -a
    pip install "transifex-client==0.10"
    # create .transifexrc file
    echo "[https://www.transifex.com]" > ~/.transifexrc
    echo "hostname = https://www.transifex.com" >> ~/.transifexrc
    echo "password = $TENDENCI_TRANSIFEX_PASSWORD" >> ~/.transifexrc
    echo "token =" >> ~/.transifexrc
    echo "username = tendenci" >> ~/.transifexrc
    tx push --source --translations --no-interactive --skip
fi
