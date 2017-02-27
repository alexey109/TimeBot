#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import datetime as dt
import time
import string
import sys
import re
import MySQLdb
from operator import itemgetter

import consts as CONST
import logger as lg
import dbmodels as db


# The main idea of this bot to help everyone with schedule.
# Bot intergated to socialnet and like a friend can tell you what lection you will have.
# Normal documentation will be in future.
attachment	= ''
logger 		= lg.Logger()

def getLessonNumb(dt_time):
	return {
							dt_time < dt.time(9,0,0)  :	0,
		dt.time(9,0,0) 	 <= dt_time < dt.time(10,30,0): 1,
		dt.time(10,30,0) <= dt_time < dt.time(12,10,0): 2,
		dt.time(12,10,0) <= dt_time < dt.time(14,30,0): 3,
		dt.time(14,30,0) <= dt_time < dt.time(16,10,0): 4,
		dt.time(16,10,0) <= dt_time < dt.time(17,50,0): 5,
		dt.time(18,00,0) <= dt_time < dt.time(19,30,0): 6,
		dt.time(19,30,0) <= dt_time < dt.time(20,00,0): 7,
		dt.time(20,00,0) <= dt_time < dt.time(21,40,0): 8,
		dt.time(21,40,0) <= dt_time					  :	9
	}[True]

def isWeeksEqual(native_week, base_week):
	base_week = base_week - dt.date(2017, 2, 6).isocalendar()[1] + 1

	if native_week == '':
		result = True
	elif 'I' in native_week:
		result = (base_week % 2 == 0) == (native_week.strip() == 'II')
	elif '-' in native_week:
		period = re.split('-', native_week)
		result = (base_week >= int(period[0])) and (base_week <= int(period[1]))
	else:
		result = str(base_week) in re.split(r'[\s,]', native_week)
	return result

def findFloor(room_native):
	room_native = room_native.lower().replace('-', '')
	campus 	= room_native[:1]
	room 	= room_native[1:]

	floor_found = {}
	if campus == u'а':
		for floor in CONST.MAP_DATA:
			if floor['nam_ru'][:1] == campus:
				for map_room in floor['rooms'].split(','):
					if room == map_room.replace(' ', ''):
						floor_found = floor
	else:
		for floor in CONST.MAP_DATA:
			if floor['nam_ru'] == (campus + room[:1]):
				floor_found = floor
	
	return floor_found

def getSchedule(params):
	schedule_base = db.Schedule.filter(group = params['group']['id'])
	try:
		db_user = db.Users.get(
			db.Users.vk_id == params['vk_id'], 
			db.Users.vk_chat == bool(params['is_chat'])
		)
		schedule_user = db.UsersSchedule.filter(user = db_user.id)
	except:
		schedule_user = []
	schedule = []
	for event_base in schedule_base:
		no_major = True
		for event_user in schedule_user:
			if event_user.week == event_base.week \
			 and event_user.day == event_base.day \
			 and event_user.numb == event_base.numb:
			 	no_major = False
			 	break
		if not no_major:
			continue
		event = {
			'name'		: event_base.name,
			'week'		: event_base.week,
			'day'		: event_base.day,
			'numb'		: event_base.numb,
			'teacher'	: event_base.teacher,
			'room'		: event_base.room,
		}
		schedule.append(event)
	for event_user in schedule_user:
		if event_user.hide:
			continue
		event = {
			'name'		: event_user.name,
			'week'		: event_base.week,
			'day'		: event_user.day,
			'numb'		: event_user.numb,
			'teacher'	: event_user.teacher,
			'room'		: event_user.room,
		}
		schedule.append(event)
	schedule = sorted(schedule, key=itemgetter('day', 'numb'))
	return schedule

def getLessons(params, lstart = 1, lfinish = 8):
	schedule = getSchedule(params)
	
	lessons = []
	for event in schedule:
		if event['day'] == params['day'] and isWeeksEqual(event['week'], params['week'])	\
		and event['numb'] >= lstart	and event['numb'] <= lfinish:
			event['time'] = CONST.LECTION_TIME[event['numb']]
			lessons.append(event)

	if not lessons:
		raise Exception(CONST.ERR_NO_LECTIONS)

	return lessons

