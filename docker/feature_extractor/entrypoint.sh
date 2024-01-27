#!/bin/bash

# Activate the Conda environment
source /opt/conda/bin/activate torch_zoo

# Run the application
exec python endpoint.py
