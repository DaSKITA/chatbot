# Extend the official Rasa SDK image
FROM rasa/rasa-sdk:2.3.1

# Use subdirectory as working directory
WORKDIR /app

# Copy any additional custom requirements, if necessary (uncomment next line)
#COPY actions/requirements-actions.txt ./

# Change back to root user to install dependencies
USER root

#RUN pip install tilt
#RUN pip install pytz
# Install extra requirements for actions code, if necessary (uncomment next line)
RUN pip install -r actions/requirements-actions.txt

# Copy actions folder to working directory
#COPY ./actions /app/actions
#RUN mkdir /etc/rasa
#COPY credentials.yml /etc/rasa/
#COPY credentials.yml /app/

#RUN cp /app/credentials.yml /etc/rasa/

# By best practices, don't run the code with root user
USER 1001