def formatLessons(lesson_list):
	string = ''
	for lesson in lesson_list:
		string += CONST.USER_MESSAGE[CONST.CMD_UNIVERSAL].format(
			lesson['numb'],
			lesson['room'], 
			lesson['time'],
			lesson['name']				
		)

	return string	

def cmdUniversal(params):	
	if params['lnumb']:
		lnumb = params['lnumb']
		lesson_list = getLessons(params, lnumb, lnumb)
	else:
		lesson_list = getLessons(params)

	return formatLessons(lesson_list)

def cmdNext(params):
	lection_start = int(getLessonNumb(dt.datetime.now().time())) + 1
	lesson_list = getLessons(params, lection_start)

	return formatLessons(lesson_list)

def cmdWeek(params):
	weeks = (params['date'].date() - dt.date(2017, 2, 5)).days / 7 + 1
	
	return CONST.USER_MESSAGE[CONST.CMD_WEEK].format(weeks)

def cmdLectionsTime(params):
	msg = ''
	for i in CONST.LECTION_TIME:
		msg += CONST.USER_MESSAGE[CONST.CMD_LECTIONS_TIME].format(i, CONST.LECTION_TIME[i])

	return msg

def cmdTeacher(params):
	lesson = getLessons(params, params['lnumb'], params['lnumb'])[0]
	teacher = lesson.get('teacher', '')
	if not teacher:
		raise Exception(CONST.ERR_NO_TEACHER)
	
	return teacher

def cmdHelp(params):
	return ''

def cmdPolite(params):
	return ''

def cmdFindLection(params):
	raise Exception(CONST.ERR_SKIP)
	return ''

def cmdFindTeacher(params):
	raise Exception(CONST.ERR_SKIP)
	return ''

def cmdWhenExams(params):
	week = params['week'] - dt.date(2017, 2, 6).isocalendar()[1] + 1
	
	now = dt.datetime.now().date()
	start = dt.date(2017, 2, 6)
	end = dt.date(2017, 5, 29)
	delta = end - now
	weeks = delta.days / 7 + 1
	days  = delta.days % 7

	delta = now - start
	amount = end - start
	percent = str(int(round((float(delta.days) / amount.days) * 100))) + '%'

	return CONST.USER_MESSAGE[CONST.CMD_WHEN_EXAMS].format(weeks, percent) #(weeks, days, percent)

def cmdMap(params):
	global attachment

	floor = findFloor(params['keyword']['word'])

	if floor:
		attachment = 'photo385457066_' + floor['vk_id']
	else:
		raise Exception(CONST.ERR_NO_ROOM)

	return CONST.USER_MESSAGE[CONST.CMD_MAP].format(floor['desc'])

def cmdExams(params):
	#try:
	#	schedule = db.exams.find({'group':params['group']})[0]['schedule']
	#except:
	#	raise Exception(CONST.ERR_GROUP_NOT_FOUND)
	
	#events = ''
	#for event in schedule:
	#	if event['type'] == True:
	#		events += CONST.USER_MESSAGE[CONST.CMD_EXAMS].format(
	#			event['day'],
	#			event['time'],
	#			event['room'],
	#			event['name']
	#		)

	#return events
	return None

def cmdConsult(params):
	#try:
	#	schedule = db.exams.find({'group':params['group']})[0]['schedule']
	#except:
	#	raise Exception(CONST.ERR_GROUP_NOT_FOUND)
	
	#events = ''
	#for event in schedule:
	#	if event['type'] == False:
	#		events += CONST.USER_MESSAGE[CONST.CMD_CONSULT].format(
	#			event['day'],
	#			event['time'],
	#			event['room'],
	#			event['name']
	#		)

	#return events
	return None

def cmdSession(params):
	#global attachment
	
	#try:
	#	schedule = db.exams.find({'group':params['group']})[0]['schedule']
	#except:
	#	raise Exception(CONST.ERR_GROUP_NOT_FOUND)
	
	#events = ''
	#for event in schedule:
	#	type_name = u'Экзамен' if event['type'] else u'Консультация'		
	#	events += CONST.USER_MESSAGE[CONST.CMD_SESSION].format(
	#		event['day'],
	#		event['time'],
	#		event['room'],
	#		type_name,
	#		event['name']
	#	)
	#attachment = 'photo385457066_456239061'

	#return events
	return None

