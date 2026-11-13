Reads got faster after the move. Median read latency fell from 40 ms to 12 ms.

Writes stayed slow, because every write waits for two replicas to confirm. Three nodes make two replicas a majority.

The team chose quorum writes over speed, since lost writes cost more than slow writes.
