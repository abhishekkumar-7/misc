import sys
import boto3, logging, botocore
from botocore.exceptions import ClientError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

def get_info(region):
    f = open("output-"+region+".csv", "w")
    f.write('tag,app_name,env_name,env_ID,visibility\n')
    eb = boto3.client('elasticbeanstalk', region)
    try:
        # Calling ElasticBeanStalk client to describe environments
        env_response = eb.describe_environments()
    except botocore.exceptions.ClientError as error:
        logger.error('API error while getting environments with error: ' + error)
        return

    for item in env_response['Environments']:
        app_name = item['ApplicationName']
        env_name = item['EnvironmentName']
        env_id = item['EnvironmentId']
        env_arn = item['EnvironmentArn']

        try:
            # Calling ElasticBeanStalk client to list tags
            tag_response = eb.list_tags_for_resource(
                ResourceArn=env_arn
            )
        except botocore.exceptions.ClientError as error:
            logger.error('API error while getting tags with error: ' + error)
            continue
        tag = ''
        for t in tag_response['ResourceTags']:
            if t['Key'] == 'Env':
                tag = t['Value']

        try:
            # Calling ElasticBeanStalk client to get configuration settings
            config_response = eb.describe_configuration_settings(
                ApplicationName=app_name,
                EnvironmentName=env_name
            )
        except botocore.exceptions.ClientError as error:
            logger.error('API error while getting tags with error: ' + error)
            continue

        option_settings = config_response['ConfigurationSettings'][0]
        for sett in option_settings['OptionSettings']:
            if sett['OptionName'] == 'ELBScheme':
                print(tag+','+app_name + ',' + env_name + ',' + env_id + ',' + sett['Value'])
                f.write(tag + ',' + app_name + ',' + env_name + ',' + env_id + ',' + sett['Value'] + '\n')


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    get_info('us-west-2')
    get_info('us-east-1')
