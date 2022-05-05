FROM continuumio/miniconda:latest 

WORKDIR /home/greenpoint


COPY boot.sh ./
RUN chmod +x boot.sh 

# COPY environment.yml ./ 
# RUN conda env create -f environment.yml

# Create the environment:
COPY environment.yml .
RUN conda env create -f environment.yml > build.log

# Initialize conda in bash config fiiles:
RUN conda init bash

# Activate the environment, and make sure it's activated:
RUN conda activate gpsim
RUN echo "Make sure flask is installed:"
RUN python -c "import flask"

# RUN echo "source activate gpsim" > ~/.bashrc ENV PATH /opt/conda/envs/gpsim/bin:$PATH 

COPY ./ ./

EXPOSE 5000 
ENTRYPOINT ["./boot.sh"]