import subprocess
import os
import re
import json
import requests
from pprint import pprint
from gmplot import GoogleMapPlotter
from WGS84ToGCJ02 import transform
import time
from pprint import *
import sys

class pict_on_google_map :
	def __init__(self,location, file_path):
		self._file_path = file_path
		self._gmap  = GoogleMapPlotter.from_geocode(location)
		self._marker_list = []
		self._jpg_paths = []
		self._per_dir_jpg_paths = {}

	def get_jpg_list_from_path(self):
		for root,directories,files in os.walk(self._file_path):
			found_jpg_in_dir = False
			files_in_dir = []
			for f in files:
				if f.endswith('.JPG') or f.endswith('.jpg'):
					found_jpg_in_dir= True
					self._jpg_paths.append(os.path.join(root,f))
					files_in_dir.append(os.path.join(root,f))
			if found_jpg_in_dir :
				self._per_dir_jpg_paths[root] =	files_in_dir

	#Draw on Google Maps		
	def main(self):
		self.get_jpg_list_from_path()
		for filepath in self._jpg_paths:
#				print(filepath)
				try: 
					pict_dict = self.get_json_from_pict(filepath)
					if self.check_gps_data_in_dict(pict_dict):
						self.add_marker_list(pict_dict)
				except Exception:
					pass

		self.plot_on_google_map()
		self.draw_google_map()
					

		
	def check_gps_data_in_dict(self,pict_dict):
		if 'GPSDateStamp' in pict_dict and 'GPSLatitude' in pict_dict:
			return True
		else :
			return False
			

	def get_json_from_pict(self,file_name):
		cli_name = "./exiftool -j " + file_name
#		print(cli_name)
		ret = subprocess.getoutput(cli_name)
#		print(ret)
		pict_list = json.loads(ret)
		return pict_list[0]
	def get_gps_time(self,pict_dict):
		return pict_dict['GPSDateStamp']
	def get_gps_latitude(self,pict_dict):
		lat_str = pict_dict['GPSLatitude']
		latitude = self.trans_gps_cord(lat_str)
		return latitude
	def get_gps_longtitude(self,pict_dict):
		longti_str = pict_dict['GPSLongitude']
		longtitude = self.trans_gps_cord(longti_str)
		return longtitude
	def get_gps_altitude(self,pict_dict):
		return pict_dict['GPSAltitude']
	
	def trans_gps_cord(self, str):
#		x = re.split(31 deg 10' 55.01" N
		x = re.split('\ |\'|"',str)
#		print(x)
		if (x[6] == 'W') or (x[6] == 'S'):
			flag = -1
		else:
			flag = 1
		x = [x[0],x[2],x[4]]
		x = [ float(t) for t in x]
		return flag*(x[0] + x[1]/60 + x[2]/3600)
	def get_mars_geo(self,pict_dict):
		return transform(self.get_gps_latitude(pict_dict),self.get_gps_longtitude(pict_dict))

		
	def add_marker_list(self,pict_dict):
#		tup = (self.get_gps_latitude(),self.get_gps_longtitude())
		mg_lat ,mg_long = self.get_mars_geo(pict_dict)
		tup = (mg_lat, mg_long)
		self._marker_list.append(tup)
#		print(self._marker_list)
		
	def plot_on_google_map(self):
		for item in self._marker_list:
			self._gmap.marker(item[0],item[1],"red")
	def draw_google_map(self):
			self._gmap.draw('./mymap.html')
		
	
		


if __name__ == '__main__':
	if len(sys.argv) != 3:
		print("usage : python plot_on_google_maps.py location photo_directory")
		sys.exit()
	plot_pict = pict_on_google_map(sys.argv[1],sys.argv[2])
	plot_pict.main()
	
	


	
	

