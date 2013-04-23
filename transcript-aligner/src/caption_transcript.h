#ifndef _CAPTION_H_
#define _CAPTION_H_

#include <iostream>
#include <fstream>
#include <sstream>
#include <string>
#include <vector>
#include <locale>

#include "string_utility.h"

using namespace std;

#define TIMESTAMP           "20121009130004.003"
#define TIMESTAMP_TR        "20120105210015"
#define LEN_TIMESTAMP       18


#define EXCEPTION_NO_FILE    -10

//
// Base class for caption transcript
//
class FileBasedText
{
public:
    FileBasedText()
    {
        text_ = "";
        filename_ = "UNKONW_FILENAME";
    }

    FileBasedText(const string& text, const string& filename)
    {
        text_ = text;
        filename_ = filename;
    }

    FileBasedText(const string& filename)
    {
        this->filename_ = filename;
        
        //Read in files
        ifstream is;
        is.open(filename.c_str());
            
        if (is.good())
        {
            // get length of file:
            is.seekg (0, ios::end);
            int length = is.tellg();
            is.seekg (0, ios::beg);
            
            
            // allocate memory:
            char* buffer = new char[length];
            // read data as a block:
            is.read (buffer,length);
            is.close();   
            text_ = string(buffer);
            delete [] buffer;
        }
        else
        {
            cout << "Cannot open file: " << filename << endl;
            throw EXCEPTION_NO_FILE;
        }
    }

    const string& GetText() const {return text_;}
    const string& GetFilename() const {return filename_;}
protected:
    string text_;
    string filename_;
};

//
// Caption
//
// A single content line in caption
class CaptionLine
{
public:
    CaptionLine(string tag, string timestamp, string content)
    {
        this->tag = tag;
        this->timestamp = timestamp;
        this->content = content;
        isNewFormat_ = false;
    }

    CaptionLine(string tag, string timestamp, string timestamp_end, string content)
    {
        this->tag = tag;
        this->timestamp = timestamp;
        this->timestamp_end = timestamp_end;
        this->content = content;
        isNewFormat_ = true;
    }

    void Print(ostream& os) const
    {
        if (isNewFormat_)
        {
            PrintNewFormat(os);
            return;
        }

        os << tag << "|";
        if (timestamp != "")
        {
            os << timestamp << "|";
        }
        os << content << endl;
    }

    void PrintNewFormat(ostream& os) const
    {
        os << timestamp << "|";
        os << timestamp_end << "|";
        os << tag << "|";
        os << content << endl;
    }

    string tag;
    string timestamp;
    string timestamp_end;
    string content;
    bool isNewFormat_;
};

// A representation of the whole caption file
class Caption : public FileBasedText
{
public:
    Caption()
    {}

    Caption(const string& filename)
        : FileBasedText(filename)
    {
        isInterpolated = false;
        ConvertToWords();
    }
    
    const vector<string>& GetWords() const
    {
        return words_;
    }

    const vector<int>& GetLineLengths() const
    {
        return lineLengths_;
    }

    void PrintToFile(ofstream& fout) const
    {
        if (fout.bad())
            return;
        
        for(int i = 0; i < headerLines.size(); i++)
        {
            fout << headerLines[i] << endl;
        }

        for(int i = 0; i < captionLines.size(); i++)
        {
            captionLines[i].Print(fout);
        }

        for(int i = 0; i < endLines.size(); i++)
        {
            fout << endLines[i] << endl;
        }
    }
private:
    // return the number of words
    const int ConvertToWords()
    {
        BuildLines();
        for(int i = 0; i < captionLines.size(); i++)
        {           
            stringstream ss(captionLines[i].content);
            int numWords = 0;
            while (!ss.eof())
            {
                string word;
                ss >> word;
                words_.push_back(word);
                numWords++;
            }
            lineLengths_.push_back(numWords);
        }
        return words_.size();
    }

