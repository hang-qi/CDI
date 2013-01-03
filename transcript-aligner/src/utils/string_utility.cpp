#include "string_utility.h"

namespace utility
{
    namespace string_utility
    {
        // Trim all occurance of characters in trimChars from the front of str
        std::string trim_front(const std::string& str, const std::string& trimChars)
        {
            int i = 0;
            for (i = 0; i < str.size(); i++)
            {
                bool found = false;
                for (int j = 0; j < trimChars.size(); j++)
                {
                    if (str[i] == trimChars[j])
                        found = true;
                }
                if (found == false)
                    break;
            }
            return str.substr(i);
        }

        // Trim all occurance of characters in trimChars from the end of str
        std::string trim_end(const std::string& str, const std::string& trimChars)
        {
            int i = 0;
            for (i = str.size()-1; i >= 0; i--)
            {
                bool found = false;
                for (int j = 0; j < trimChars.size(); j++)
                {
                    if (str[i] == trimChars[j])
                        found = true;
                }
                if (found == false)
                    break;
            }
            return str.substr(0, i+1);
        }

        // Trim all occurance of characters in trimChars from both front and end of str
        std::string trim(const std::string& str, const std::string& trimChars)
        {
            return trim_end(trim_front(str, trimChars), trimChars);
        }

        std::string replace_and_copy(const std::string& str, const std::string& oldStr, const std::string& newStr)
        {
            std::string result = str;
            result = replace(result, oldStr, newStr);
            return result;
        }

        std::string& replace(std::string& str, const std::string& oldStr, const std::string& newStr)
        {
            if(oldStr.empty())
            {
                return str;
            }
            size_t start_pos = 0;
            while((start_pos = str.find(oldStr, start_pos)) != std::string::npos)
            {
                str.replace(start_pos, oldStr.length(), newStr);
                start_pos += newStr.length(); // In case 'to' contains 'from', like replacing 'x' with 'yx'
            }
            return str;
         }

        std::string to_lower(const std::string& str)
        {
            std::string result = str;
            for (auto c = result.begin(); c != result.end(); ++c)
            {
                *c = tolower(*c);
            }
            return result;
        }

        std::string to_upper(const std::string& str)
        {
            std::string result = str;
            for (auto c = result.begin(); c != result.end(); ++c)
            {
                *c = toupper(*c);
            }
            return result;
        }

        std::vector<std::string> split(const std::string& str, char deliminator)
        {
            std::vector<std::string> parts;         
            size_t begin = 0;
            size_t found = str.find(deliminator, begin);
            while (found != std::string::npos)
            {
                parts.push_back(str.substr(begin, found - begin));
                begin = found + 1;
                found = str.find(deliminator, begin);
            }
            parts.push_back(str.substr(begin, str.length() - begin));
            return parts;
        }


        bool has_lower_case(const std::string& str)
        {
            for (int i = 0; i < str.size(); i++)
            {
                if (str[i] >= 'a' && str[i] <= 'z')
                {
                    return true;
                }
            }
            return false;
        }

        bool has_no_letter(const std::string& str)
        {
            char c;
            for (int i = 0; i < str.size(); i++)
            {
                c = tolower(str[i]);
                if (c >= 'a' && c <= 'z')
                {
                    return false;
                }
            }
            return true;
        }

        std::string to_camal_style(const std::string& str)
        {
            std::string result = to_lower(str);

            char preCh = ' ';
            char curCh = ' ';
            auto current = result.begin();
            while(current != result.end())
            {
                curCh = *current;
                if (curCh >= 'a' && curCh <= 'z')
                {
                    if (preCh == ' ' || preCh == '\'' || preCh == '('
                            || preCh == '.' )
                    {
                        // convert to Uppercase
                        *current = toupper(curCh);
                    }
                }
                preCh = curCh;
                current++;
            };
            return result;
        }
    }
} 