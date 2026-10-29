from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = "Shows which database the project is connected to (and hides the password)."

    def handle(self, *args, **options):
        db = settings.DATABASES["default"]
        engine = db["ENGINE"].split(".")[-1]

        self.stdout.write("")
        self.stdout.write(f"  Settings file : {settings.ENV_FILE_IN_USE}")
        self.stdout.write(f"  Engine        : {engine}")

        if engine == "mysql":
            self.stdout.write(f"  Host : port   : {db['HOST']} : {db['PORT']}")
            self.stdout.write(f"  Database      : {db['NAME']}")
            self.stdout.write(f"  User          : {db['USER']}")
        else:
            self.stdout.write(f"  File          : {db['NAME']}  (quick-test mode, DB_HOST is empty)")

        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT sqlite_version()" if engine == "sqlite3" else "SELECT VERSION()")
                version = cursor.fetchone()[0]
        except Exception as error:
            self.stdout.write("")
            self.stdout.write(self.style.ERROR(f"  CONNECTION FAILED: {error}"))
            self.stdout.write("  Check the values in your settings file, and that the database server is running.")
            self.stdout.write("")
            return

        self.stdout.write(f"  Server version: {version}")

        if engine == "mysql":
            with connection.cursor() as cursor:
                cursor.execute("SHOW SESSION STATUS LIKE 'Ssl_cipher'")
                row = cursor.fetchone()
            cipher = row[1] if row else ""
            verified = bool(db["OPTIONS"].get("ssl"))
            self.stdout.write(f"  Encrypted     : {'yes (' + cipher + ')' if cipher else 'no'}")
            self.stdout.write(
                "  Server checked: "
                + ("yes, certificate verified with DB_SSL_CA" if verified else "no (fine on your own computer; add DB_SSL_CA when you use Aiven)")
            )

        tables = connection.introspection.table_names()
        if "students_student" in tables:
            from students.models import Student
            self.stdout.write(f"  Students table: found, {Student.objects.count()} student(s) stored")
        else:
            self.stdout.write("  Students table: not created yet. Run: python manage.py migrate")

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("  CONNECTED"))
        self.stdout.write("")
