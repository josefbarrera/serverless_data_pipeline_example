import io
import sys
import zipfile
import boto3
# these libraries are not available via pypi but they are available in the glue environment on aws
from awsglue.utils import getResolvedOptions


def main():
    args = getResolvedOptions(sys.argv, ['source_bucket', 'source_key', 'destination_bucket', 'destination_key'])
    print('args parsed : {}'.format(args))

    source_bucket = args["source_bucket"]
    source_key = args["source_key"]
    destination_bucket = args["destination_bucket"]
    destination_key = args["destination_key"]

    s3_client = boto3.client('s3')
    s3_object = boto3.resource('s3').Object(bucket_name=source_bucket, key=source_key)
    zip_file_byte_object = io.BytesIO(s3_object.get()["Body"].read())
    zip_file = zipfile.ZipFile(zip_file_byte_object)
    name_list = zip_file.namelist()
    ret_val = []
    for email_path in name_list:
        print('processing email path {}'.format(email_path))
        email = zip_file.open(email_path)
        email_byte_object = io.BytesIO(email.read())
        full_destination_key = destination_key + email_path
        print('uploading object to {}'.format(full_destination_key))
        s3_client.upload_fileobj(email_byte_object, destination_bucket, full_destination_key)
        email.close()
        ret_val.append(full_destination_key)
    print('stopped unzip')
    return ret_val


if __name__ == '__main__':
    main()
