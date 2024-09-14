# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y git nmap sqlmap whatweb dirb gobuster hydra-gtk curl gnupg2 \
    postgresql libgmp-dev zlib1g-dev libpcap-dev build-essential libreadline-dev \
    libssl-dev libpq-dev libsqlite3-dev libffi-dev libyaml-dev libxslt1-dev libxml2-dev \
    libcurl4-openssl-dev software-properties-common ruby ruby-dev ncat hashcat john unzip pandoc && \
    apt-get clean

# Install Metasploit Framework
RUN curl -o /tmp/msfinstall https://raw.githubusercontent.com/rapid7/metasploit-omnibus/master/config/templates/metasploit-framework-wrappers/msfupdate.erb && \
    chmod 755 /tmp/msfinstall && \
    /tmp/msfinstall && \
    rm /tmp/msfinstall

# Install Nikto
RUN git clone https://github.com/sullo/nikto.git /opt/nikto && \
    ln -s /opt/nikto/program/nikto.pl /usr/local/bin/nikto

# Install WPScan
RUN gem install wpscan

# Download and unpack wordlists
RUN curl -L -o /tmp/wordlists.zip https://github.com/kkrypt0nn/wordlists/archive/refs/heads/master.zip && \
    unzip /tmp/wordlists.zip -d /tmp && \
    mv /tmp/wordlists-main /usr/share/wordlists && \
    rm /tmp/wordlists.zip

# Install fish shell and pylint
RUN apt-get install -y fish pylint && \
    chsh -s /usr/bin/fish

# Create a Python virtual environment
RUN python3 -m venv /app/env

# Activate the virtual environment and install pip in it
RUN /app/env/bin/pip install --upgrade pip

# Install dependencies in the virtual environment
RUN /app/env/bin/pip install --no-cache-dir -r requirements.txt

# Install the pipeline package in editable mode
RUN /app/env/bin/pip install -e .

# Clone the SearchSploit repository
RUN git clone -b main https://gitlab.com/exploit-database/exploitdb.git /opt/exploit-database

# Create a symbolic link to make SearchSploit accessible
RUN ln -sf /opt/exploit-database/searchsploit /usr/local/bin/searchsploit

# Copy the resource file to the home directory
RUN cp -n /opt/exploit-database/.searchsploit_rc ~/

# Modify the searchsploit script to remove sudo and fix paths
RUN sed -i 's/sudo //g' /opt/exploit-database/searchsploit
RUN sed -i 's|/opt/exploitdb|/opt/exploit-database|g' /opt/exploit-database/searchsploit
RUN sed -i 's|master|main|g' /opt/exploit-database/searchsploit

# Set environment variables if needed
ENV PATH="/usr/local/bin:$PATH"

# Update SearchSploit
# RUN timeout 60 searchsploit -u || echo "Update process completed with errors"

# Installing net-tools
# Install additional tools like net-tools
RUN apt-get install -y net-tools

# Expose the necessary port for Metasploit
EXPOSE 3790

# Ensure that the correct environment is activated by default
ENV VIRTUAL_ENV=/app/env
ENV PATH="/app/env/bin:$PATH"

# Set the entrypoint to an interactive shell
CMD ["bash"]
