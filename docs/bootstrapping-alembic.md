# Bootstrapping Alembic

Alembic is always a pain in the ass to get working for a new application.
Usually my situation is that I spend a couple days working on a new
application, only later to think about maintaining my database in some
production-esque environment. How do I create my original migration file? This
document is the quick and dirty way to bootstrap your alembic configuration.

---

First, copy over and read through the alembic directory within this code base.
It has wired up the `env.py` file properly and applied the changes suggested
from the linked resources below.

Second, you want to get rid of invocations of `db.create_all`. See notes in
the code. TL;DR: You're replacing database table create/upgrade/downgrade
operations with alembic. Calling `db.create_all` causes thrashing that is hard
to detect and fix.

Third, you want to delete your database to start with a clean start. Delete it,
and run `alembic stamp head` to indicate this is the current head state of your
database.

Fourth, you want to create your "initial migration" from the head state that
you just stamped (i.e., an empty database) to the new state (i.e., the fully
created/populated database). To do that run `alembic revision --autogenerate -m
"Initial database setup."`. You should see a meaningful migration file created.

You're done. At this point, read through the following resources and become
diligent about creating your migration files when you update your database
models.

# Resources

These are some useful Alembic resources for going deeper:

- [Alembic Tutorial](https://alembic.sqlalchemy.org/en/latest/tutorial.html)
- [Autogenerating Migrations](https://alembic.sqlalchemy.org/en/latest/autogenerate.html)
