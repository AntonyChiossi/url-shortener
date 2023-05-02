# Short.it
Yet another URL shortener

## Requirements

- Main functionality: given a valid URL, the system should provide a shortened alias for such url. For instance, assume that https://www.wikipedia.org/ is passed as input, the system has to provide an alias such as https://short.it/abc1234, that redirect to such URL. If a user visits the alias, it will redirect to the target URL (https://www.wikipedia.org/).
- Traffic volume: Let's assume that short.it is a very popular website used worldwide and it can handle on average 10 million URLs generations every day
- URI length: at most 32 characters
- An action that can be done on the URL (the alias):
  - Create
  - Read
  - Update: **not** allowed
  - Delete: **not** allowed. Soft delete will be applyed at expiration time.
- URL visits statistics must be collected and visible only to the owner
- When a URL has an expiration date, it should stop redirecting to the target URL at the time of expiration. The owner of the URL should also be notified of the expiration and receive statistics about the URL's traffic.
- High availability
- Scalability
- Good Fault tolerance

## Back of the envelope estimation
For the purpose of this rough estimation, let's make the assumption that short.it is a highly popular website with a large global user base.

- 10 millions URLs created every day
- The URLs created per second: 10M / 24 / 3600 = 115 = ~120 (write/s)
- Let's assume that the read/write ratio of 30:1: 120 * 30 = ~3600 (read/s)
- System retention time is 10 years, so we must hadle: 10M * 365 * 10 = ~37B URLs
- Assume that the average length is 32 characters: 37B * 32bytes = ~1.5TB

## Architecture and Design
![arch-design](https://user-images.githubusercontent.com/26548787/235768215-f4389258-355f-41d8-aa94-e1953f8b443d.png)

The URL shortener service is designed to be scalable and reliable. To achieve this goal, we used a microservices architecture based on the following components:

- **Load Balancer** (NGINX): A reverse proxy server that distributes incoming traffic to multiple stateless web servers. NGINX provides high availability, scalability, and security by distributing requests across multiple web servers.
- Stateless **Web Servers** (Django): We used Django, a Python-based web framework, to build the stateless web servers. The web servers handle incoming requests, perform business logic, and return responses to the client. They don't store any state on the server side, which makes them horizontally scalable.
- **Async Tasks** (Celery with RabbitMQ): For tasks that are slow or resource-intensive, we used Celery with RabbitMQ as the message broker. Celery allows us to perform tasks asynchronously and in the background leveraging RabbitMQ.
- **Database** (PostgreSQL): We used PostgreSQL as the primary database for the project. PostgreSQL is a reliable and scalable database that supports ACID transactions and provides high data integrity and consistency.
- **Cache** (Redis): To speed up the response time and reduce the load on the database, we used Redis as the cache layer.
    
## Installation

**Warning**: Please note that the software provided is not intended for production use. The Dockerized solution is intended as a proof-of-concept only. For deployment in a real production scenario, we recommend provisioning the services on dedicated machines for optimal **performance** and **security**.

- `git clone git@github.com:AntonyChiossi/url-shortener.git`
- `cd url-shortener && mkdir -p data/{db}`
- `cd frontend && ng build --base-href /app/ && cd ..`
- `docker-compose -f docker-compose.yml --env-file .env.dev build`
- `docker-compose -f docker-compose.yml --env-file .env.dev up -d` (this should start 3 instances of the api server; if you dont see all them running run `docker-compose -f docker-compose.yml down` and repeat this step )

## What has been implemented
- [x] Load balancer 
- [x] Web server scaling (stateless)
- [ ] Database scaling (currently there is no replication or sharding)
- [ ] Caching (an LRU cache can be added to reduce db reads)
- [ ] Security (the code is far from secure, there is no hardening, default passwords, 
