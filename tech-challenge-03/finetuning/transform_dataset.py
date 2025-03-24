import json

from pysqlx_engine import PySQLXEngineSync

from .const import CLEAN_FILE

SELECT_SQL = """--sql
with cto as (
    select
        title,
        count(title) as total
    from product
    where length(content) > 10 and length(title) > 0 and trim(content) != ''
    group by title
    having count(title) >= 10
)
select distinct title, content as description from product as p
where p.title in (select cto.title from cto) and length(content) > 10 and length(title) > 0 and trim(content) != ''
order by title;
"""

conn = PySQLXEngineSync(uri="postgresql://test:test@localhost:5432/test")
conn.connect()

result = conn.query_as_dict(SELECT_SQL)

with open(CLEAN_FILE, "w") as f:
    for row in result:
        f.write(f"{json.dumps(row)}\n")

conn.close()
