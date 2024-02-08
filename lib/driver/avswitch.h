#ifndef __avswitch_h
#define __avswitch_h

#include <lib/base/object.h>
#include <lib/python/connections.h>

class eAVSwitch
{
	static eAVSwitch *instance;
	int m_video_mode;
	bool m_active;
#ifdef SWIG
	eAVSwitch();
	~eAVSwitch();
#endif
protected:
public:
#ifndef SWIG
	eAVSwitch();
	~eAVSwitch();
#endif
	static eAVSwitch *getInstance();
	bool haveScartSwitch();
	int getAspect(int defaultVal = 0, int flags = 0) const;
	int getFrameRate(int defaultVal = 50000, int flags = 0) const;
	bool getProgressive(int flags = 0) const;
	int getResolutionX(int defaultVal = 0, int flags = 0) const;
	int getResolutionY(int defaultVal = 0, int flags = 0) const;
	std::string getVideoMode(const std::string &defaultVal = "", int flags = 0) const;
	std::string getPreferredModes(int flags = 0) const;
	std::string readAvailableModes(int flags = 0) const;
	void setAspect(const std::string &newFormat, int flags = 0) const;
	void setAspectRatio(int ratio);
	void setColorFormat(int format);
	void setInput(int val);
	void setWSS(int val);
	void setVideomode(int mode);
	void setVideoMode(const std::string &newMode, int flags = 0) const;
	void setPolicy43(const std::string &newPolicy, int flags = 0) const;
	void setPolicy169(const std::string &newPolicy, int flags = 0) const;
	void setVideoSize(int top, int left, int width, int height, int flags = 0) const;
	bool isActive();

	enum
	{
		FLAGS_DEBUG = 1,
		FLAGS_SUPPRESS_NOT_EXISTS = 2,
		FLAGS_SUPPRESS_READWRITE_ERROR = 4
	};

};

#endif
