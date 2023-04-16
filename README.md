# Short.it
Yet another URL shortener

## Requirements

- Main functionality: given a valid URL, the system should provide a shortened alias for such url. For instance, assume that https://www.wikipedia.org/ is passed as input, the system has to provide an alias such as https://short.it/abc1234, that redirect to such URL. If a user visits the alias, it will redirect to the target URL (https://www.wikipedia.org/).
- Traffic volume: Let's assume that short.it is a very popular website used worldwide and it can handle on average 100 million URLs generations every day
- URI length: at most 32 characters
- An action that can be done on the URL (the alias):
  - Creation
  - Update (set/update expire time only)
  - Deletion **not** allowed. Soft delete will be applyed at expiration time.
- URL visits statistics must be collected and visible only to the owner
- When a URL has an expiration date, it should stop redirecting to the target URL at the time of expiration. The owner of the URL should also be notified of the expiration and receive statistics about the URL's traffic.
- High availability
- Scalability
- Good Fault tolerance

## Back of the envelope estimation
For the purpose of this rough estimation, let's make the assumption that short.it is a highly popular website with a large global user base.

- 100 millions URLs created every day
- The URLs created per second: 100M / 24 / 3600 = 1157 = ~1200 (write/s)
- Let's assume that the read/write ratio of 30:1: 1200 * 30 = ~36000 (read/s)
- System retention time is 7 years, so we must hadle: 100M * 365 * 7 = ~255B URLs
- Assume that the average length is 32 characters: 255B * 32bytes = ~8.2TB
