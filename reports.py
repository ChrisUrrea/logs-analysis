#!/usr/bin/env python3.6
import psycopg2
import argparse
import os


top_authors_query = """select articles.title, count(*) as n_visits from
                        articles, log where
                        log.path = concat('/article/', articles.slug)
                        group by articles.title
                        order by n_visits desc limit 3;"""

top_articles_query = """select authors.name, count(*) as n_visits
                        from articles, authors, log
                        where articles.author = authors.id
                        and log.path = concat('/article/', articles.slug)
                        group by authors.name
                        order by n_visits desc;"""

over1_errors_query = """select * from (
                        select to_char(err_visits.day,'DD-MON-YYYY'),
                        round(100.0*err_visits.errs/all_visits.count,2)
                        as err_percent from ((select date(time) as day,
                        count(*) as count from log group by day)
                        as all_visits inner join (select date(time) as day,
                        count(*) as errs from log where status
                        like '%404%' group by day) as err_visits
                        on all_visits.day = err_visits.day))
                        as all_errs where err_percent > 1.0;"""


def connect_cursor(dbname):
    "Connects to database with `db_name` and returns psql cursor."
    try:
        database = psycopg2.connect(f"dbname={dbname}")
        cursor = database.cursor()
    except Exception as e:
        print(f"Failed to connect to PSQL database named {dbname}. ")
        print(e)
        exit()
    else:
        print(f"Successfully connected to PSQL database named {dbname}.")
        return cursor, database


def exec_query(cursor, query):
    "Execute sql `query` with `cursor`"
    cursor.execute(query)
    # Fetch results
    results = cursor.fetchall()
    return results


def write_txt(file_name, query_output, query_descriptor, end_tag):
    "Write `query_results` headed by `query_descriptor` in `file_name` txt file"

    with open(file_name, "a+") as file:
        file.write(query_descriptor)
        file.write('\n')
        for row in query_output:
            file.write('\t' + row[0] + ' - ' + str(row[1]) + ' ' + end_tag)
            file.write('\n')
        file.write('\n')
    file.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-db', '--db_name',
                        help='name of database to query', required=True)
    parser.add_argument('-o', '--output_path',
                        help='output path', required=False)

    args = parser.parse_args()
    kwargs = vars(args)

    if not kwargs.get('output_path', None):
        kwargs['output_path'] = f'{os.path.basename(__file__).split(".")[0]}.txt'

    cursor, database = connect_cursor(kwargs['db_name'])

    top_authors_results = exec_query(cursor, top_authors_query)
    write_txt(kwargs['output_path'], top_authors_results,
              "Top Authors:", "views")
    top_articles_results = exec_query(cursor, top_articles_query)
    write_txt(kwargs['output_path'], top_articles_results,
              "Top 3 Articles:", "views")
    over1_errors_results = exec_query(cursor, over1_errors_query)
    write_txt(kwargs['output_path'], over1_errors_results,
              "Dates with more than 1% error views:", "% error views")
    database.close()
