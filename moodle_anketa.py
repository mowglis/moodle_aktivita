#!/usr/bin/env python3
"""
Moodle anketa
- data čerpá přímo z db moodle
- vytváří soubory za jednotlivé volby ankety (csv, xls)
- vytváří soubory za jednotlivé třídy

db Moodle:
- host: 192.168.6.36 (www.gybon.cz)
- db: moodle
- tbl:

mdl_choice - ankety
--- id
--- name 

mdl_choice_options - volby ankety
--- id
--- choiceid - id -> mdl_choice
--- text

mdl_choice_answers - odpovědi ankety
--- id
--- choiceid - id -> mdl_choice
--- optionid - id -> mdl_choice_options
--- userid   - id -> mdl_user

mdl_user
--- id
--- username
--- firstname
--- lastname
"""

import sys
sys.path.insert(1, '/home/rusek/skola/lib')
from gybon import Bakalari, Moodle, Gybon_moodle, Moodle_choice_option

import argparse
from rich import box
from rich.console import Console, Group
from rich.table import Table
from rich.panel import Panel
from rich import print
from rich.align import Align
from rich.live import Live

empty_option = {'id':999, 'text':'===== žádná aktivita nevybrána =====', 'maxanswers':0}

def list_all_choices():
    t = Table(title="Výpis anket z Moodle")
    t.add_column("Id")
    t.add_column("Anketa")
    for choice in mdl.choice():
      t.add_row(str(choice.id), choice.name)
    c.print(t)

def empty_option_answers(answers):
    """ list students without any option """

    baka = Bakalari()
    students_with_answer = [student for option, list_students in answers.items() \
                for student in list_students]
    students_no_answer = [student for trida in baka.tridy for student in baka.trida(trida) \
                          if student not in students_with_answer]
    return empty_option['id'], students_no_answer

def list_choice(_choice, class_sorted=None):
    choice, answers = _choice
    t = Table(title="Výpis ankety: {}".format(choice.name))
    if class_sorted:
        t.add_column("Třída")
        t.add_column("Seznam")
        list_class = set([student.trida for option, list_student in answers.items() \
                          for student in list_student])
        for _class in sorted(list_class):
            peoples = [student.fullname for option, list_student in answers.items() for \
                             student in list_student if student.trida == _class]
            count = str(len(peoples))
            t.add_row(_class+' ('+count+')', ", ".join(peoples))
    else:
        t.add_column("Volba")
        t.add_column("Seznam")
        for option in choice.options:
            peoples = ", ".join([st.fullname for st in answers[option.id]])
            count = '('+str(len(answers[option.id]))+'/'+str(option.maxanswers)+')'
            t.add_row(option.text+'\n'+count, peoples)
    c.print(t)

def get_choice(id):
    choice = list(mdl.choice(id=id))[0]
    answers = mdl.choice_answers(choice)
    if not args.noempty: 
        choice.options += [Moodle_choice_option(empty_option)]
        id_empty_option, students = empty_option_answers(answers)
        answers[id_empty_option] = students
    return choice, answers

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(description="Ankety v Moodle")
    parser.add_argument("-i", "--id", help="Vypiš anketu s id")
    parser.add_argument("-t", "--trida", help="Vypiš podle tříd", action="store_true")
    parser.add_argument("-w", "--write", help="Zapiš do DB", action="store_true")
    parser.add_argument("-n", "--noempty", help="Nevypisovat nepřihlášené", action="store_true")
 
    args = parser.parse_args()

    mdl = Moodle()
    c = Console()
    if args.id:
        choice, answers = get_choice(id=args.id)
        list_choice((choice, answers), args.trida)
    
        if args.write:
            answers_items = [{'choiceid':choice.id,
                              'optionid':option,
                              'login':student.login,
                              'firstname':student.jmeno,
                              'lastname':student.prijmeni,
                              'class':student.trida} \
                            for option, list_students in answers.items() for student in list_students]
            mdl_gybon = Gybon_moodle()
            mdl_gybon.delete_all_tables()
            mdl_gybon.insert_choice(choice, answers_items, debug=False)
            c.print("Database updated....")

    else:   
        list_all_choices()
