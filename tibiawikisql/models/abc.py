import abc

from tibiawikisql.parsers.utils import parse_attributes


class Parser(abc.ABCMeta):
    map = None
    pattern = None
    child_tables = {}
    child_rows = []

    @classmethod
    def from_article(mcs, article, extra_data=None):
        if mcs.map is None:
            raise NotImplementedError('Method must be called from inherited instance')

        if article is None or (mcs.pattern and not mcs.pattern.search(article.content)):
            return None
        row = {"id": article.article_id, "last_edit": article.unix_timestamp, "title": article.title}
        attributes = parse_attributes(article.content)
        for attribute, value in attributes.items():
            if attribute not in mcs.map:
                continue
            column, func = mcs.map[attribute]
            row[column] = func(value)
        mcs.extra_parsing(row, attributes)
        if isinstance(extra_data, list):
            mcs.parse_extra_data(article.article_id, attributes, c, extra_data)
        return row

    @classmethod
    def extra_parsing(mcs, row, attributes):
        pass

    @classmethod
    def parse_extra_data(mcs, article_id, attributes, c, extra_data):
        return []

    @classmethod
    def insert_extra_data(mcs, data, c):
        results = {}
        for table, columns in mcs.child_tables.items():
            rows = []
            for row in data:
                if row[0] == table:
                    if len(columns) != len(row) - 1:
                        raise ValueError(f"Number of columns provided for table {table} doesn't match.")
                    rows.append(row[1:])
            if rows:
                query = f"INSERT INTO {table}({','.join(columns)}) VALUES({', '.join('?' for _ in columns)})"
                c.executemany(query, rows)
                results[table] = len(rows)
        return results

