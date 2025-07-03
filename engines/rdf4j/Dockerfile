FROM maven:3.9.6

RUN mkdir /rdf4j

RUN mkdir /data
RUN mkdir /shapes
RUN mkdir /reports

# Set the working directory in the container
WORKDIR /rdf4j

# Copy the rest of the application code into the container
COPY . . 

## Compile application
RUN mvn clean package -DskipTests

## Command to run the compiled JAR
ENTRYPOINT ["java", "-Xmx32G" , "-Xms32G" , "-jar" , "target/validator-0.0.1-SNAPSHOT.jar"]

