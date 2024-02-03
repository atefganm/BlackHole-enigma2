installdir = $(pkglibdir)/python/Plugins/SystemPlugins

SUBDIRS = PositionerSetup Satfinder CableScan \
	VideoTune Hotplug OpentvZapper \
	DefaultServicesScanner CommonInterfaceAssignment \
	VideoClippingSetup OBH \
	WirelessLan NetworkWizard SABnzbdSetup \
	FastScan SatelliteEquipmentControl DiseqcTester

if HAVE_LIBVUGLES2
SUBDIRS += AnimationSetup
endif

if HAVE_OSDANIMATION
SUBDIRS += AnimationSetup
endif

if DREAMNEXTGEN
SUBDIRS += AmlFRQ VideoEnhancementAML
else
SUBDIRS += VideoEnhancement
endif

if HAVE_FCC
SUBDIRS += FastChannelChange
endif

install_PYTHON = __init__.py
