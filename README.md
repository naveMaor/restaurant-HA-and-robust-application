![System Architecture Diagram](https://i.ibb.co/z6YJrJF/Screenshot-1.png)


## HA and Robust Restaurant Application with Docker Compose

This project aims to develop a highly available and robust restaurant application using Docker Compose for a Software Engineering for Cloud Native Applications course. The assignment focuses on implementing key features such as persistence, fault tolerance, and load balancing.

### Features
1. **Containerized Services:** The application consists of four services:
   - Meals Service: Developed in Assignment #1, provides information about meals.
   - Diet Service: Developed for this assignment, handles diet-related functionalities.
   - Database Service: A pre-built service obtained from DockerHub, responsible for storing and managing data.
   - Reverse-Proxy Service: Another pre-built service from DockerHub (e.g., NGINX), used for routing requests.

2. **Persistent Storage:** Both the Meals Service and the Diet Service require persistent storage to maintain data integrity across restarts. The implementation should ensure that data is stored persistently in the database service.

3. **Fault Tolerance:** Docker Compose is utilized to handle failures and automatically restart the assignment and diet services upon failure. The application should seamlessly continue processing requests as if the failure never occurred, ensuring high availability.

4. **Reverse-Proxy Routing:** To efficiently route requests to the appropriate server, a reverse-proxy server (such as NGINX) is employed. The reverse-proxy examines the incoming requests and forwards them to the appropriate service (either Meals Service or Diet Service).

5. **Extra Credit - Load Balancing:** As an optional extra credit feature, load balancing can be implemented for the Meals Service. Load balancing ensures that incoming requests are evenly distributed among multiple instances of the Meals Service, improving performance and scalability.

### Technologies Used
- Docker Compose: Container orchestration tool used to manage the deployment and scaling of multiple services.
- Docker: Containerization platform used to package the application and its dependencies into containers.
- NGINX: A popular reverse-proxy server used to route requests to the appropriate services.
- Database Service: A pre-built Docker image or containerized database service for persistent storage.

### Goals
- Create a fault-tolerant and highly available application using Docker Compose.
- Ensure persistence for the Meals Service and the Diet Service by leveraging a persistent storage mechanism.
- Utilize Docker Compose to automatically restart failed services and maintain uninterrupted request processing.
- Implement a reverse-proxy server (e.g., NGINX) for efficient request routing.
- Implement load balancing for the Meals Service to distribute requests evenly.

By completing this assignment, I gain practical experience in building cloud-native applications that exhibit high availability, fault tolerance, and efficient request routing through the use of Docker Compose, reverse-proxy servers, and persistent storage mechanisms.
