tables = {
    'urls': 'CREATE TABLE IF NOT EXISTS urls ('
            'id SERIAL PRIMARY KEY, '
            'url TEXT UNIQUE'
            ');',
    'timeouts': 'CREATE TABLE IF NOT EXISTS timeouts ('
                'id SERIAL, '
                'timeout INT'
                ');',
    'regexps': 'CREATE TABLE IF NOT EXISTS regexps ('
               'id SERIAL, '
               'regexp_text TEXT, '
               'url_id INT, '
               'CONSTRAINT fk_urls FOREIGN KEY(url_id) REFERENCES urls(id)'
               ');',
    'check_data': 'CREATE TABLE IF NOT EXISTS check_data ('
                  'id SERIAL, '
                  'error_code INT, '
                  'latency FLOAT, '
                  'regexp BOOL, '
                  'url_id INT, '
                  'CONSTRAINT fk_urls FOREIGN KEY(url_id) REFERENCES urls(id)'
                  ');'
}

default_timeout = 60

kafka_topic = 'website_check'
