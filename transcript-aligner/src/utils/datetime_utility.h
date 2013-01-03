#ifndef DATETIME_UTILITY_
#define DATETIME_UTILITY_ value

#include <string>
#include <time.h>

#define DEFAULT_DT_FORMAT "%Y-%m-%d %X"

namespace utility
{
    namespace datetime_utility
    {
		// Get current date/time, format is YYYY-MM-DD.HH:mm:ss
		const std::string currentDateTime(const std::string& format = DEFAULT_DT_FORMAT);

		const std::string currentUTCDateTime(const std::string& format = DEFAULT_DT_FORMAT);

		const std::string timestampAdd(const std::string& orgTimeStr, int deltaInSeconds);
		tm str2timestruct(const std::string& str);
		const std::string time2str(tm tstruct);
	}
}

#endif