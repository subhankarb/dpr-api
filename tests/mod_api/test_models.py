from app import create_app
import boto3
import unittest
from app.mod_api.models import MetaDataS3
from moto import mock_s3


class MetadataS3TestCase(unittest.TestCase):

    def setUp(self):
        self.app = create_app()

    def test_metadata_s3_key(self):
        metadata = MetaDataS3(publisher="pub_test", package="test_package")
        expected = "{t}/pub_test/test_package/_v/latest/datapackage.json".format(t=metadata.prefix)
        assert expected == metadata.build_s3_key()

    def test_metadata_s3_prefix(self):
        metadata = MetaDataS3(publisher="pub_test", package="test_package")
        expected = "{t}/pub_test".format(t=metadata.prefix)
        assert expected == metadata.build_s3_prefix()

    @mock_s3
    def test_save(self):
        with self.app.app_context():
            s3 = boto3.resource('s3')
            bucket_name = self.app.config['S3_BUCKET_NAME']
            bucket = s3.Bucket(bucket_name)
            bucket.create()
            metadata = MetaDataS3(publisher="pub_test", package="test_package", body='hi')
            key = metadata.build_s3_key()
            metadata.save()
            obs_list = list(s3.Bucket(bucket_name).objects.filter(Prefix=key))
            assert 1 == len(obs_list)
            assert key == obs_list[0].key

    @mock_s3
    def test_get_metadata_body(self):
        with self.app.app_context():
            s3 = boto3.resource('s3')
            bucket_name = self.app.config['S3_BUCKET_NAME']
            bucket = s3.Bucket(bucket_name)
            bucket.create()
            metadata = MetaDataS3(publisher="pub_test", package="test_package", body='hi')
            bucket.put_object(Key=metadata.build_s3_key(), Body=metadata.body)
            assert metadata.body == metadata.get_metadata_body()

    @mock_s3
    def test_get_all_metadata_name_for_publisher(self):
        with self.app.app_context():
            s3 = boto3.resource('s3')
            bucket_name = self.app.config['S3_BUCKET_NAME']
            bucket = s3.Bucket(bucket_name)
            bucket.create()
            metadata = MetaDataS3(publisher="pub_test", package="test_package", body='hi')
            bucket.put_object(Key=metadata.build_s3_key(), Body=metadata.body)
            assert 1 == len(metadata.get_all_metadata_name_for_publisher())