def cmdCalendarJn(params):
	global attachment	
	attachment = 'photo385457066_456239061'

	return ''

def cmdCalendarDc(params):
	global attachment
	attachment = 'photo385457066_456239062'

	return ''

def cmdZachet(params):
	#global attachment

	#try:
	#	schedule = db.zachet.find({'group':params['group']})[0]['schedule']
	#except:
	#	raise Exception(CONST.ERR_GROUP_NOT_FOUND)
	
	#events = ''
	#prev_day = 0
	#for event in schedule:
	#	if event['day'] < dt.datetime.today().day:
	#		continue
	#	if prev_day <> event['day']:
	#		events += '\n____________\n' + str(event['day']) + u' декабря:\n' 
	#	room =  '' if event['room'] == '-' else u', в ' + event['room']  	
	#	events += CONST.USER_MESSAGE[CONST.CMD_ZACHET].format(
	#		event['numb'],
	#		room,
	#		event['name']
	#	)
	#	prev_day = event['day']
	#attachment = 'photo385457066_456239062'

	#return events
	return None

def cmdMyGroup(params):

	return params['group']['code'].upper()

def cmdWhere(params):
	global attachment

	if params['lnumb']:
		lnumb = params['lnumb']
	else:
		lnumb = int(getLessonNumb(dt.datetime.now().time())) 
			
	lesson = getLessons(params, lnumb, lnumb)[0]
	if not lesson.get('room', False):
		raise Exception(CONST.ERR_NO_ROOM)

	text = CONST.USER_MESSAGE[CONST.CMD_WHERE].format(
		lesson['room'].upper(), 
		lesson['name'], 
	)

	floor = findFloor(lesson['room'])
	if floor:
		attachment = 'photo385457066_' + floor['vk_id']
	else:
		text += CONST.ERR_MESSAGES[CONST.ERR_NO_ROOM]
	
	return text
	
def cmdFor7days(params):
	try:
		day_amount = int(re.search('[1-7]', params['keyword']['word']).group())
	except:
		day_amount = 7
	
	text = ''
	for i in range(0, day_amount):	
		date = params['date'] + dt.timedelta(days = i)
		weekday = date.weekday()
		
		params['day'] 	= weekday
		params['week']	= date.isocalendar()[1]
		try:
			if params['lnumb']:
				lesson_list = getLessons(params, params['lnumb'], params['lnumb'])
			else:
				lesson_list = getLessons(params)
		except:
			continue

		if weekday == 6:
			continue
			
		if len(lesson_list) == 0:
			continue
			
		dname = CONST.DAY_NAMES[weekday].title()
		text += '_'*(len(dname) + len(dname)/2 + 6) + '\n' + dname + ' '+ date.strftime('%d.%m') + '\n'
		text += formatLessons(lesson_list)
		text += '\n'
		
	if len(text) == 0:
		raise Exception(CONST.ERR_NO_LECTIONS)
	
	return text
	

functions = {
	CONST.CMD_UNIVERSAL			: cmdUniversal,
	CONST.CMD_NEXT 				: cmdNext,
	CONST.CMD_TODAY 			: cmdUniversal,
	CONST.CMD_AFTERTOMMOROW 	: cmdUniversal,
	CONST.CMD_TOMMOROW			: cmdUniversal,
	CONST.CMD_YESTERDAY			: cmdUniversal,
	CONST.CMD_DAY_OF_WEEK 		: cmdUniversal,
	CONST.CMD_WEEK				: cmdWeek,
	CONST.CMD_NOW				: cmdUniversal,
	CONST.CMD_BY_DATE			: cmdUniversal,
	CONST.CMD_BY_TIME			: cmdUniversal,
	CONST.CMD_LECTION_NUMB		: cmdUniversal,
	CONST.CMD_HELP				: cmdHelp,
	CONST.CMD_POLITE			: cmdPolite,
	CONST.CMD_LECTIONS_TIME		: cmdLectionsTime,
	CONST.CMD_TEACHER			: cmdTeacher,
	CONST.CMD_FIND_LECTION		: cmdFindLection,
	CONST.CMD_WHEN_EXAMS		: cmdWhenExams,
	CONST.CMD_MAP				: cmdMap,
	CONST.CMD_EXAMS				: cmdExams,
	CONST.CMD_CONSULT			: cmdConsult,
	CONST.CMD_SESSION			: cmdSession,
	CONST.CMD_CALENDAR_JN		: cmdCalendarJn,
	CONST.CMD_CALENDAR_DC		: cmdCalendarDc,
	CONST.CMD_ZACHET			: cmdZachet,
	CONST.CMD_MYGROUP			: cmdMyGroup,
	CONST.CMD_WHERE				: cmdWhere,
	CONST.CMD_FOR7DAYS			: cmdFor7days,
	CONST.CMD_LECTIONS			: cmdUniversal,
}


