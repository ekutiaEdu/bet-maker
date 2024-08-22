# bet-maker

## Issues
Since there is no persistent event storage as required:
1. It is possible to place a bet on an event that has already had its result set, meaning the event has already concluded.
2. It is possible to change the outcome of an event twice.