from sys import modules, version_info
from os import path as ospath
from time import time
import socket
import fcntl
import struct

from enigma import getEnigmaVersionString
from Components.SystemInfo import BoxInfo
from Tools.Directories import fileReadLine, fileReadLines

MODULE_NAME = __name__.split(".")[-1]

socfamily = BoxInfo.getItem("socfamily")
MODEL = BoxInfo.getItem("model")


def getVersionString():
	return BoxInfo.getItem("imageversion")


def getImageVersionString():
	return str(BoxInfo.getItem("imageversion"))


def getEnigmaVersionString():
	return str(BoxInfo.getItem("imageversion"))


def getFlashDateString():
	if ospath.isfile('/etc/install'):
		with open("/etc/install", "r") as f:
			return _formatDate(f.read())
	else:
		return _("unknown")


def driversDate():
	return _formatDate(getDriverDate())


def getLastUpdate():
	return _formatDate(getEnigmaVersionString().replace("-", ""))


def _formatDate(Date):
	# expected input = "YYYYMMDD"
	if len(Date) != 8 or not Date.isnumeric():
		return _("unknown")
	from Components.config import config
	return config.usage.date.dateFormatAbout.value % {"year": Date[0:4], "month": Date[4:6], "day": Date[6:8]}


def getGStreamerVersionString():
	try:
		from glob import glob
		gst = [x.split("Version: ") for x in open(glob("/var/lib/opkg/info/gstreamer[0-9].[0-9].control")[0], "r") if x.startswith("Version:")][0]
		return "%s" % gst[1].split("+")[0].split("-")[0].replace("\n", "")
	except:
		return _("unknown")


def getKernelVersionString():
	try:
		return open("/proc/version").read().split(" ", 3)[2].split("-", 1)[0]
	except:
		return _("unknown")


def getIsBroadcom():
	try:
		for x in open("/proc/cpuinfo").readlines():
			x = x.split(": ")
			if len(x) > 1 and (x[0].startswith("Hardware") and x[1].split(" ")[0] == "Broadcom" or x[0].startswith("system type") and x[1].startswith("BCM")):
				return True
	except:
		pass
	return False


def getModelString():
	model = BoxInfo.getItem("machinebuild")
	return model


def getChipsetString():
	if MODEL in ("dm7080", "dm820"):
		chipset = "7435"
	elif MODEL in ("dm520", "dm525"):
		chipset = "73625"
	elif MODEL in ("dm900", "dm920", "et13000"):
		chipset = "7252S"
	elif MODEL in ("hd51", "vs1500", "h7"):
		chipset = "7251S"
	elif MODEL in ("dreamone", "dreamtwo"):
		chipset = "S922X"
	else:
		chipset = fileReadLine("/proc/stb/info/chipset", default=_("Undefined"), source=MODULE_NAME)
		chipset = chipset.lower().replace("\n", "").replace("bcm", "").replace("brcm", "").replace("sti", "")
	return chipset


def getCPUSerial():
	lines = fileReadLines("/proc/cpuinfo", source=MODULE_NAME)
	if lines:
		for line in lines:
			if line[0:6] == "Serial":
				return line[10:26]
	return _("Undefined")


def _getCPUSpeedMhz():
	if MODEL in ('hzero', 'h8', 'sfx6008', 'sfx6018'):
		return 1200
	elif MODEL in ('dreamone', 'dreamtwo', 'dreamseven'):
		return 1800
	elif MODEL in ('vuduo4k',):
		return 2100
	else:
		return 0


def getCPUInfoString():
	cpuCount = 0
	cpuSpeedStr = "-"
	cpuSpeedMhz = _getCPUSpeedMhz()
	processor = ""
	lines = fileReadLines("/proc/cpuinfo", source=MODULE_NAME)
	if lines:
		for line in lines:
			line = [x.strip() for x in line.strip().split(":", 1)]
			if not processor and line[0] in ("system type", "model name", "Processor"):
				processor = line[1].split()[0]
			elif not cpuSpeedMhz and line[0] == "cpu MHz":
				cpuSpeedMhz = float(line[1])
			elif line[0] == "processor":
				cpuCount += 1
		if processor.startswith("ARM") and isfile("/proc/stb/info/chipset"):
			processor = "%s (%s)" % (fileReadLine("/proc/stb/info/chipset", "", source=MODULE_NAME).upper(), processor)
		if not cpuSpeedMhz:
			cpuSpeed = fileReadLine("/sys/devices/system/cpu/cpu0/cpufreq/cpuinfo_max_freq", source=MODULE_NAME)
			if cpuSpeed:
				cpuSpeedMhz = int(cpuSpeed) / 1000
			else:
				try:
					cpuSpeedMhz = int(int(hexlify(open("/sys/firmware/devicetree/base/cpus/cpu@0/clock-frequency", "rb").read()), 16) / 100000000) * 100
				except:
					cpuSpeedMhz = "1500"

		temperature = None
		if isfile("/proc/stb/fp/temp_sensor_avs"):
			temperature = fileReadLine("/proc/stb/fp/temp_sensor_avs", source=MODULE_NAME)
		elif isfile("/proc/stb/power/avs"):
			temperature = fileReadLine("/proc/stb/power/avs", source=MODULE_NAME)
