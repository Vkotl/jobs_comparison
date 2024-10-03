from helpers import get_date, compare_positions


def main():
    old_date = get_date(is_old=True)
    new_date = get_date(is_old=False)
    compare_positions(old_date, new_date, 'SoFi')
    compare_positions(old_date, new_date, 'Galileo')


if __name__ == '__main__':
    main()
