#!/bin/sh

sqlite3 /tmp/strichliste2.db "DELETE from transactions; DELETE from users;"
