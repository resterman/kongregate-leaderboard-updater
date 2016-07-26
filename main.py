import csv
import sys
import time
from datetime import date

from KongregateData import KongregateData
from bisect import bisect_left
from operator import itemgetter


def download_data():
    first_user = int(input('Enter first user id: '))
    last_user = int(input('Enter last user id: '))
    threshold = int(input('Enter point threshold: '))
    connections = int(input('Enter max concurrent connections: '))
    filename = input('Enter save file path (blank for default): ')
    default_filename = '{}_to_{}_with_{}_points_{}.csv'\
        .format(first_user, last_user, threshold, date.today().strftime('%Y-%m-%d'))

    save_file = open(default_filename if not filename else filename, 'w')

    def callback(user):
        """
        Write user in .csv format
        """
        user_vars = user['user_vars']

        if user_vars['points'] > threshold:
            user_row = '{},{},{},{}\n'.format(user['user_id'], user_vars['username'], user_vars['level'],
                                              user_vars['points'])
            save_file.write(user_row)

    k = KongregateData(first_user, last_user)
    t = time.time()
    k.run(connections, callback)
    print('Time elapsed: {}'.format(time.time() - t))


def get_position_changes():
    old_file_path = input('Enter old file path: ')
    new_file_path = input('Enter new file path: ')
    rank_file_path = input('Enter rank file path: ')

    with open(old_file_path, 'r') as old_file:
        with open(new_file_path, 'r') as new_file:
            with open(rank_file_path, 'w') as rank_file:
                get_position_changes_with_files(old_file, new_file, rank_file)


def get_position_changes_with_files(old_file, new_file, rank_file):
    csv.register_dialect('kong-leaderboards', delimiter=',', quoting=csv.QUOTE_NONE)
    old_file_reader = csv.reader(old_file, dialect='kong-leaderboards')
    new_file_reader = csv.reader(new_file, dialect='kong-leaderboards')

    new_users = []
    for line in new_file_reader:
        try:
            user_id = int(line[0])
            points = int(line[3])
            new_users.append((user_id, points))
        except csv.Error as e:
            sys.exit('File %s, line %d: $s'.format(new_file.name, new_file_reader.line_num, e))

    new_users = [x[0] for x in sorted(new_users, key=itemgetter(1, 0))]

    old_users = []
    for line in old_file_reader:
        try:
            user_id = int(line[0])
            points = int(line[3])
            old_users.append((user_id, points))
        except csv.Error as e:
            sys.exit('File %s, line %d: $s'.format(old_file.name, old_file_reader.line_num, e))

    old_users = [x[0] for x in sorted(old_users, key=itemgetter(1, 0))]

    print(new_users)
    print(old_users)

    position_change_file = csv.writer(rank_file)
    total_users = len(new_users)
    for new_pos in range(0, len(new_users)):
        user_id = new_users[new_pos]
        old_pos = bisect_left(old_users, user_id)

        if old_pos != len(old_users) and old_users[old_pos] == user_id:
            position_change_file.writerow([user_id, total_users - (new_pos - old_pos) + 1])
        position_change_file.writerow([user_id, 'NEW'])


def main():
    option = 0
    while True:
        try:
            option = int(input('Do you want to [1] download user data or [2] calculate position changes? '))
        except ValueError:
            print('Invalid value')
        else:
            if option not in [1, 2]:
                print('Invalid option')
            else:
                break

    if option == 1:
        download_data()
    elif option == 2:
        get_position_changes()
    else:
        print('Invalid value')


if __name__ == "__main__":
    main()
