from constructs import Construct

from aws_cdk import (
    Duration,
    Stack,
    aws_dynamodb as dynamodb_cdk,
    aws_lambda as lambda_cdk,
    aws_events as events,
    aws_events_targets as targets,
    aws_apigateway as apigateway_cdk,
)


class ExchangeRateApiStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create DynamoDB table
        exchange_table_cdk = dynamodb_cdk.Table(self, "currency_table",
                partition_key=dynamodb_cdk.Attribute(name="id", 
                type=dynamodb_cdk.AttributeType.STRING))
        
        # Create Lambda function for Exchange Rates
        exchange_lambda_cdk = lambda_cdk.Function(self, "exchange_lambda_cdk",
                code=lambda_cdk.Code.from_asset("./lambda/currency"),
                handler="exchange_lambda.lambda_handler",
                runtime=lambda_cdk.Runtime.PYTHON_3_7)
        
        # Create Lambda function for Exchange Rates
        scrap_lambda_cdk = lambda_cdk.Function(self, "scrap_lambda_cdk",
                code=lambda_cdk.Code.from_asset("./lambda/scrap"),
                timeout=Duration.seconds(300),
                handler="scrap_lambda.lambda_handler",
                runtime=lambda_cdk.Runtime.PYTHON_3_7)
        
        # Update Environment Variables
        exchange_lambda_cdk.add_environment("TABLE_NAME", exchange_table_cdk.table_name)
        scrap_lambda_cdk.add_environment("TABLE_NAME", exchange_table_cdk.table_name)

        # Grant Lambda permission to access DynamoDB
        exchange_table_cdk.grant_write_data(scrap_lambda_cdk)
        exchange_table_cdk.grant_read_data(exchange_lambda_cdk)

        # Create ApiGateway, point to above Lambda
        
        customer_api_cdk = apigateway_cdk.LambdaRestApi(self, "customer_api_cdk",
                        handler=exchange_lambda_cdk,
                        proxy=False)
        get_currency_resource = customer_api_cdk.root.add_resource('get_exchange_rates')
        get_currency_resource.add_method("GET")

        scrap_currency_api_resource = customer_api_cdk.root.add_resource('scrap_content')
        scrap_currency_api_resource.add_method("GET")

        rule = events.Rule(
            self, "Rule",
            schedule=events.Schedule.cron(
                minute='0',
                hour='4',
                month='*',
                week_day='MON-FRI',
                year='*'),
        )
        rule.add_target(targets.LambdaFunction(scrap_lambda_cdk))

