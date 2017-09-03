#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import urllib2
import re
import codecs
from os import listdir
from os.path import isfile, join
from optparse import OptionParser

import consts as CONST
import parser as pr
import dbmodels as db

optparser = OptionParser()
optparser.add_option("-t", "--type",
                     dest="type",
                     help="set schedule type (lections/exams/zachet)",
                     default='lections')
optparser.add_option("-d", "--download",
                     dest="download",
                     help="load docs or not",
                     default=False)
(user_options, args) = optparser.parse_args()


if user_options.download:
    print "Try to get html code from mirea schedule page."
    try:
        response = urllib2.urlopen(
            'https://www.mirea.ru/education/schedule-main/schedule/')
        html = response.read()
        print 'HTML got succesfull.'
        response.close()
    except Exception as e:
        print 'HTML got with errors!'
        logger.log(CONST.LOG_ERROR, e)

    print 'Try to load excel documents.'
    counter = 0
    try:
        doc_urls = re.findall('[^"]*\.xlsx?', html)
        print 'Document amount = ' + str(len(doc_urls))
        for i, url in enumerate(doc_urls):
            try:
                ftype = re.search('\.[a-z]*\Z', url).group()
                with open(CONST.SCHEDULE_DIR + str(i) + ftype,
                          'wb') as f:
                    f.write(urllib2.urlopen(url).read())
                    f.close()
                counter += 1
            except Exception as e:
                print '--- Exception\n' + url + '\n' + str(
                    e) + '\n---\n'
        print 'Document loaded succesfull. Count = ' + str(counter)
    except Exception as e:
        print 'Documents loaded with errors. Last document No ' + str(
            counter)
        logger.log(CONST.LOG_ERROR, e)

documents = [f for f in listdir(CONST.SCHEDULE_DIR) if
             isfile(join(CONST.SCHEDULE_DIR, f))]

print 'Load schedule to database'
parser = pr.Parser()
print u'Документов:' + str(len(documents))
count = 0
for doc in documents:
    count += 1
    print u'Загрузка документа №' + str(count) + '\r'
    #try:
    schdl_type, schedule = parser.getSchedule(
        CONST.SCHEDULE_DIR + doc)
    #except Exception as e:
    #    print e
    #    continue

    if schdl_type == user_options.type == 'lections':
        for group, events in schedule.items():
            try:
                group_obj, flag = db.Groups.get_or_create(gcode=group)
                query = db.Schedule.delete().where(db.Schedule.group == group_obj.id)
                query.execute()
            except Exception as e:
                print e
                continue

            for event in events:
                try:
                    nname = event['name']
                    for par in event['params']:
                        nname += " (" + par + ")"
                    nteacher = event['teacher'] if event[
                        'teacher'] else ''
                    nroom = event['room'] if event['room'] else ''
                    schdl_obj = db.Schedule(
                        group=group_obj,
                        week=event['week'],
                        day=event['day'],
                        numb=event['numb'],
                        name=nname,
                        room=nroom,
                        teacher=nteacher,
                    )
                    schdl_obj.save()
                except Exception as e:
                    print e
                    continue