def findKeywords(words, text):	
	keyword = {}
	for idx, word in enumerate(words):
		try:
			result = re.search(word, text).group()
		except:
			continue
		if result:
			keyword = {'idx': idx, 'word': result}
			break
	return keyword

def getGroup(params):
	answer 		= ''
	group_id 	= 0
	group_code 	= ''
	vk_id 		= params['chat_id'] if params['chat_id'] else params['user_id']
	try:
		db_user = db.Users.get(
			db.Users.vk_id == vk_id, 
			db.Users.vk_chat == bool(params['chat_id'])
		)
	except:
		db_user = None

	match = re.search(u'[а-я]{4}[а-я]?-[0-9]{2}-[0-9]{2}', params['text'])
	msg_group = match.group(0) if match else ''
	params['text'] = params['text'].replace(msg_group, '')
	
	if msg_group and db_user:
		try:
			db_group = db.Groups.get(db.Groups.gcode == msg_group)
		except:
			raise Exception(CONST.ERR_NO_GROUP)		
		db_user.group = db_group.id
		db_user.save()
		answer += CONST.USER_PREMESSAGE[CONST.CMD_SAVE_GROUP].format(msg_group.upper())
	elif msg_group:
		try:
			db_group = db.Groups.get(db.Groups.gcode == msg_group)
		except:
			raise Exception(CONST.ERR_NO_GROUP)	
		db_user = db.Users(
			vk_id			= vk_id,
			vk_chat			= bool(params['chat_id']),
			my_id			= hash(vk_id + 'h3d8er3f3'),
			group			= db_group.id,
			notice_today	= False,
			notice_tommorow	= False,
			notice_week		= False,
			notice_map		= False
		)
		db_user.save()
		
		answer += CONST.USER_PREMESSAGE[CONST.CMD_SAVE_GROUP].format(msg_group.upper())
		answer += CONST.USER_PREMESSAGE[CONST.CMD_HELP]
	elif db_user:
		group_id = db_user.group.id
		group_code = db_user.group.gcode
	else:
		raise Exception(CONST.ERR_NO_GROUP)	

	group = {
		'id' 	: group_id,
		'code'	: group_code
	}
	return group, answer	

