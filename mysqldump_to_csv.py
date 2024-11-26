#!/usr/bin/env python
import fileinput
import csv
import sys
import re
from signal import signal, SIGPIPE, SIG_DFL

# Prevent prematurely closed pipes from raising an exception in Python
signal(SIGPIPE, SIG_DFL)

# Allow large content in the dump
csv.field_size_limit(sys.maxsize)

# List of required columns and their positions in the SQL data
REQUIRED_FIELDS = {
    "LOGIN": 2,
    "NAME": 6,
    "LAST_NAME": 7,
    "EMAIL": 8,
    "PERSONAL_BIRTHDATE": 16,
    "TIMESTAMP_X": 1,
    "PERSONAL_PHONE": 18,
    "PERSONAL_MOBILE": 20,
    "PERSONAL_MAILBOX": 23,
    "PERSONAL_CITY": 24,
    "PERSONAL_STATE": 25,
    "WORK_CITY": 37,
    "PASSWORD": 3,
    "CHECKWORD": 4,
}

LINES_PER_FILE = 10000  # Maximum lines per CSV file


def is_insert(line):
    """Checks if the line starts a SQL INSERT INTO statement."""
    return line.strip().startswith('INSERT INTO')


def get_values(statement):
    """Extracts the values portion of an INSERT INTO statement."""
    _, _, values = statement.partition(' VALUES ')
    return values.strip().rstrip(';')


def parse_values(values, writer, line_counter):
    """Parses the values and writes them to the CSV writer."""
    rows = re.split(r"\),\s*\(", values.strip("()"))

    for row in rows:
        # Extract values (handle quoted strings, NULLs, and numbers)
        columns = re.findall(r"(?:'([^']*)'|NULL|\d+)", row)

        # Map values to the required fields
        result_row = [
            columns[index] if index < len(columns) and columns[index] != "NULL" else ""
            for field, index in REQUIRED_FIELDS.items()
        ]

        writer.writerow(result_row)
        line_counter[0] += 1

        # Check if we need to switch to a new file
        if line_counter[0] >= LINES_PER_FILE:
            line_counter[0] = 0
            return True  # Signal to switch files
    return False


def process_insert(statement, writer, line_counter):
    """Processes a single INSERT INTO statement."""
    try:
        values = get_values(statement)
        return parse_values(values, writer, line_counter)
    except Exception as e:
        print(f"Error processing statement: {e}", file=sys.stderr)
        return False


def main():
    """Main function to process SQL dump and split into multiple CSV files."""
    buffer = ""
    file_count = 0
    line_counter = [0]  # Track lines written to current file

    try:
        current_file = open(f"apteka_{file_count}.csv", "w", newline="", encoding="utf-8")
        writer = csv.writer(current_file, quoting=csv.QUOTE_MINIMAL)
        writer.writerow(REQUIRED_FIELDS.keys())  # Write header once per file

        for line in fileinput.input():
            line = line.strip()
            if is_insert(line):
                if buffer:
                    if process_insert(buffer, writer, line_counter):
                        current_file.close()
                        file_count += 1
                        current_file = open(f"apteka_{file_count}.csv", "w", newline="", encoding="utf-8")
                        writer = csv.writer(current_file, quoting=csv.QUOTE_MINIMAL)
                        writer.writerow(REQUIRED_FIELDS.keys())  # Write header for new file
                    buffer = ""
                buffer = line
            elif buffer:
                buffer += " " + line
                if line.endswith(";"):
                    if process_insert(buffer, writer, line_counter):
                        current_file.close()
                        file_count += 1
                        current_file = open(f"apteka_{file_count}.csv", "w", newline="", encoding="utf-8")
                        writer = csv.writer(current_file, quoting=csv.QUOTE_MINIMAL)
                        writer.writerow(REQUIRED_FIELDS.keys())  # Write header for new file
                    buffer = ""
        if buffer:
            process_insert(buffer, writer, line_counter)

        current_file.close()
    except KeyboardInterrupt:
        sys.exit(0)
    except Exception as e:
        print(f"Unhandled exception: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
