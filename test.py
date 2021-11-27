if pgrep -f "/usr/bin/python3 /home/madnanua/git/cryptobot/autobot-2.py
" &>/dev/null; then
    echo "it is already running"
    exit
else
    /usr/bin/python3 /home/madnanua/git/cryptobot/autobot-2.py

fi