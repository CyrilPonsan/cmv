#!/bin/bash
alembic merge heads
alembic stamp head
alembic revision --autogenerate
alembic upgrade head