#		elif isfile("/proc/stb/fp/temp_sensor"):
#			temperature = fileReadLine("/proc/stb/fp/temp_sensor", source=MODULE_NAME)
#		elif isfile("/proc/stb/sensors/temp0/value"):
#			temperature = fileReadLine("/proc/stb/sensors/temp0/value", source=MODULE_NAME)
#		elif isfile("/proc/stb/sensors/temp/value"):
#			temperature = fileReadLine("/proc/stb/sensors/temp/value", source=MODULE_NAME)
		elif isfile("/sys/devices/virtual/thermal/thermal_zone0/temp"):
			temperature = fileReadLine("/sys/devices/virtual/thermal/thermal_zone0/temp", source=MODULE_NAME)
			if temperature:
				temperature = int(temperature) / 1000
		elif isfile("/sys/class/thermal/thermal_zone0/temp"):
			temperature = fileReadLine("/sys/class/thermal/thermal_zone0/temp", source=MODULE_NAME)
			if temperature:
				temperature = int(temperature) / 1000
		elif isfile("/proc/hisi/msp/pm_cpu"):
			lines = fileReadLines("/proc/hisi/msp/pm_cpu", source=MODULE_NAME)
			if lines:
				for line in lines:
					if "temperature = " in line:
						temperature = int(line.split("temperature = ")[1].split()[0])

		if cpuSpeedMhz and cpuSpeedMhz >= 1000:
			cpuSpeedStr = _("%s GHz") % format_string("%.1f", cpuSpeedMhz / 1000)
		else:
			cpuSpeedStr = _("%d MHz") % int(cpuSpeedMhz)

		if temperature:
			degree = "\u00B0"
			if not isinstance(degree, str):
				degree = degree.encode("UTF-8", errors="ignore")
			if isinstance(temperature, float):
				temperature = format_string("%.1f", temperature)
			else:
				temperature = str(temperature)
			return (processor, cpuSpeedStr, ngettext("%d core", "%d cores", cpuCount) % cpuCount, "%s%s C" % (temperature, degree))
			#return ("%s %s MHz (%s) %s%sC") % (processor, cpuSpeed, ngettext("%d core", "%d cores", cpuCount) % cpuCount, temperature, degree)
		return (processor, cpuSpeedStr, ngettext("%d core", "%d cores", cpuCount) % cpuCount, "")
		#return ("%s %s MHz (%s)") % (processor, cpuSpeed, ngettext("%d core", "%d cores", cpuCount) % cpuCount)


def getCPUArch():
	if getBoxType() in ("osmio4k", ):
		return "ARM V7"
	if "ARM" in getCPUString():
		return getCPUString()
	return _("Mipsel")


def getCPUString():
	try:
		return [x.split(": ")[1].split(" ")[0] for x in open("/proc/cpuinfo").readlines() if (x.startswith("system type") or x.startswith("model name") or x.startswith("Processor")) and len(x.split(": ")) > 1][0]
	except:
		return _("unavailable")


def getCpuCoresInt():
	try:
		return int(open("/sys/devices/system/cpu/present").read().split("-")[1]) + 1
	except:
		return 0


def getCpuCoresString():
	cores = getCpuCoresInt()
	return {
		0: _("unavailable"),
		1: _("Single core"),
		2: _("Dual core"),
		4: _("Quad core"),
		8: _("Octo core")
	}.get(cores, _("%d cores") % cores)


def _ifinfo(sock, addr, ifname):
	iface = struct.pack('256s', bytes(ifname[:15], 'utf-8'))
	info = fcntl.ioctl(sock.fileno(), addr, iface)
	if addr == 0x8927:
		return ''.join(['%02x:' % ord(chr(char)) for char in info[18:24]])[:-1].upper()
	else:
		return socket.inet_ntoa(info[20:24])


def getIfConfig(ifname):
	ifreq = {"ifname": ifname}
	infos = {}
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	# offsets defined in /usr/include/linux/sockios.h on linux 2.6
	infos["addr"] = 0x8915 # SIOCGIFADDR
	infos["brdaddr"] = 0x8919 # SIOCGIFBRDADDR
	infos["hwaddr"] = 0x8927 # SIOCSIFHWADDR
	infos["netmask"] = 0x891b # SIOCGIFNETMASK
	try:
		for k, v in infos.items():
			ifreq[k] = _ifinfo(sock, v, ifname)
	except:
		pass
	sock.close()
	print("[About] ifreq: ", ifreq)
	return ifreq


def getIfTransferredData(ifname):
	with open("/proc/net/dev", "r") as f:
		for line in f:
			if ifname in line:
				data = line.split("%s:" % ifname)[1].split()
				rx_bytes, tx_bytes = (data[0], data[8])
				return rx_bytes, tx_bytes


def getPythonVersionString():
	return "%s.%s.%s" % (version_info.major, version_info.minor, version_info.micro)


def getEnigmaUptime():
	try:
		seconds = int(time() - ospath.getmtime("/etc/enigma2/profile"))
		return formatUptime(seconds)
	except:
		return ''


def getBoxUptime():
	try:
		with open("/proc/uptime", "rb") as f:
			seconds = int(f.readline().split('.')[0])
		return formatUptime(seconds)
	except:
		return ''


def formatUptime(seconds):
	out = ''
	if seconds > 86400:
		days = int(seconds / 86400)
		out += (_("1 day") if days == 1 else _("%d days") % days) + ", "
	if seconds > 3600:
		hours = int((seconds % 86400) / 3600)
		out += (_("1 hour") if hours == 1 else _("%d hours") % hours) + ", "
	if seconds > 60:
		minutes = int((seconds % 3600) / 60)
		out += (_("1 minute") if minutes == 1 else _("%d minutes") % minutes) + " "
	else:
		out += (_("1 second") if seconds == 1 else _("%d seconds") % seconds) + " "
	return out


# For modules that do "from About import about"
about = modules[__name__]