    void BuildLines()
    {
        stringstream ss(text_);
        if (ss.bad())
        {
            return;
        }

        string line;
        while(!ss.eof())
        {
            getline(ss, line);
            if (line == "")
                continue;

            if (line[0] >= '0' && line[0] <= '9')
            {                
                string startTime = line.substr(0, LEN_TIMESTAMP);
                string endTime = line.substr(LEN_TIMESTAMP + 1, LEN_TIMESTAMP);

                int tagStart = 2* (LEN_TIMESTAMP + 1);
                string tag_content = line.substr(tagStart);
                size_t tagEnd = tag_content.find('|');
                int contentStart = tagEnd + 1;

                string tag = tag_content.substr(0, tagEnd);

                if (tag == "CC1" || tag == "CC0" || tag == "CCO" || tag == "TR0" || tag == "TR1")
                {
                    // whole line after CC1/CC0
                    string content = tag_content.substr(contentStart);
                    CaptionLine capline(tag, startTime, endTime, content);
                    captionLines.push_back(capline);
                }
            }
            else
            {
                string tag = line.substr(0, 3);
                if (tag == "CC1" || tag == "CC0" || tag == "CCO" || tag == "TR0" || tag == "TR1")
                {
                    // whole line after CC1/CC0
                    string content = line.substr(4);
                    
                    // UTC format timestamp
                    string timestamp;
                    if (tag == "TR0" || tag == "TR1")
                    {
                        isInterpolated = true;
                        timestamp = content.substr(0, string(TIMESTAMP_TR).size());
                    }
                    else
                    {
                        timestamp = content.substr(0, string(TIMESTAMP).size());
                    }

                    // actual caption content
                    content = content.substr(timestamp.size() + 1);
                    if (isInterpolated && content == "(COMMERCIAL BREAK)")
                    {
                        content.clear();
                    }

                    if (captionLines.size() > 0)
                    {
                        (captionLines.end()-1)-> timestamp_end = timestamp;
                    }
                    captionLines.push_back(CaptionLine(tag, timestamp, utility::datetime_utility::timestampAdd(timestamp, 2), content));
                }
                else if (tag == "END")
                {
                    endLines.push_back(line);
                }
                else if (tag == "OTS")
                {
                    continue;   // skip OTS
                }
                else
                {
                    headerLines.push_back(line);
                }
            }
        }

        if (captionLines.size() == 0)
        {
            cout << "WARINING: No CC tags found." << endl;
        }
    }

public:
    vector<string> headerLines;
    vector<CaptionLine> captionLines;
    vector<string> endLines;
    bool isInterpolated;
private:
    vector<string> words_;  // words
    vector<int> lineLengths_;    // the length in words_ of each caption line
};

//
// Transcript
//
class Transcript : public FileBasedText
{
public:
    Transcript()
    {}

    Transcript(const string& filename)
        : FileBasedText(filename)
    {
        ConvertToWords();
    }

    const vector<string>& GetWords() const
    {
        return words_;
    }
private:
    int ConvertToWords()
    {
        stringstream ss(text_);
        bool videoClip = false;
        string line; 
        while (!ss.eof())
        {
            getline (ss, line);
            line = utility::string_utility::trim(line);

            vector<string> words = ProcessLine(line);
            words_.insert(words_.end(), words.begin(), words.end());
        }
        return words_.size();
    }

    vector<string> ProcessLine(const string& line)
    {
        stringstream ss(line);
        vector<string> words;

        string strOrder = "TO ORDER A VIDEO OF THIS TRANSCRIPT";
        if (line.substr(0, strOrder.size()) == strOrder)
        {
            return words;
        }

        while (!ss.eof())
        {
            vector<string> entities = FilterEntities(ss);
            words.insert(words.end(), entities.begin(), entities.end());
        }
        return words;
    }

    vector<string> FilterEntities(stringstream& ss)
    {
        vector<string> words;
        string longWordBuffer;
        string word;
        while (!ss.eof())
        {
            ss >> word;

            // do not do word analysis for lines start with (HEAD), (SUBHEAD), (OBT)
            if (word == "(HEAD)")
            {
                getline(ss, programTitle);
                programTitle = utility::string_utility::trim(programTitle);
                words.clear();
                return words;
            }
            else if (word == "(SUBHEAD)")
            {
                getline(ss, subHeadline);
                words.clear();
                return words;
            }
            else if (word == "(OBT)")
            {
                getline(ss, obtline);
                words.clear();
                return words;
            }

            // Words contain lower case will not be combined,
            // except that end with ':''
            if ((utility::string_utility::has_lower_case(word) || word == "--"))
            {
                if (word == "(voice-over):")
                {
                    ;   // do nothing
                }
                else if(word == "(on")
                {
                    // check if next is "camera)".
                    string nextWord;
                    if (ss >> nextWord)
                    {
                        if (nextWord == "camera):")
                        {
                            word = "(on camera):";
                        }
                        else
                        {
                            words.push_back(word);
                            words.push_back(nextWord);
                        }
                    }
                }
                else
                {
                    break;   
                }
            }

            // For words do not contain lower case letters,
            // it shall be buffered
            // And we treat these punctuations as termination of a long word: 
            //    :  )  .  ?  !
            longWordBuffer.append(word + " ");
            char lastChar = word[word.size() -1];
            if (lastChar == ':' || lastChar == ')' || lastChar == '?' || lastChar == '!')
            {
                if (utility::string_utility::has_no_letter(longWordBuffer))
                {
                    // If the long words has no letter, beak it down into single words.
                    // cout << "LongWord break down: " << longWordBuffer << endl;
                    vector<string> parts = utility::string_utility::split(longWordBuffer, ' ');
                    words.insert(words.end(), parts.begin(), parts.end());
                }
                else
                {                    
                    words.push_back(utility::string_utility::trim_end(longWordBuffer));                    
                }
                longWordBuffer.clear();
            }
            word.clear();
        }

        if (!longWordBuffer.empty())
        {
            vector<string> parts = utility::string_utility::split(longWordBuffer, ' ');
            words.insert(words.end(), parts.begin(), parts.end());            
        }

        if (!word.empty())
        {
            words.push_back(word);
        }
        return words;
    }

public:
    string programTitle;
    string subHeadline;
    string obtline;
private:
    vector<string> words_;
};

#endif