# Takes message and prepare answer for it.
# Return type: string
def analize(params):
	answer = ''
	answer_ok = False

	# Set default settings
	group, answer = getGroup(params)
	answer_ok = bool(answer)
	markers = {}
	default_kwd = {'word': u'сегодня', 'idx': 0}
	command	= {
		'code'	 : CONST.CMD_UNIVERSAL, 
		'keyword': default_kwd
	}
	date 	= dt.datetime.today()
	lesson 	= 0
	
	# Define command
	for cmd, keywords in CONST.KEYWORDS.items():
		if cmd in CONST.MARKERS:
			continue
		word = findKeywords(keywords, params['text']) 
		if word and (command['code'] >= cmd):
			command['code'] 	= cmd 
			command['keyword'] 	= word
			answer_ok 			= True
	if answer_ok:
		params['text'] = params['text'].replace(command['keyword']['word'], '')
	
	# Find all markers
	for cmd, keywords in CONST.KEYWORDS.items():
		if not cmd in CONST.MARKERS:
			continue
		word = findKeywords(keywords, params['text']) 
		if word:
			params['text'] = params['text'].replace(word['word'], '')
			markers[cmd] = word
	
	if answer_ok and not markers:
		markers = {CONST.CMD_TODAY: default_kwd}	
	
	# Apply markers for settings
	for cmd_code, keyword in markers.items():
		if cmd_code == CONST.CMD_TOMMOROW:
			date = dt.datetime.today() + dt.timedelta(days=1)
		elif cmd_code == CONST.CMD_NOW:
			lesson = int(getLessonNumb(dt.datetime.now().time()))
		elif cmd_code == CONST.CMD_AFTERTOMMOROW:
			date = dt.datetime.today() + dt.timedelta(days=2)
		elif cmd_code == CONST.CMD_YESTERDAY:
			date = dt.datetime.today() - dt.timedelta(days=1)
		elif cmd_code == CONST.CMD_DAY_OF_WEEK:
			keyword['word'] = CONST.DAY_NAMES_VINIT[keyword['idx']]
			for i in range(0,7):
				temp_date = dt.datetime.today() + dt.timedelta(days=i)
				if temp_date.weekday() == keyword['idx']:
					date = temp_date
					break
		elif cmd_code == CONST.CMD_LECTION_NUMB:
			lesson = keyword['idx']
			keyword['word'] = keyword['idx']
		elif cmd_code == CONST.CMD_BY_TIME:
			try:
				lesson = getLessonNumb(dt.datetime.strptime(keyword['word'], '%H:%M').time())
			except:
				del markers[cmd_code]
		elif cmd_code == CONST.CMD_BY_DATE:
			try:
				year = str(dt.date.today().year)
				date = dt.datetime.strptime(keyword['word']+year, '%d.%m%Y')
			except:
				try:
					day, month = keyword['word'].split(' ')
					mnumb = 0
					for idx, name in enumerate(CONST.MONTH_NAMES):
						if re.search(name, month):
							mnumb = idx + 1
							break
					date = dt.date(2017, mnumb, int(day))
				except:
					del markers[cmd_code]

	# Prepare parametrs for functions 
	cmd_params = {
		'vk_id'		: params['chat_id'] if params['chat_id'] else params['user_id'],
		'is_chat'	: bool(params['chat_id']),
		'group'		: group,
		'date'		: date,
		'day' 		: date.weekday(),
		'week'		: date.isocalendar()[1],
		'lnumb'		: lesson,
		'keyword'	: command['keyword']
	}
	
	# Check markers after apply
	header = ''
	for cmd, kwd in markers.items():
		header += CONST.USER_PREMESSAGE[cmd].format(kwd['word'])
		answer_ok = True
	if not answer_ok:
		logger.log(CONST.LOG_MESGS, params['text'])
		raise Exception(CONST.ERR_SKIP)

	# Perform command and check for result
	answer += CONST.USER_PREMESSAGE[command['code']].format(markers = header)
	try:
		answer += functions[command['code']](cmd_params)
	except Exception as e:
		if isinstance(e.args[0], int):
			if e.args[0] == CONST.ERR_GROUP_NOT_FOUND:
				answer = CONST.ERR_MESSAGES[e.args[0]].format(cmd_params['group'].upper())
			else:
				answer += CONST.ERR_MESSAGES[e.args[0]]
		else:
			raise e
	
	return answer	

def genAnswer(params):
	global attachment
	attachment = ''
	answer = {
		'text':'',
		'attachment':''
	}

	params['text']	= params['text'].lower()

	# Check for chat
	if params['chat_id'] and not any(re.match('^' + word, params['text']) for word in CONST.CHAT_KEYWORDS):
		raise Exception(CONST.ERR_SKIP)

	# Check feedback
	if any(re.search(word, params['text']) for word in CONST.FEEDBACK_KEYWORDS):
		logger.log(CONST.LOG_FBACK, params['user_id'] + ' ' + params['text'])
		answer['text'] = CONST.USER_PREMESSAGE[CONST.CMD_FEEDBACK]
		return answer
		
	answer['text'] = analize(params)
	answer['attachment'] = attachment
	
	return answer

				

