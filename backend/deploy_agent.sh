#!/bin/bash
pip install requests
wget http://your-backend-host/agent.py -O agent.py
python agent.py --register --config agent_config.json
