from Components.Converter.Converter import Converter
from enigma import iServiceInformation, iPlayableService, eServiceReference
from Screens.InfoBarGenerics import hasActiveSubservicesForCurrentChannel
from Components.Element import cached
from Components.Converter.Poll import Poll
from Components.SystemInfo import BoxInfo
from Tools.Transponder import ConvertToHumanReadable

from os import path

WIDESCREEN = [1, 3, 4, 7, 8, 0xB, 0xC, 0xF, 0x10]


class ServiceInfo(Poll, Converter):
	HAS_TELETEXT = 1
	IS_MULTICHANNEL = 2
	IS_STEREO = 3
	IS_CRYPTED = 4
	IS_WIDESCREEN = 5
	IS_NOT_WIDESCREEN = 6
	SUBSERVICES_AVAILABLE = 7
	XRES = 8
	YRES = 9
	APID = 10
	VPID = 11
	PCRPID = 12
	PMTPID = 13
	TXTPID = 14
	TSID = 15
	ONID = 16
	SID = 17
	FRAMERATE = 18
	TRANSFERBPS = 19
	HAS_HBBTV = 20
	AUDIOTRACKS_AVAILABLE = 21
	SUBTITLES_AVAILABLE = 22
	EDITMODE = 23
	IS_STREAM = 24
	IS_SD = 25
	IS_HD = 26
	IS_1080 = 27
	IS_720 = 28
	IS_576 = 29
	IS_480 = 30
	IS_4K = 31
	FREQ_INFO = 38
	PROGRESSIVE = 39
	VIDEO_INFO = 40
	IS_SD_AND_WIDESCREEN = 35
	IS_SD_AND_NOT_WIDESCREEN = 36
	IS_SDR = 37
	IS_HDR = 38
	IS_HDR10 = 39
	IS_HLG = 40
	IS_VIDEO_MPEG2 = 41
	IS_VIDEO_AVC = 42
	IS_VIDEO_HEVC = 43

	def __init__(self, type):
		Poll.__init__(self)
		Converter.__init__(self, type)
		self.poll_interval = 5000
		self.poll_enabled = True
		self.type, self.interesting_events = {
			"HasTelext": (self.HAS_TELETEXT, (iPlayableService.evUpdatedInfo,)),
			"IsMultichannel": (self.IS_MULTICHANNEL, (iPlayableService.evUpdatedInfo,)),
			"IsStereo": (self.AUDIO_STEREO, (iPlayableService.evUpdatedInfo,)),
			"IsCrypted": (self.IS_CRYPTED, (iPlayableService.evUpdatedInfo,)),
			"IsWidescreen": (self.IS_WIDESCREEN, (iPlayableService.evVideoSizeChanged,)),
			"IsNotWidescreen": (self.IS_NOT_WIDESCREEN, (iPlayableService.evVideoSizeChanged,)),
			"SubservicesAvailable": (self.SUBSERVICES_AVAILABLE, (iPlayableService.evUpdatedEventInfo,)),
			"VideoWidth": (self.XRES, (iPlayableService.evVideoSizeChanged,)),
			"VideoHeight": (self.YRES, (iPlayableService.evVideoSizeChanged,)),
			"AudioPid": (self.APID, (iPlayableService.evUpdatedInfo,)),
			"VideoPid": (self.VPID, (iPlayableService.evUpdatedInfo,)),
			"PcrPid": (self.PCRPID, (iPlayableService.evUpdatedInfo,)),
			"PmtPid": (self.PMTPID, (iPlayableService.evUpdatedInfo,)),
			"TxtPid": (self.TXTPID, (iPlayableService.evUpdatedInfo,)),
			"TsId": (self.TSID, (iPlayableService.evUpdatedInfo,)),
			"OnId": (self.ONID, (iPlayableService.evUpdatedInfo,)),
			"Sid": (self.SID, (iPlayableService.evUpdatedInfo,)),
			"Framerate": (self.FRAMERATE, (iPlayableService.evVideoSizeChanged,iPlayableService.evUpdatedInfo,)),
			"Progressive": (self.PROGRESSIVE, (iPlayableService.evVideoProgressiveChanged, iPlayableService.evUpdatedInfo,)),
			"VideoInfo": (self.VIDEO_INFO, (iPlayableService.evVideoSizeChanged, iPlayableService.evVideoFramerateChanged, iPlayableService.evVideoProgressiveChanged, iPlayableService.evUpdatedInfo,)),
			"TransferBPS": (self.TRANSFERBPS, (iPlayableService.evUpdatedInfo,)),
			"HasHBBTV": (self.HAS_HBBTV, (iPlayableService.evUpdatedInfo,iPlayableService.evHBBTVInfo,)),
			"AudioTracksAvailable": (self.AUDIOTRACKS_AVAILABLE, (iPlayableService.evUpdatedInfo,)),
			"SubtitlesAvailable": (self.SUBTITLES_AVAILABLE, (iPlayableService.evUpdatedInfo,)),
			"Freq_Info": (self.FREQ_INFO, (iPlayableService.evUpdatedInfo,)),
			"Editmode": (self.EDITMODE, (iPlayableService.evUpdatedInfo,)),
			"IsStream": (self.IS_STREAM, (iPlayableService.evUpdatedInfo,)),
			"IsSD": (self.IS_SD, (iPlayableService.evVideoSizeChanged,)),
			"IsHD": (self.IS_HD, (iPlayableService.evVideoSizeChanged,iPlayableService.evVideoGammaChanged,)),
			"Is1080": (self.IS_1080, (iPlayableService.evVideoSizeChanged,)),
			"Is720": (self.IS_720, (iPlayableService.evVideoSizeChanged,)),
			"Is576": (self.IS_576, (iPlayableService.evVideoSizeChanged,)),
			"Is480": (self.IS_480, (iPlayableService.evVideoSizeChanged,)),
			"Is4K": (self.IS_4K, (iPlayableService.evVideoSizeChanged,iPlayableService.evVideoGammaChanged,)),
			"IsIPStream": (self.IS_IPSTREAM, (iPlayableService.evUpdatedInfo,)),
			"IsSDR": (self.IS_SDR, (iPlayableService.evVideoSizeChanged,iPlayableService.evVideoGammaChanged,)),
			"IsHDR": (self.IS_HDR, (iPlayableService.evVideoSizeChanged,iPlayableService.evVideoGammaChanged,)),
			"IsHDR10": (self.IS_HDR10, (iPlayableService.evVideoSizeChanged,iPlayableService.evVideoGammaChanged,)),
			"IsHLG": (self.IS_HLG, (iPlayableService.evVideoSizeChanged,iPlayableService.evVideoGammaChanged,)),
			"IsHDHDR": (self.IS_HDHDR, (iPlayableService.evVideoSizeChanged,iPlayableService.evVideoGammaChanged,)),
		}[type]
		self.interesting_events += (iPlayableService.evStart,)

	def _isHDMIIn(self, info):
		return eServiceReference(info.getInfoString(iServiceInformation.sServiceref)).type == eServiceReference.idServiceHDMIIn

	def getServiceInfoString(self, info, what, convert=lambda x: "%d" % x):
		if self._isHDMIIn(info):
			return "N/A"
		v = info.getInfo(what)
		if v == -1:
			return "N/A"
		if v == -2:
			return info.getInfoString(what)
		return convert(v)

	def _getProcVal(self, pathname, base=10):
		val = None
		try:
			f = open(pathname, "r")
			val = int(f.read(), base)
			f.close()
			if val >= 2 ** 31:
				val -= 2 ** 32
		except Exception as e:
			pass
		return val

	def _getVal(self, pathname, info, infoVal, base=10):
		if self._isHDMIIn(info):
			return None
		val = self._getProcVal(pathname, base=base)

		return val if val is not None else info.getInfo(infoVal)

	def _getValInt(self, pathname, info, infoVal, base=10, default=-1):
		val = self._getVal(pathname, info, infoVal, base)
		return val if val is not None else default

	def _getValStr(self, pathname, info, infoVal, base=10, convert=lambda x: "%d" % x):
		if self._isHDMIIn(info):
			return "N/A"
		val = self._getProcVal(pathname, base=base)

		return convert(val) if val is not None else self.getServiceInfoString(info, infoVal, convert)

	def _getVideoHeight(self, info):
		return self._getValInt("/proc/stb/vmpeg/0/yres", info, iServiceInformation.sVideoHeight, base=16)

	def _getVideoHeightStr(self, info, convert=lambda x: "%d" % x if x > 0 else "?"):
		return self._getValStr("/proc/stb/vmpeg/0/yres", info, iServiceInformation.sVideoHeight, base=16, convert=convert)

	def _getVideoWidth(self, info):
		return self._getValInt("/proc/stb/vmpeg/0/xres", info, iServiceInformation.sVideoWidth, base=16)

	def _getVideoWidthStr(self, info, convert=lambda x: "%d" % x if x > 0 else "?"):
		return self._getValStr("/proc/stb/vmpeg/0/xres", info, iServiceInformation.sVideoWidth, base=16, convert=convert)

	def _getFrameRate(self, info):
		return self._getValInt("/proc/stb/vmpeg/0/framerate", info, iServiceInformation.sFrameRate)

	def _getFrameRateStr(self, info, convert=lambda x: "%d" % x if x > 0 else ""):
		return self._getValStr("/proc/stb/vmpeg/0/framerate", info, iServiceInformation.sFrameRate, convert=convert)

	def _getProgressive(self, info):
		return self._getValInt("/proc/stb/vmpeg/0/progressive", info, iServiceInformation.sProgressive, default=0)

	def _getProgressiveStr(self, info, convert=lambda x: "" if x else "i"):
		return self._getValStr("/proc/stb/vmpeg/0/progressive", info, iServiceInformation.sProgressive, convert=convert)

