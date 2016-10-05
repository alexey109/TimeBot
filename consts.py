#!/usr/bin/env python
# -*- coding: UTF-8 -*-


# There is all constant values used by all project classes.
class CONST:
	# Enable/disable logging everything.
	LOG	 = True
	# Enable/disable test mode
	TEST = False


	# Commands (CMD)
	CMD_TO_DEVELOPER	= 100 
	CMD_NEXT 			= 110
	CMD_TODAY 			= 120
	CMD_AFTERTOMMOROW 	= 130 # It is important to be aftertommorow before tomorrow :)
	CMD_TOMMOROW		= 140
	CMD_DAY_OF_WEEK 	= 150
	CMD_WEEK_NUMB		= 160 # It is important to be aftertommorow before current lection :)
	CMD_NOW				= 170 
	CMD_WHERE_LECTION	= 180 #TODO Add implementation

	SAVED_GROUP_NAME	= 1000

	DAY_NAMES = (
		u'понедельник', 
		u'вторник',
		u'среду',
		u'четверг',
		u'пятницу',
		u'субботу'
	)

	# Keywords using when send message from group's chat.
	CHAT_KEYWORDS = (u'рп,+', u'расписание,+', u'том,+', u'луи,+', u'бот,+')
	# Keywords for every command.
	CMD_KEYWORDS = {
		CMD_NEXT 			: [u'дальше', u'следующая', u'следующие', u'оставшиеся', u'остались'],
		CMD_TODAY 			: [u'сегодня'],
		CMD_AFTERTOMMOROW 	: [u'послезавтра'], 
		CMD_TOMMOROW		: [u'завтра'],
		CMD_WEEK_NUMB		: [u'неделя+'],
		CMD_NOW				: [u'сейчас', u'текущая'],
		CMD_DAY_OF_WEEK 	: DAY_NAMES,
		CMD_TO_DEVELOPER	: [u'(разработчику)', u'(предложение)', u'(ошибка)']
	}

	# Template takes: lection number, classroom, time(start-end), lection name
	UNI_TEMPLATE = u'\n%s пара (%s, %s):\n%s\n'
	USER_PREMESSAGE = {
		# Parametrs: UNI_TEMPLATE (for all next messages)
		CMD_NEXT 			: u'Следующие пары:\n%s',
		CMD_TODAY 			: u'Пары сегодня:\n%s',
		CMD_TOMMOROW		: u'Пары завтра:\n%s',
		CMD_AFTERTOMMOROW 	: u'Пары послезавтра:\n%s',
		CMD_WEEK_NUMB		: u'Сейчас идет %s неделя.',
		CMD_NOW				: u'Текущая пара:\n%s',
		CMD_DAY_OF_WEEK 	: u'Пары в %s:\n%s', # One new parametr: day of week
		CMD_TO_DEVELOPER	: u'Сообщение принято и обязательно будет рассмотрено, спасибо :)',
		SAVED_GROUP_NAME	: u'Я запомнил, что ты из %s.\n\n'
	}

	# Dictionary of lections start-end time for using in messages
	LECTION_TIME = {
		1: '9:00-10:35',
		2: '10:45-12:20',
		3: '12:50-14:25',
		4: '14:35-16:10',
		5: '16:20-17:55',
		6: '18:00-21:20',
	}


	# Error codes, will raise as exceptions.
	ERR_UNDEFINED 		= 0
	ERR_SKIP			= 1
	ERR_GROUP_NOT_FOUND = 2
	ERR_NO_GROUP_NAME	= 3
	ERR_NO_COMMAND		= 4
	ERR_NO_LECTIONS		= 5
	
	ERR_MESSAGES = {
		ERR_UNDEFINED: u'Что-то пошло не так, повторите запрос еще раз :(',
		ERR_SKIP: '',
		ERR_GROUP_NOT_FOUND: u'Группа не найдена :(\nНазвание группы указано с ошибками,'\
			+ u' либо расписание для данной группы пока недоступно.',
		ERR_NO_GROUP_NAME: u'Не удается распознать группу :(\n\n'\
			+ u'Укажите группу в названии беседы или в сообщении.\n'\
			+ u'Примеры сообщения:\n'\
			+ u'"Расписание, какие пары завтра у группы ИКБО-04-15"\n'\
			+ u'"Расписание, что во вторник?"',
		ERR_NO_COMMAND: u'Неизвестная команда :(',
		ERR_NO_LECTIONS: u'Пар нет :)'
	}

# Class, which save bot activity.
#class Logger():
# TODO: write implementation of this class
