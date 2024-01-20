#### This step stores the data insights created by sentinel.
import funcs as f
import glob
import pyodbc
from datetime import datetime

filenames = glob.glob("pickles/diced/*")

def create_cursor():
    conn = pyodbc.connect('DRIVER=%s;SERVER=%s;Trusted_Connection=yes;' % ('{ODBC Driver 17 for SQL Server}', 'DESKTOP-SD87CAL\SQLEXPRESS'), database='gay')
    return conn, conn.cursor()

def upload_data(json):
    created = datetime.now()
    created = created.strftime('%Y-%m-%d %H:%M:%S')

    query = "SET NOCOUNT ON;\nDECLARE @PK_GAME TABLE (ID INT)"
    query += "\nINSERT INTO games (world, created, flip) OUTPUT Inserted.id into @PK_GAME VALUES ('%s', '%s', %s)" % (json.world, created, json.flip)

    for i, team in enumerate(json.teams):
        for j, player in enumerate(team):
            query += "\nDECLARE @PK_PLAYER_%s_%s TABLE (ID INT)" % (i, j)
            query += "\nINSERT INTO teams (name, hero, team, slot, game) OUTPUT Inserted.id into @PK_PLAYER_%s_%s VALUES ('%s', '%s', %s, %s, (SELECT ID FROM @PK_GAME))" % (i, j, player.name, player.hero, i, j)


    round_index = 0
    for round in json.rounds:
        round_index += 1
        query += "\nDECLARE @PK_ROUND_%s TABLE (ID INT)" % round_index
        query += "\nINSERT INTO rounds (winner, num, game) OUTPUT Inserted.id into @PK_ROUND_%s VALUES (%s, %s, (SELECT ID FROM @PK_GAME))" % (round_index, round.winner, round.round_num)

        for event in round.events:
            #TODO - Handle suicides.
            if type(event).__name__ == 'Suicide': continue

            e_weapon = event.weapon if hasattr(event, 'weapon') else 'NULL'
            e_headshot = event.headshot if hasattr(event, 'headshot') else 'NULL'
            e_wallbang = event.wallbang if hasattr(event, 'wallbang') else 'NULL'

            if hasattr(event, 'right'):
                query += "\nINSERT INTO events (left_player, weapon, right_player, headshot, wallbang, time, type, round) VALUES " \
                         "((SELECT ID FROM @PK_PLAYER_%s_%s), '%s', (SELECT ID FROM @PK_PLAYER_%s_%s), %s, %s, %s, '%s', (SELECT ID FROM @PK_ROUND_%s))" \
                         % (event.left.team, event.left.slot, e_weapon, event.right.team, event.right.slot, e_headshot, e_wallbang, event.time, type(event).__name__, round_index)
            else:
                query += "\nINSERT INTO events (left_player, weapon, right_player, headshot, wallbang, time, type, round) VALUES " \
                         "((SELECT ID FROM @PK_PLAYER_%s_%s), '%s', %s, %s, %s, %s, '%s', (SELECT ID FROM @PK_ROUND_%s))" \
                         % (event.left.team, event.left.slot, e_weapon, 'NULL', e_headshot, e_wallbang, event.time, type(event).__name__, round_index)

    conn, cursor = create_cursor()
    cursor.execute(query)
    cursor.execute("exec agg_fights")
    conn.commit()
    conn.close()

    print("Finished uploading rounds.")

for pickle in filenames:
    json = f.load_object(pickle)

    for team in json.teams:
        s = input("Enter corrected names for video (comma delimited) - " + pickle + "\n")
        s = s.split(',')
        for x in range(0, 5):
            team[x].name = s[x]

    upload_data(json)




