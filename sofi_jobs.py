
def clean_jobs(jobs: list) -> dict:
    res = {}
    openings_len = len('OPENINGS')
    department = ''
    while len(jobs) > 0:
        line = jobs.pop(0)
        lower_line = line.lower()
        if lower_line.endswith('openings') or lower_line.endswith('opening'):
            department = line[:line.rindex(' ', 0, (1+openings_len)*(-1))]
            res[department] = []
        elif line != 'Apply Now':
            res[department].append(line)
            if jobs.pop(0) == 'Apply Now':
                jobs.pop(0)
    return res


def get_jobs_from_file(file_name) -> tuple[list, str]:
    with open(file_name) as f:
        jobs = f.read().splitlines()
    return jobs, jobs.pop(0)


def crosscheck_jobs(new_jobs, old_jobs) -> dict:
    res = {'new': {}, 'removed': {}}
    new_pos = res['new']
    removed_pos = res['removed']
    _handle_comparison(new_jobs, old_jobs, new_pos)
    _handle_comparison(old_jobs, new_jobs, removed_pos)
    return res


def _handle_comparison(from_lst, to_lst, diff_lst):
    for department in from_lst:
        if department not in to_lst:
            diff_lst[department] = from_lst[department]
        else:
            diff_lst[department] = []
            for pos in from_lst[department]:
                if pos not in to_lst[department]:
                    diff_lst[department].append(pos)
            if len(diff_lst[department]) == 0:
                del diff_lst[department]


def print_difference(orig_dict):
    if len(orig_dict) != 0:
        for department in orig_dict:
            print(f'  {department}:')
            for pos in orig_dict[department]:
                print(f'    {pos}')
    else:
        print('There are no changes.')


def main():
    new_path = 'new.txt'
    prev_path = 'prev.txt'
    old_jobs, old_date = get_jobs_from_file(prev_path)
    new_jobs, new_date = get_jobs_from_file(new_path)
    old_jobs = clean_jobs(old_jobs)
    new_jobs = clean_jobs(new_jobs)
    difference = crosscheck_jobs(new_jobs, old_jobs)
    print(f'Change between {old_date} and {new_date}')
    print('New positions:')
    print_difference(difference['new'])
    print('Removed positions:')
    print_difference(difference['removed'])


if __name__ == '__main__':
    main()
