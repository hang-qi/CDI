#include "datetime_utility.h"

namespace utility
{
    namespace datetime_utility
    {
		const std::string currentDateTime(const std::string& format)
		{
		    time_t     now = time(0);
		    char       buf[80];
		    tm* tstruct = localtime(&now);
		    
		    // Visit http://www.cplusplus.com/reference/clibrary/ctime/strftime/
		    // for more information about date/time format
		    strftime(buf, sizeof(buf), format.c_str(), tstruct);

		    return buf;
		}

		const std::string currentUTCDateTime(const std::string& format)
		{
		    time_t     now = time(0);
		    char       buf[80];
		    tm* tstruct = gmtime(&now);
		    // Visit http://www.cplusplus.com/reference/clibrary/ctime/strftime/
		    // for more information about date/time format
		    strftime(buf, sizeof(buf), format.c_str(), tstruct);

		    return buf;
		}

		// 20061003231943.000
		const std::string timestampAdd(const std::string& orgTimeStr, int deltaInSeconds)
		{
			tm t = str2timestruct(orgTimeStr);
			std::string milliseconds = orgTimeStr.substr(15,3);
			t.tm_sec += deltaInSeconds;
			std::string newTimeString = time2str(t) + "." + milliseconds;
			return newTimeString;
		}

		// 20061003231943
		tm str2timestruct(const std::string& str)
		{
			tm t;
			t.tm_sec = atoi(str.substr(12,2).c_str());
			t.tm_min = atoi(str.substr(10, 2).c_str());
			t.tm_hour = atoi(str.substr(8, 2).c_str());
			t.tm_mday = atoi(str.substr(6, 2).c_str());
			t.tm_mon = atoi(str.substr(4, 2).c_str()) - 1;
			t.tm_year = atoi(str.substr(0, 4).c_str()) - 1900;
			return t;
		}

		// 20061003231943
		const std::string time2str(tm tstruct)
		{
			char buf[80];
			strftime(buf, sizeof(buf), "%Y%m%d%H%M%S", &tstruct);
			return buf;
		}
	}
}