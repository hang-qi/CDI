// std::string_utility.h
#ifndef _STRING_UTILITY_H_
#define _STRING_UTILITY_H_

#include <string>
#include <vector>

namespace utility
{
    namespace string_utility{

        // Trim all occurance of characters in trimChars from the front of str
        std::string trim_front(const std::string& str, const std::string& trimChars = " ");

        // Trim all occurance of characters in trimChars from the end of str
        std::string trim_end(const std::string& str, const std::string& trimChars = " ");

        // Trim all occurance of characters in trimChars from both front and end of str
        std::string trim(const std::string& str, const std::string& trimChars = " ");

        std::string replace_and_copy(const std::string& str, const std::string& oldStr, const std::string& newStr);

        std::string& replace(std::string& str, const std::string& oldStr, const std::string& newStr);

        std::string to_lower(const std::string& str);

        std::string to_upper(const std::string& str);

        std::vector<std::string> split(const std::string& str, char deliminator);

        bool has_lower_case(const std::string& str);

        bool has_no_letter(const std::string& str);

        std::string to_camal_style(const std::string& str);
    }
}   

#endif