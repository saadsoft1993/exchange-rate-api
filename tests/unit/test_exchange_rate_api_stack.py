import aws_cdk as core
import aws_cdk.assertions as assertions
from exchange_rate_api.exchange_rate_api_stack import ExchangeRateApiStack


def test_sqs_queue_created():
    app = core.App()
    stack = ExchangeRateApiStack(app, "exchange-rate-api")
    template = assertions.Template.from_stack(stack)

    template.has_resource_properties("AWS::SQS::Queue", {
        "VisibilityTimeout": 300
    })


def test_sns_topic_created():
    app = core.App()
    stack = ExchangeRateApiStack(app, "exchange-rate-api")
    template = assertions.Template.from_stack(stack)

    template.resource_count_is("AWS::SNS::Topic", 1)
