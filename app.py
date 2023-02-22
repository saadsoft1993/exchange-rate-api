#!/usr/bin/env python3

import aws_cdk as cdk

from exchange_rate_api.exchange_rate_api_stack import ExchangeRateApiStack


app = cdk.App()
ExchangeRateApiStack(app, "exchange-rate-api")

app.synth()
