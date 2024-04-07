"""
Для конвертации финального видео в mp4 требуется установленный в систему ffmpeg
"""
import os
#import sys
import shutil
import requests
from bs4 import BeautifulSoup as bs
import json
import ast
import time

def merge_ts(video_id, count):
	with open(f'seg\\{video_id}.ts', 'wb') as merged:
		for ts in range(1, count+1):
			with open(f'seg\\segment-{ts}-v1-a1.ts', 'rb') as mergefile:
				shutil.copyfileobj(mergefile, merged)
	os.system(f"ffmpeg -i seg\\{video_id}.ts {video_id}.mp4")
	print('[+] - Конвертирование завершено')

	file_dir = os.listdir('seg')
	for file in file_dir:
		os.remove(f'seg\\{file}')
	os.removedirs('seg')
		

def get_download_segment(link, count):
	if not os.path.isdir('seg'):
		os.mkdir('seg')
	for item in range(1, count+1):
		print(f'[+] - Загружаю сегмент {item}/{count}')
		# бесконечно пытаюсь скачать, пока не добьюсь успеха
		while True:
			try:
				req = requests.get(f'{link}segment-{item}-v1-a1.ts')
				#УБРАТЬ УСЛОВИЕ проверки ts файла!!! ТОЛЬКО НА ВРЕМЯ ТЕСТОВ!!!
				if not os.path.exists(f'seg\\segment-{item}-v1-a1.ts'):
					with open(f'seg\\segment-{item}-v1-a1.ts', 'wb') as file:
						file.write(req.content)
				break
			except MaxRetryError as e:
				print(e)
				time.sleep(5)
	print('[INFO] - Все сегменты загружены')

def get_download_link(m3u8_link):
	link = f'{m3u8_link.split(".m3u8")[0]}/'
	return link

def get_segment_count(m3u8_link):
	req = requests.get(url=m3u8_link)
	data_seg_dict = []
	for seg in req:
		data_seg_dict.append(seg)
	print(data_seg_dict)
	seg_count = int(str(data_seg_dict[-2]).split("/")[-1].split("-")[1])
	return seg_count

def get_best_link_from_m3u8(m3u8_url):
	if not os.path.isdir('seg'):
		os.mkdir('seg')
	req = requests.get(url=m3u8_url)
	data_m3u8_dict = []
	with open('seg\\pl_list.txt', 'w', encoding='utf-8') as file:
		file.write(req.text)
	with open('seg\\pl_list.txt', 'r', encoding='utf-8') as file:
		src = file.readlines()

	for item in src:
		data_m3u8_dict.append(item)

	url_playlist = data_m3u8_dict[-1]
	return url_playlist

def get_m3u8_list(video_id):
	prefix = 'https://rutube.ru/api/play/options/'
	url = f'{prefix}{video_id}'
	req = requests.get(url=url)
	video_json_data = req.json()
	m3u8_url = video_json_data['video_balancer']['m3u8']
	return m3u8_url
	
def seeker1(playlist_url):
	playlist_id = playlist_url.split('playlist=')[-1]

	video_data_list = []
	nexp_flag = True
	page = 1
	while nexp_flag:
		url = f'https://rutube.ru/api/playlist/custom/{playlist_id}/videos/?limit=20&page={page}'
		#headers = {'Content-Type': 'application/json; charset=utf-8'}
		r = requests.get(url)#, headers=headers)
		json = r.json()
		video_data_dict = {}
		for result in json['results']:
			video_data_dict = {}
			video_data_dict['video_id'] = result['id']
			video_data_dict['title'] = result['title']
			video_data_dict['description'] = result['description']
			video_data_dict['category_id'] = result['category']['id']
			video_data_dict['category_name'] = result['category']['name']
			video_data_dict['img_link'] = result['thumbnail_url']
			#create_shortcut(file_name, target, work_dir)
			video_data_list.append(video_data_dict)
		nexp_flag = json['has_next']
		page += 1
	return video_data_list

def seeker(playlist_id):
	video_data_list = []
	nexp_flag = True
	page = 1
	
	while nexp_flag:
		url = f'https://rutube.ru/api/playlist/custom/{playlist_id}/videos/?limit=20&page={page}'
		#headers = {'Content-Type': 'application/json; charset=utf-8'}
		r = requests.get(url)#, headers=headers)
		json = r.json()
		video_data_dict = {}
		for result in json['results']:
			video_data_dict = {}
			video_data_dict['video_id'] = result['id']
			video_data_dict['title'] = result['title']
			video_data_dict['description'] = result['description']
			video_data_dict['category_id'] = result['category']['id']
			video_data_dict['category_name'] = result['category']['name']
			video_data_dict['img_link'] = result['thumbnail_url']
			#create_shortcut(file_name, target, work_dir)
			video_data_list.append(video_data_dict)
		nexp_flag = json['has_next']
		page += 1
	return video_data_list

def main(playlist_url):
	#ссылки на плейлист могут быть трех типов или даже больше! написать логику выбора метода, потестить
	if playlist_url.endswith('/'):
		playlist_id = playlist_url.replace('/','').split('plst')[-1]
		print(f'ПОСЛЕ: {playlist_id}, ДО: {playlist_url}')
	elif '&playlistPage=' in playlist_url:
		playlist_id = playlist_url.split('playlist=')[-1].split('&')[0]
		print(f'ПОСЛЕ: {playlist_id}, ДО: {playlist_url}')
	else:
		playlist_id = playlist_url.split('playlist=')[-1].split('&')[0]
		print(f'ПОСЛЕ: {playlist_id}, ДО: {playlist_url}')

	video_data_list = seeker(playlist_id)
	for video in video_data_list:
		video_id = video['video_id']
		#
		# тут вызываем метод проверки отсутствия в базе. Если отсутствует, идём дальше, если присутствует, пропускаем
		#
		#print(video_id)
		m3u8_url = get_m3u8_list(video_id)
		print(m3u8_url)
		best_resolution_m3u8_link = get_best_link_from_m3u8(m3u8_url)
		print(best_resolution_m3u8_link)
		count = get_segment_count(best_resolution_m3u8_link)
		print(count)
		link = get_download_link(best_resolution_m3u8_link)
		print(link)
		print(video)
		get_download_segment(link, count)
		merge_ts(video_id, count)
		#
		# тут вызываем метод отправки скачанного видео в телеграм
		#
		#
		# тут вызываем метод добавления данных по скачанному видео в базу
		#
		#sys.exit()

	

if __name__ == '__main__':
	#TESTS
	playlist_url = 'https://rutube.ru/video/8e9315f724a70b1798d8694b92d12176/?playlist=330005'
	#ПОСЛЕ: 330005, ДО: https://rutube.ru/video/8e9315f724a70b1798d8694b92d12176/?playlist=330005

	#playlist_url = 'https://rutube.ru/plst/330005/'
	#ПОСЛЕ: 330005, ДО: https://rutube.ru/plst/330005/

	#playlist_url = 'https://rutube.ru/video/8e9315f724a70b1798d8694b92d12176/?playlist=330005&playlistPage=1'
	#ПОСЛЕ: 330005, ДО: https://rutube.ru/video/8e9315f724a70b1798d8694b92d12176/?playlist=330005&playlistPage=1

	main(playlist_url)
	