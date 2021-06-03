# Datavalid

This library allow you to declare validation tasks to check for CSV files. This ensure data correctness for ETL pipeline that update frequently.

## Installation

```bash
pip install datavalid
```

## Usage

Create a `datavalid.yml` file in your data folder:

```yaml
files:
  fuse/complaint.csv:
    schema:
      uid:
        description: >
          accused officer's unique identifier. This references the `uid` column in personnel.csv
      tracking_number:
        description: >
          complaint tracking number from the agency the data originate from
      complaint_uid:
        description: >
          complaint unique identifier
        unique: true
        no_na: true
    validation_tasks:
      - name: "`complaint_uid`, `allegation` and `uid` should be unique together"
        unique:
          - complaint_uid
          - uid
          - allegation
      - name: if `allegation_finding` is "sustained" then `disposition` should also be "sustained"
        empty:
          and:
            - column: allegation_finding
              op: equal
              value: sustained
            - column: disposition
              op: not_equal
              value: sustained
  fuse/event.csv:
    schema:
      event_uid:
        description: >
          unique identifier for each event
        unique: true
        no_na: true
      kind:
        options:
          - officer_level_1_cert
          - officer_pc_12_qualification
          - officer_rank
    validation_tasks:
      - name: no officer with more than 1 left date in a calendar month
        where:
          column: kind
          op: equal
          value: officer_left
        group_by: uid
        no_more_than_once_per_30_days:
          date_from:
            year_column: year
            month_column: month
            day_column: day
save_bad_rows_to: invalid_rows.csv
```

Then run datavalid command in that folder:

```bash
python -m datavalid
```

You can also specify a data folder that isn't the current working directory:

```bash
python -m datavalid --dir my_data_folder
```

## Config specification

A config file is a file named `datavalid.yml` and it must be placed in your root data folder. Your root data folder is the folder that contain all of your data files. Config file contains [config object](#config-object) in YAML format.

### Config object

- **files**: required, a mapping between file names and file configurations. Each file path is evaluated relative to root data folder and each file must be in CSV format. Refer to [file object](#file-object) to learn more about file configuration.
- **save_bad_rows_to**: optional, which file to save offending rows to. If not defined then bad rows will just be output to terminal.

### File object

- **schema**: optional, description of each column in this file. This field accepts a [column schema object](#column-schema-object).
- **validation_tasks**: optional, additional validation tasks to perform on this file. Refer to [task object](#task-object) to learn more.

### Column schema object

- **description**: optional, textual description of this column.
- **unique**: optional, if set to true then this column can not contain duplicates.
- **no_na**: optional, if set to true then this column cannot contain empty values.
- **integer**: optional, if set to true then this column can only contain integers.
- **float**: optional, if set to true then this column can only contain floats.
- **options**: optional, list of valid values for this column.
- **range**: optional, list of 2 numbers. Lower bound and higher bound of what values are considered valid. Setting this imply `float: true`.
- **title_case**: optional, if set to true then all words in this column must begin with an upper case letter.

### Task object

Common fields:

- **name**: required, name of validation task.
- **where**: optional, how to filter the data. This field accepts a [condition object](#condition-object).
- **group_by**: optional, how to divide the data before validation. This could be a single column name or a list of column names to group the data with.
- **warn_only**: optional, if set to true then failing this validation only generate a warning rather than failing the whole run.

Checker fields (define exactly one of these fields):

- **unique**: optional, column name or list of column names to ensure uniqueness.
- **empty**: optional, accepts a [condition object](#condition-object) and ensure that no row fulfill this condition.
- **no_more_than_once_per_30_days**: optional, ensure that no 2 rows occur closer than 30 days apart. Accepts the following fields:
  - **date_from**: required, how to parse date from the given data. Accepts a [date parser](#date-parser) object.
- **no_consecutive_date**: optional, ensure that no row occur on consecutive days. Accepts the following fields:
  - **date_from**: required, how to parse date from the given data. Accepts a [date parser](#date-parser) object.

### Condition object

There are 3 ways to define a condition. The first way is to provide `column`, `op` and `value`:

- **column**: optional, column name to compare
- **op**: optional, compare operation to use. Possible value are:
  - _equal_
  - _not_equal_
  - _greater_than_
  - _less_than_
  - _greater_equal_
  - _less_equal_
- **value**: optional, the value to compare with.

The second way is to provide `and` field:

- **and**: optional, list of conditions to combine into one condition. The condition is fulfilled when all of sub-conditions are fulfilled. Each sub-condition can have any field which is valid for a [condition object](#condition-object).

Finally the last way is to provide `or` field:

- **or**: optional, same as `and` except that the sub-conditions are or-ed together which mean the condition is fulfilled if any of the sub-conditions is fulfilled.

### Date parser

Combines multiple columns to create dates.

- **year_column**: required, year column name.
- **month_column**: required, month column name.
- **day_column**: required, day column name.
