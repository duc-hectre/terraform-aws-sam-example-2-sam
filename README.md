## Introduction

This is the sample project to describe how to initiate & provision a serverless platform on AWS cloud using Terraform & SAM.
The approach is:

- Use Terraform:
  - To initiate & provision all the surrounding infrastructures such as sqs, dynamodb, code pipeline,... and corresponding IAM roles, policies
  - Use AWS Code Pipeline to integrate with Terraform image in docker-hup for CI/CD action.
  - There is a separated github repository for this part. Can find that repo here [Terraform part](https://github.com/duc-hectre/terraform-aws-sam-example-2-tf)
- Use SAM:
  - To develop, test & debug the source code of lambda function.
  - Build & deploy for API Gateway, Lambda as well as related IAM roles, policies.
  - There is a separated github repository for this part.

# Sample architecture

This project is to build a simple Todo application which allow user to record their todo action with some simple description likes Todo, Desc & Status.

The AWS structure is:

![Sample Architecture](https://github.com/duc-hectre/duc-hectre/blob/main/TF-SAM-APPROACH-2.png?raw=true)

# Get started.

Regarding to this sample, this is the repository for Terraform part, which contains the definition about SQS, DynamoDB, Code Pipeline for terraform deployment as well as SAM deployment.
The project structure looks like image below.

![Sample project structure](https://github.com/duc-hectre/duc-hectre/blob/main/tf_2_sam_project_structure.png)

If any changes not regarding to API gateway, Lambda, they will be defined in this terraform parts.

### How to run the project.

Following the steps below to get the project starts.

1. **Install prerequisites**

   - Install AWS CLI tool
     An AWS account with proper permission with the services we are intend to initiate & use.

   - Install AWS CLI tool [Installing or updating the latest version of the AWS CLI - AWS Command Line Interface ](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)

   - Install AWS SAM CLI tool [Installing the AWS SAM CLI - AWS Serverless Application Model ](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html)

   - Install Docker - that use to simulate the AWS environment for debugging

   - Install some extensions for VS Code:

     - AWS Toolkit [AWS Toolkit for Visual Studio Code - AWS Toolkit for VS Code ](https://docs.aws.amazon.com/toolkit-for-vscode/latest/userguide/welcome.html)

2. **Run locally**

   To run the lambda locally. Navigate the corresponding SAM folder of lambda function then using SAM CLI below:

   ```
   sam local invoke -d 3000 -e event.json TodoFunction
   ```

   or

   ```
   sam local invoke -d 3000 -e event.json TodoPersistFunction
   ```

   for example a SAM template for TodoFunction to handler user request from API gateway and send data to SQS.

   ```
    AWSTemplateFormatVersion: '2010-09-09'
    Transform: AWS::Serverless-2016-10-31
    Description: >
    Todo lambda function
    Globals:
    Function:
        Timeout: 3


    Parameters:
    AppName:
        Type: String
        Description: Name of application (no spaces). Value must be globally unique
        Default: todo-a2
    Environment:
        Type: String
        Description: Name of application (no spaces). Value must be globally unique
        Default: dev
    DynamoDbName:
        Type: AWS::SSM::Parameter::Value<String>
        Description: Name of application (no spaces). Value must be globally unique
        Default: /dev/todo-a2/dynamodb_name
    SQSQueueName:
        Type: AWS::SSM::Parameter::Value<String>
        Description: Name of application (no spaces). Value must be globally unique
        Default: /dev/todo-a2/sqs_queue_name
    DynamoDbArn:
        Type: AWS::SSM::Parameter::Value<String>
        Description: Name of application (no spaces). Value must be globally unique
        Default: /dev/todo-a2/dynamodb_arn
    SQSQueueArn:
        Type: AWS::SSM::Parameter::Value<String>
        Description: Name of application (no spaces). Value must be globally unique
        Default: /dev/todo-a2/sqs_queue_arn

    Resources:
    TodoFunction:
        Type: AWS::Serverless::Function # More info about Function Resource: https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlessfunction
        Properties:
        FunctionName:
            Fn::Sub: "${Environment}_${AppName}_todo_handler"
        CodeUri: ./lambda/src/todo_handler/
        Handler: main.lambda_handler
        Runtime: python3.8
        Architectures:
            - x86_64
        Policies:
            - DynamoDBCrudPolicy:
                TableName: !Ref DynamoDbName
            - SQSSendMessagePolicy:
                QueueName: !Ref SQSQueueName

        Events:
            AnyTodoApi:
            Type: Api # More info about API Event Source: https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#api
            Properties:
                Path: /todo
                Method: any
        Environment:
            Variables:
            DYNAMO_TABLE_NAME: !Ref DynamoDbName
            SQS_URL:
                Fn::Sub: "https://sqs.ap-southeast-1.amazonaws.com/983670951732/${SQSQueueName}"

    TodoPersistFunction:
        Type: AWS::Serverless::Function # More info about Function Resource: https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#awsserverlessfunction
        Properties:
        FunctionName:
            Fn::Sub: "${Environment}_${AppName}_todo_persist"
        CodeUri: ./lambda/src/todo_persist/
        Handler: main.lambda_handler
        Runtime: python3.8
        Architectures:
            - x86_64
        Policies:
            - DynamoDBCrudPolicy:
                TableName: !Ref DynamoDbName
            - SQSPollerPolicy:
                QueueName: !Ref SQSQueueName
        Events:
            TodoQueue:
            Type: SQS
            Properties:
                Queue: !Ref SQSQueueArn
                BatchSize: 10
                Enabled: false
        Environment:
            Variables:
            DYNAMO_TABLE_NAME: !Ref DynamoDbName

    Outputs:
    TodoFunction:
        Description: "Todo Api Handler Lambda Function ARN"
        Value: !GetAtt TodoFunction.Arn
    TodoFunctionRole:
        Description: "Implicit  Role created for Todo Api Handler function"
        Value: !GetAtt TodoFunctionRole.Arn
    TodoPersistFunction:
        Description: "Todo Persistent Lambda Function ARN"
        Value: !GetAtt TodoPersistFunction.Arn
    TodoPersistFunctionRole:
        Description: "Implicit  Role created for Todo Persistent function"
        Value: !GetAtt TodoPersistFunctionRole.Arn
   ```

3. **Debug**

   To debug the lambda function, open the launch.json file located in ./vscode/ folder, then add new SAM profile or edit the existing profiles to set difference input according to different scenarios to test.
   Pay attention to these parameters **TemplatePath, LogicalId, API** accordingly.

   ```
   {
    // Use IntelliSense to learn about possible attributes.
    // Hover to view descriptions of existing attributes.
    // For more information, visit: https://go.microsoft.com/fwlink/?linkid=830387
    "version": "0.2.0",
    "configurations": [
        {
        "type": "aws-sam",
        "request": "direct-invoke",
        "name": "SAM local debug - todo-handler - POST",
        "invokeTarget": {
            "target": "api",
            "templatePath": "${workspaceFolder}/template.yaml",
            "logicalId": "TodoFunction"
        },
        "api": {
            "path": "/todo",
            "httpMethod": "post",
            "payload": {
            "json": { "todo": "Initiate sam project 01" }
            }
        }
        },
        {
        "type": "aws-sam",
        "request": "direct-invoke",
        "name": "SAM local debug - todo-handler - GET",
        "invokeTarget": {
            "target": "api",
            "templatePath": "${workspaceFolder}/template.yaml",
            "logicalId": "TodoFunction"
        },
        "api": {
            "path": "/todo",
            "httpMethod": "get"
        }
        },
        {
        "type": "aws-sam",
        "request": "direct-invoke",
        "name": "SAM local debug - todo-persisit - SQS",
        "invokeTarget": {
            "target": "template",
            "templatePath": "${workspaceFolder}/template.yaml",
            "logicalId": "TodoPersistFunction"
        },
        "sam": {
            "localArguments": ["-e", "${workspaceFolder}/events/event.json"]
        }
        }
    ]
    }
   ```

   Once ok, can use F5 in VS Code to start the lambda function & debug.

4. **Build**

   To build the deployment package of lambda function. Navigate the corresponding SAM folder of lambda function then using SAM CLI below:

   ```
   sam build
   ```

5. **Deploy**

   Can manually deploy the SAM template by using CLI below:

   ```
   sam deploy --guided --stack-name <name-of-stack> --capabilities CAPABILITY_IAM
   ```

   Once the SAM pipeline has been deployed by Terraform part. To deploy the SAM project, just need to push the changes to corresponding github repository.

   Refer to the image below for the SAM pipeline

   ![SAM CI/CD](https://github.com/duc-hectre/duc-hectre/blob/main/tf_1_sam_cicd_pipeline.png)

6. **Destroy**

   To destroy all the AWS resources defined by Terraform, using the CLI below:

   ```
   aws cloudformation delete-stack --stack-name <name-of-stack>
   ```
