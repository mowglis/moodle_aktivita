#!/usr/bin/env python3
"""
vstup: csv z Moodle a aktivity 'anketa' ze STDIN
output: csv rozdělení studentů do tříd
"""
import sys
import csv
sys.path.insert(1, '/home/rusek/skola/lib')
from gybon import Bakalari, asci

login = lambda pr, jm: asci(jm[0:3].lower()+pr[0:4].lower())
login_mail = lambda mail: mail.split('@')[0]
login_new = lambda pr, jm: asci(jm.lower()+'.'+pr.lower()) 

csvfile = sys.stdin
csv_reader = csv.reader(csvfile, delimiter=',', quotechar='"')
baka = Bakalari()

csv_out = open('moodle_aktivita.csv', 'w', newline='')
csv_writer = csv.writer(csv_out, delimiter=',',
                                quotechar='"', quoting=csv.QUOTE_MINIMAL)
csv_writer.writerow(['Příjmení', 'Jméno', 'Mail', 'Třída', 'Aktivita'])
student_aktivita = {}

for pr, jm, mail, skupina, aktivita in csv_reader:
    student = baka.student(login=login_mail(mail))
    if student == None:
        student = baka.student(login=login_new(pr, jm))
        if student == None:
            student = baka.student(login=login(pr, jm))
            if student == None:
                #print(pr, jm, "*** Nenalezeno!")
                continue
    #print(student)
    if aktivita != "Dosud nezodpovězeno":
        try:
            student_aktivita[student.trida] += [student]
            csv_writer.writerow([student.prijmeni, student.jmeno, mail, student.trida, aktivita])
        except:
            student_aktivita[student.trida] = [student]

csv_out.close()

csv_out = open('moodle_aktivita_neodpovedeli.csv', 'w', newline='')
csv_writer = csv.writer(csv_out, delimiter=',',
                                quotechar='"', quoting=csv.QUOTE_MINIMAL)
csv_writer.writerow(['Třída', 'Příjmení', 'Jméno', 'Mail'])

def student_kontrola(s, studenti):
    for st in studenti:
        if st.prijmeni == s.prijmeni and st.jmeno == s.jmeno:
            return False
    return True            

def csv_write_row(s):
    csv_writer.writerow([s.trida, s.prijmeni, s.jmeno, s.email])

for trida, studenti in student_aktivita.items():
    [csv_write_row(s) for s in baka.trida(trida) if student_kontrola(s, studenti)]
