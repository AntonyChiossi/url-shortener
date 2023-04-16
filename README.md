# Short.it
Yet another url shortener

## Requirements

- Main functionality: given a valid URL the system should provide a shortened alias for such url. For instance assume that https://www.wikipedia.org/ is passed as input, the system has to provide an alias such as https://shortener.com/abc1234, that redirect to such URL. If an user visits the alias it will redirected to the target URL.
- Traffic volume: Let's assume that shortener.com is a very popular website used world wide and it can handle on average 100 million URLs generations every day
- URI length: at most 32 characters
- Action that can be made on the URL (the alias):
  - creation
  - update (set/update expire time only)
  - deletion **not** allowed
- High availability
- Scalability
- Good Fault tolerace

## Back of the envelop estiomation

- 100 millions URLs created every day
- URLs created per second: 100M / 24 / 3600 = 1157 = ~1200
- Let's assume that the read/write ratio of 30:1: 1200 * 30 = ~36000
- System retention time is 7 years, so we must hadle: 100M * 365 * 7 = ~255B URLs
- Assume that the average length is 32 characters: 255B * 32bytes = ~8.2TB
