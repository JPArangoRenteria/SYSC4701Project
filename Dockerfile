#FROM python:3.8-slim
FROM ubuntu:20.04
# Install dependencies to set up virtual environment
WORKDIR /app
RUN ln -fs /usr/share/zoneinfo/UTC /etc/localtime && dpkg-reconfigure --frontend noninteractive tzdata
RUN apt-get update && apt-get install -y \
    python3 \
    python3-venv \
    python3-pip \
    wireshark \
    && apt-get clean
    
RUN python3 -m venv /venv

# Activate the virtual environment
ENV PATH="/venv/bin:$PATH"

# Install required Python packages
RUN pip install wheel
RUN pip install setuptools==67.6.1
RUN pip install eventlet==0.30.2
RUN pip install ryu
RUN pip install mininet
RUN pip install pyshark
#RUN pip install csv
RUN pip install argparse
RUN pip install datetime


# Copy the Ryu controller script and other necessary scripts into the container
COPY ryu_controller.py /app/ryu_controller.py
COPY mininet-sim.py /app/mininet-sim.py
COPY network_metrics_to_csv.py /app/network_metrics_to_csv.py

# Create a new bash script to execute the setup
COPY run_sim.sh /run_sim.sh

# Make the script executable
RUN chmod +x /run_sim.sh

# Run the bash script to set up the environment and start the simulation
CMD ["/run_sim.sh"]

