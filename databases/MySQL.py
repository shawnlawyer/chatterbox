from peewee import MySQLDatabase
from envs import env

database = MySQLDatabase(host=env('MYSQL_HOST'),
                         port=env('MYSQL_PORT', var_type='integer'),
                         user=env('MYSQL_USER'),
                         passwd=env('MYSQL_PASSWORD'),
                         database=env('MYSQL_DATABASE'))
