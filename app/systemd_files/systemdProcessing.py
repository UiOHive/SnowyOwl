[Unit]
Description=Process LiDAR data
After=network.target

[Service]
ExecStart=/usr/bin/python3 /home/data/LIVOX/SnowyOwlProcessing_Finse.py

[Install]
WantedBy=network.target
