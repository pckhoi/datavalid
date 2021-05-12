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
    - name: `complaint_uid` should be unique per `allegation` x `uid`
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
    - name: no officer with consecutive left date
      where:
        column: kind
        op: equal
        value: officer_left
      group_by: uid
      no_consecutive_date:
        date_from:
          year: year
          month: month
          day: day
```

Then run datavalid command in that folder:

```bash
python -m datavalid
```

You can also specify a data folder that isn't the current working directory:

```bash
python -m datavalid --dir my_data_folder
```
