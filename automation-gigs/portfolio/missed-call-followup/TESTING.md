| # | Input | Expected |
|---|-------|----------|
| 1 | Call at 2pm local, not answered | "open hours" SMS to caller within ~5s; Sheet row |
| 2 | Call at 9pm local, not answered | "after hours" SMS; Sheet row |
| 3 | Call answered (CallStatus=completed) | no SMS, no row |
