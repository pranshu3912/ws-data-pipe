This project intends to create a data pipeline to ingest, process and send streaming data to several downstream services to use as seen fit.

This project arose out of the necessity to get low interval trading data especially on forex, which is not available unless you pay a lot of money to data providers.

This is not the development repo, I had to use this alternate account to demonstrate my abilities as people were stealing code from my older projects, without giving credit.

Huge thanks to 0xrushi, without whose support this project would not have been possible.

### In this project the major components are - 
- A websocket connection to tradingview's websocket api
- A basic web interface to start and stop streaming data manually
- Processing scripts to go from raw data to sensible price data
- Strategies to trade on, using the price data
- A streaming pipeline to get data from the ingestion module to processing and further downstream activities, uses a queue much like Apache Kafka
- A simple script to send emails using Sendgrid (gmail security issues on receiver side, make sure to allow those mails)

### Further improvements will include
  - A dashboard for verifying price action data
  - Improvements on the pipeline
  - More websocket apis for data validation
  - Time series database for aggregation of data for future strategy testing
 
  The major sources for learning concepts required to build this came from Designing Data Intensive Applications, Confluent and MDN docs.


P.S. - I have not provided the full code so it would not be executable, this is a further step to prevent blatant copying of code.
Individual scripts are executable though, ingestion scripts work well, except on weekends because markets are closed then.