#	def _getProcVal(self, pathname, base=10):
#		val = None
#		try:
#			f = open(pathname, "r")
#			val = int(f.read(), base)
#			f.close()
#			if val >= 2 ** 31:
#				val -= 2 ** 32
#		except Exception:
#			pass
#		return val

#	def _getVal(self, pathname, info, infoVal, base=10):
#		if self._isHDMIIn(info):
#			return None
#		val = self._getProcVal(pathname, base=base)
#		return val if val is not None else info.getInfo(infoVal)

#	def _getValInt(self, pathname, info, infoVal, base=10, default=-1):
#		val = self._getVal(pathname, info, infoVal, base)
#		return val if val is not None else default

#	def _getValStr(self, pathname, info, infoVal, base=10, convert=lambda x: "%d" % x):
#		if self._isHDMIIn(info):
#			return "N/A"
#		val = self._getProcVal(pathname, base=base)
#		return convert(val) if val is not None else self.getServiceInfoString(info, infoVal, convert)

	def _getVideoHeight(self, info):
		if self._isHDMIIn(info):
			return -1
		val = eAVControl.getInstance().getResolutionY(0)
		return val if val else info.getInfo(iServiceInformation.sVideoHeight)

	def _getVideoHeightStr(self, info, convert=lambda x: "%d" % x if x > 0 else "?"):
		if self._isHDMIIn(info):
			return "?"
		val = eAVControl.getInstance().getResolutionY(0)
		return convert(val) if val else self.getServiceInfoString(info, iServiceInformation.sVideoHeight, convert)

	def _getVideoWidth(self, info):
		if self._isHDMIIn(info):
			return -1
		val = eAVControl.getInstance().getResolutionX(0)
		return val if val else info.getInfo(iServiceInformation.sVideoWidth)

	def _getVideoWidthStr(self, info, convert=lambda x: "%d" % x if x > 0 else "?"):
		if self._isHDMIIn(info):
			return "?"
		val = eAVControl.getInstance().getResolutionX(0)
		return convert(val) if val else self.getServiceInfoString(info, iServiceInformation.sVideoWidth, convert)

	def _getFrameRate(self, info):
		if self._isHDMIIn(info):
			return -1
		val = eAVControl.getInstance().getFrameRate(0)
		return val if val else info.getInfo(iServiceInformation.sFrameRate)

	def _getFrameRateStr(self, info, convert=lambda x: "%d" % x if x > 0 else ""):
		if self._isHDMIIn(info):
			return ""
		val = eAVControl.getInstance().getFrameRate(0)
		return convert(val) if val else self.getServiceInfoString(info, iServiceInformation.sFrameRate, convert)

	def _getProgressive(self, info):
		if self._isHDMIIn(info):
			return 0
		return eAVControl.getInstance().getProgressive()

	def _getProgressiveStr(self, info):
		if self._isHDMIIn(info):
			return "i"
		return "p" if eAVControl.getInstance().getProgressive() else "i"

	@cached
	def getBoolean(self):
		service = self.source.service
		info = service and service.info()
		if not info:
			return False
		video_height = None
		video_width = None
		video_aspect = None
		video_height = self._getVideoHeight(info)
		video_width = self._getVideoWidth(info)

		if path.exists("/proc/stb/vmpeg/0/aspect"):
			f = open("/proc/stb/vmpeg/0/aspect", "r")
			try:
				video_aspect = int(f.read())
			except:
				pass
			f.close()

		if not video_aspect:
			video_aspect = info.getInfo(iServiceInformation.sAspect)

		if self.type == self.HAS_TELETEXT:
			tpid = info.getInfo(iServiceInformation.sTXTPID)
			return tpid != -1
		elif self.type in (self.IS_MULTICHANNEL, self.IS_STEREO):
			# FIXME. but currently iAudioTrackInfo doesn't provide more information.
			audio = service.audioTracks()
			if audio:
				n = audio.getNumberOfTracks()
				idx = 0
				while idx < n:
					i = audio.getTrackInfo(idx)
					description = i.getDescription().replace("A_", "").replace("", "").replace("AC-3", "AC3").replace("(ATSC A/52)", "").replace("(ATSC A/52B)", "").replace("MPEG", "AAC").replace(" Layer 2 (MP2)", "").replace(" 3 (MP3)", "MP3").replace("-1", "").replace("2-", "").replace("-4 AAC", "").replace("4-AAC", "HE-AAC").replace("audio", "").replace("/L3", "").replace("/mpeg", "AAC").replace("/x-",  "").replace("raw",  "Dolby TrueHD").replace("E-AC3", "AC3+").replace("EAC3", "AC3+").replace("IPCM", "AC3").replace("LPCM", "AC3+").replace("AAC_PLUS", "AAC+").replace("AAC_LATM", "AAC").replace("WMA/PRO", "WMA Pro")
					if description and description.split()[0] in ("AC4", "AAC+", "AC3", "AC3+", "Dolby", "DTS", "DTS-HD", "HE-AAC", "IPCM", "LPCM", "WMA Pro"):
						if self.type == self.IS_MULTICHANNEL:
							return True
						elif self.type == self.IS_STEREO:
							return False
					idx += 1
				if self.type == self.IS_MULTICHANNEL:
					return False
				elif self.type == self.IS_STEREO:
					return True
			return False
		elif self.type == self.IS_CRYPTED:
			return info.getInfo(iServiceInformation.sIsCrypted) == 1
		elif self.type == self.SUBSERVICES_AVAILABLE:
			return hasActiveSubservicesForCurrentChannel(':'.join(info.getInfoString(iServiceInformation.sServiceref).split(':')[:11]))
		elif self.type == self.HAS_HBBTV:
			return info.getInfoString(iServiceInformation.sHBBTVUrl) != ""
		elif self.type == self.AUDIOTRACKS_AVAILABLE:
			audio = service.audioTracks()
			return bool(audio) and audio.getNumberOfTracks() > 1
		elif self.type == self.SUBTITLES_AVAILABLE:
			subtitle = service and service.subtitle()
			subtitlelist = subtitle and subtitle.getSubtitleList()
			if subtitlelist:
				return len(subtitlelist) > 0
			return False
		elif self.type == self.EDITMODE:
			return hasattr(self.source, "editmode") and not not self.source.editmode
		elif self.type == self.IS_STREAM:
			return service.streamed() is not None
		elif self.isVideoService(info):
			if self.type == self.IS_WIDESCREEN:
				return video_aspect in WIDESCREEN
			elif self.type == self.IS_NOT_WIDESCREEN:
				return video_aspect not in WIDESCREEN
			elif self.type == self.IS_HD:
				return video_width > 1025 and video_width <= 1920 and video_height >= 481 and video_height < 1440 or video_width >= 960 and video_height == 720
			elif self.type == self.IS_SD:
				return video_width > 1 and video_width <= 1024 and video_height > 1 and video_height <= 578
			elif self.type == self.IS_SD_AND_WIDESCREEN:
				return video_height < 578 and video_aspect in WIDESCREEN
			elif self.type == self.IS_SD_AND_NOT_WIDESCREEN:
				return video_height < 578 and video_aspect not in WIDESCREEN
			elif self.type == self.IS_1080:
				return video_width >= 1367 and video_width <= 1920 and video_height >= 768 and video_height <= 1440
			elif self.type == self.IS_720:
				return video_width >= 1025 and video_width <= 1366 and video_height >= 481 and video_height <= 768 or video_width >= 960 and video_height == 720
			elif self.type == self.IS_576:
				return video_width > 1 and video_width <= 1024 and video_height > 481 and video_height <= 578
			elif self.type == self.IS_480:
 				return video_width > 1 and video_width <= 1024 and video_height > 1 and video_height <= 480
			elif self.type == self.IS_4K:
				return video_height >= 1460
			elif self.type == self.PROGRESSIVE:
				return bool(self._getProgressive(info))
			elif self.type == self.IS_SDR:
				return info.getInfo(iServiceInformation.sGamma) == 0
			elif self.type == self.IS_HDR:
				return info.getInfo(iServiceInformation.sGamma) == 1
			elif self.type == self.IS_HDR10:
				return info.getInfo(iServiceInformation.sGamma) == 2
			elif self.type == self.IS_HLG:
				return info.getInfo(iServiceInformation.sGamma) == 3
			elif self.type == self.IS_VIDEO_MPEG2:
				return info.getInfo(iServiceInformation.sVideoType) == 0
			elif self.type == self.IS_VIDEO_AVC:
				return info.getInfo(iServiceInformation.sVideoType) == 1
			elif self.type == self.IS_VIDEO_HEVC:
				return info.getInfo(iServiceInformation.sVideoType) == 7
		elif self.PROGRESSIVE:
			return bool(self._getProgressive(info))
		return False

	boolean = property(getBoolean)

	@cached
	def getText(self):
		service = self.source.service
		info = service and service.info()
		if not info:
			return ""
		if self.type == self.XRES:
			return self._getVideoWidthStr(info)
		elif self.type == self.YRES:
			return self._getVideoHeightStr(info)
		elif self.type == self.APID:
			return self.getServiceInfoString(info, iServiceInformation.sAudioPID)
		elif self.type == self.VPID:
			return self.getServiceInfoString(info, iServiceInformation.sVideoPID)
		elif self.type == self.PCRPID:
			return self.getServiceInfoString(info, iServiceInformation.sPCRPID)
		elif self.type == self.PMTPID:
			return self.getServiceInfoString(info, iServiceInformation.sPMTPID)
		elif self.type == self.TXTPID:
			return self.getServiceInfoString(info, iServiceInformation.sTXTPID)
		elif self.type == self.TSID:
			return self.getServiceInfoString(info, iServiceInformation.sTSID)
		elif self.type == self.ONID:
			return self.getServiceInfoString(info, iServiceInformation.sONID)
		elif self.type == self.SID:
			return self.getServiceInfoString(info, iServiceInformation.sSID)
		elif self.type == self.FRAMERATE:
			video_rate = eAVControl.getInstance().getFrameRate(0)
			if not video_rate:
				try:
					video_rate = int(self.getServiceInfoString(info, iServiceInformation.sFrameRate))
				except Exception:
					return "N/A fps"
			return video_rate, lambda x: "%d fps" % ((x + 500) / 1000)
		elif self.type == self.PROGRESSIVE:
			return self._getProgressiveStr(info)
		elif self.type == self.TRANSFERBPS:
			return self.getServiceInfoString(info, iServiceInformation.sTransferBPS, lambda x: "%d kB/s" % (x // 1024))
		elif self.type == self.HAS_HBBTV:
			return info.getInfoString(iServiceInformation.sHBBTVUrl)
		elif self.type == self.FREQ_INFO:
			feinfo = service.frontendInfo()
			if feinfo is None:
				return ""
			feraw = feinfo.getAll(False)
			if feraw is None:
				return ""
			fedata = ConvertToHumanReadable(feraw)
			if fedata is None:
				return ""
			frequency = fedata.get("frequency")
			sr_txt = "Sr:"
			polarization = fedata.get("polarization_abbreviation")
			if polarization is None:
				polarization = ""
			symbolrate = str(int(fedata.get("symbol_rate", 0)))
			if symbolrate == "0":
				sr_txt = ""
				symbolrate = ""
			fec = fedata.get("fec_inner")
			if fec is None:
				fec = ""
			out = "Freq: %s %s %s %s %s" % (frequency, polarization, sr_txt, symbolrate, fec)
			return out
		elif self.type == self.VIDEO_INFO:
			if self._isHDMIIn(info):
				return ""
			progressive = self._getProgressiveStr(info)
			fieldrate = self._getFrameRate(info)
			fieldrate = "%dfps" % ((fieldrate + 500) // 1000,)
			return "%sx%s%s %s" % (self._getVideoWidthStr(info), self._getVideoHeightStr(info), progressive, fieldrate)
		return ""

	text = property(getText)

	@cached
	def getValue(self):
		service = self.source.service
		info = service and service.info()
		if not info:
			return -1

		if self.type == self.XRES:
			video_width = eAVControl.getInstance().getResolutionX(0)
			if not video_width:
				video_width = info.getInfo(iServiceInformation.sVideoWidth)
			return str(video_width)
		elif self.type == self.YRES:
			video_height = eAVControl.getInstance().getResolutionY(0)
			if not video_height:
				video_height = info.getInfo(iServiceInformation.sVideoHeight)
			return str(video_height)
		elif self.type == self.FRAMERATE:
			video_rate = eAVControl.getInstance().getFrameRate(0)
			if not video_rate:
				video_rate = info.getInfo(iServiceInformation.sFrameRate)
			return str(video_rate)
		return -1

	value = property(getValue)

	def changed(self, what):
		if what[0] != self.CHANGED_SPECIFIC or what[1] in self.interesting_events:
			# Only want to update on iPlayableService.evStart
			# if the service is HDMI IN.
			if len(what) > 1 and what[1] == iPlayableService.evStart:
				service = self.source.service
				info = service and service.info()
				if info and not self._isHDMIIn(info):
					return

			Converter.changed(self, what)
