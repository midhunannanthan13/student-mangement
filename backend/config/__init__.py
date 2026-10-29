"""
Use PyMySQL as the MySQL driver.

Why: the original steps use `mysqlclient`, which needs a C compiler on Windows
and cannot be built on Vercel. PyMySQL is pure Python, so the same code runs
on your laptop and on Vercel.
"""
import pymysql

pymysql.install_as_MySQLdb()
