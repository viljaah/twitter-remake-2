# twitter-remake-2

## Goals
• Implement “likes” as a part of your website, if not already added.
• Limit unnecessary traTic to the API and database using caching. Both between
web server and API, and API and database.
• Limit unnecessary traTic to the database by sending likes in batches/in bulk.
• Improve the speed of the architecture by adding load balancing.
• Implement logging of requests for the API. Logs should be accessible from the
/logs endpoint.


### new architecture to update + new features to implement
Key Components to Implement:

1. Load Balancer with Caches -MODESTA
Purpose: Reduce unnecessary read requests to the API
Functionality: Cache GET requests for 1 minute
Implementation: Python containers using dictionaries
Architecture: Dockerized containers between web server and API

2. Like Batcher- VILJA
- Like tweets -> The like button does not have to track which users has liked. Idempotence be damned! It can simply be a “make the database number one larger each time I click it”-
button.  

Purpose: Handle high volumes of "like" operations efficiently
Functionality: Batch like operations and send them to the database when:
A post has more than 10 likes accumulated
Likes haven't been passed to the database in over 1 minute
Implementation: Python with local storage

3. DB Cache -MODESTA
Purpose: Similar to the API caches but between API and database
Functionality: Cache read operations with 1-minute timeout
Implementation: Python

4. Logger
Purpose: Track API usage
Functionality: Log all API calls and database accesses
Endpoint: Accessible at /logs
Format: Include method and endpoint (e.g., ["GET", "/like/123"])

## Report Requirements
Your report should focus on the new components added in Assignment 2, including:

Design and architecture choices
Justification for your implementation decisions
Discussion of the scalability approaches (like the like batcher)
Analysis of how these components would perform under different traffic scenarios
