# MySQL dump to CSV
## Introduction
This Python script converts MySQL dump files into CSV format. It is optimized to handle extraordinarily large dumps, such as those from Wikipedia.

MySQL dumps contain a series of INSERT statements and can be difficult to import or manipulate, often requiring significant hardware upgrades. This script provides an easy way to convert these dump files into the universal CSV format.

The script takes advantage of the structural similarities between MySQL INSERT statements and CSV files. It uses Python's CSV parser to convert the MySQL syntax into CSV, enabling the data to be read and used more easily.

## Usage
Just run `python mysqldump_to_csv.py` followed by the filename of an SQL file. You can specify multiple SQL files, and they will all be concatenated into one CSV file. This script can also take in SQL files from standard input, which can be useful for turning a gzipped MySQL dump into a CSV file without uncompressing the MySQL dump.

## License
The code is strung together from other public repos, I'm pretty sure the license is standard MIT License.


## For run

python3 -m venv myenv
source myenv/bin/activate
myenv\Scripts\activate
pip install openpyxl
python mysqldump_to_csv.py b_user.sql
deactivate
