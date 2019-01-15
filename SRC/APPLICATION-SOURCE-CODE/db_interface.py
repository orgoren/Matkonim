#!/usr/bin/env python
import os
import sys
import datetime
import MySQLdb as mdb
import sshtunnel
import getpass
import queries
import re
from utils import *
SERVER_PORT = 3306
DB_USERNAME = "DbMysql11"
DB_PASSWORD = "DbMysql11"
DB_NAME = "DbMysql11"
VALID_RANDOM_PORT = 40326

def main():

	username = raw_input("enter username (for nova): ")
	password = getpass.getpass("enter password (for nova): ")
	with sshtunnel.SSHTunnelForwarder(
			('nova.cs.tau.ac.il', 22),
			ssh_username=username,
			ssh_password=password,
			remote_bind_address=("mysqlsrv1.cs.tau.ac.il", 3306),
			local_bind_address=("127.0.0.1", 3307)
	) as tunnel:
		con = mdb.connect(host='127.0.0.1',    # your host, usually localhost
							 user=DB_USERNAME,         # your username
							 passwd=DB_PASSWORD,  # your password
							 db=DB_NAME,
							 port = 3307)        # name of the data base
		cur = con.cursor(mdb.cursors.DictCursor)


		while True:
			query_lines = []
			query = ""
			query = raw_input("Enter a query:\n")
			while query != "end":
				query_lines.append(query)
				query = raw_input()

				if query == "break":
					cur.close()
					exit(0)

			query = " ".join(query_lines)
			# query = "Select * from NUTRITIONS"

			if query == "":
				print "ERROR: no query in input"

			else:
				try:
					cur.execute(query)
					ans = cur.fetchall()
					print ans
				except Exception as e:
					print e


		#res = [item['recipe_name'] for item in cur.fetchall()]
		cur.close()


if __name__ == "__main__":
	main()