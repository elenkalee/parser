from subprocess import run, PIPE
from datetime import datetime
import sys

today = datetime.today()
file_name = today.strftime("%d-%m-%Y-%H:%M")
stdout = sys.stdout
sys.stdout = open(f'{file_name}-scan.txt', 'w')

res = run(['ps', 'aux'], stdout=PIPE)
procs = res.stdout.decode().split('\n')
titles = procs[0].split()

max_cpu = 0
max_cpu_proc = ''
max_mem = 0
max_mem_proc = ''

users = set()
all_proc_count = 0
user_proc = {}
mem = 0
cpu = 0
for p in procs[1:]:

    if not p == '':
        chunks = p.split(maxsplit=len(titles) - 1)
        procs_cpu = float(chunks[titles.index('%CPU')])
        procs_mem = float(chunks[titles.index('%MEM')])
        users.add(chunks[titles.index('USER')])
        mem += float(chunks[titles.index('%MEM')])
        cpu += float(chunks[titles.index('%CPU')])
        all_proc_count += 1

        if procs_cpu >= max_cpu or procs_mem >= max_mem:
            max_cpu = procs_cpu
            max_cpu_proc = chunks[titles.index('COMMAND')]
            max_mem = procs_mem
            max_mem_proc = chunks[titles.index('COMMAND')]

user_proc = {u: 0 for u in users}

for p in procs[1:]:
    if not p == '':
        chunks = p.split(maxsplit=len(titles) - 1)
        if chunks[titles.index('USER')] in user_proc:
            user_proc[chunks[titles.index('USER')]] += 1

sys.stdout.write(f'Отчет о состоянии системы:''\n'
                 f'Пользователи системы: {", ".join(sorted(users))}''\n'
                 f'Процессов запущено: {all_proc_count}''\n'
                 f'Пользовательских процессов:''\n')

for key, value in sorted(user_proc.items()): print(key, ':', value)

sys.stdout.write(f'Всего памяти используется: {round(mem, 1)}%''\n'
                 f'Всего CPU используется: {round(cpu, 1)}%''\n'
                 f'Больше всего CPU использует: {max_cpu}% {max_cpu_proc[:20]}''\n'
                 f'Больше всего памяти использует: {max_mem}% {max_mem_proc[:20]}')

sys.stdout.close()
sys.stdout = stdout
