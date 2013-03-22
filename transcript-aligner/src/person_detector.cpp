#include "person_detector.h"

bool PersonDetector::GetSpeakerName(string& word, string& name)
{
    using namespace utility::string_utility;
    string potentialName = trim_end(replace_and_copy(word, FLG_ON_CAMERA, ""));
    potentialName = trim_end(replace(potentialName, FLG_VOICE_OVER, ""));
    if (!has_lower_case(potentialName) && word[word.size()-1] == ':')
    {
        // get rid of ":"
        name = trim(potentialName.substr(0, potentialName.size()-1));
        if (name.empty())
        {
            name = lastSpeakerName_;
            word = name + " " + word;
        }
        else
        {
            lastSpeakerName_ = name;
        }
        return true;
    }
    return false;
}


// Return a SPK string in format of Person=name|Role=role
// Given a longNameString in transcript like "name, role:"
string PersonDetector::GetSPKString(const string& longNameStr)
{   
    using namespace utility::string_utility;

    string name;
    string role;
 
    // erase the ending ':'
    string longNameString = trim_end(longNameStr, ":");

    bool isVoiceOver = (longNameString.find(FLG_VOICE_OVER) != string::npos);
    bool isOnCamera = (longNameString.find(FLG_ON_CAMERA) != string::npos);
    if (isVoiceOver)
    {
        longNameString = trim_end(replace(longNameString, FLG_VOICE_OVER, ""));
    }
    else if(isOnCamera)
    {
        longNameString = trim_end(replace(longNameString, FLG_ON_CAMERA, ""));
    }

    string nerString;
    // deliminated by ',', the first part is NAME, second part is ROLE
    size_t found = longNameString.find(',');
    if (found != string::npos)
    {   // if the person name has a corresponding role, 
        // we store the SPK string in a table with the person's last name as key
        // so that we can look up the table for the full SPK string 
        // when his/her last name appears again.

        name = ConvertToCamalStyle(longNameString.substr(0 ,found));
        role = longNameString.substr(found + 1);
        nerString = "Person=" + name + "|Role=" + trim_front(role);

        // extract last name, and save SPK String into dictionary
        auto nameParts = split(name, ' ');
        string lastPart = nameParts[nameParts.size() - 1];
        string lastName = lastPart;

        // The last part of the name may contains party/state information
        // e.g. MITT ROMNEY (R), JOHN BOEHSPK (R-OH)
        if (HasParty(lastPart))
        {
            name = trim(replace(name, lastPart, ""));
            lastName = nameParts[nameParts.size() - 2];
            
            string party, state;
            GetPartyAndState(lastPart, party, state);           
            
            nerString = "Person=" + name + "|Role=" + trim_front(role) + "|Party=" + party;
            if (!state.empty())
            {
                nerString.append(string("|State=") + state);
            }
        }

        personDictionary_[lastName] = nerString;
    }
    else
    {
        // if the name appears alone without a corresponding role, 
        // we look up the last name in table.
        // If found we use the previously stored SPK string.
        // Otherwise, just display the name as it is.
        auto nameParts = split(ConvertToCamalStyle(longNameString), ' ');
        string lastName = nameParts[nameParts.size() - 1];
        if (personDictionary_.find(lastName) != personDictionary_.end())
        {
            nerString = personDictionary_[lastName];
        }
        else
        {
            nerString = "Person=" + longNameString;
        }
    }

    if (isOnCamera)
    {
        nerString.append("|Type=On-Camera");
    }
    else if(isVoiceOver)
    {
        nerString.append("|Type=Voice-Over");   
    }

    return nerString;
}

// Input str may be like (R), (D), (D-CA), (R-OH)
bool PersonDetector::HasParty(const string& str)
{
    return (str.substr(0,2) == "(R" || str.substr(0,2) == "(D");
}

// Input str may be like (R), (D), (D-CA), (R-OH)
void PersonDetector::GetPartyAndState(const string& str, string& party, string& state)
{
    if (str.substr(0,2) == "(R")
    {
        party = "Republican";
        if (str.size() > 5)
        {
            state = utility::string_utility::to_upper(str.substr(3, 2));
        }
    }
    else if(str.substr(0,2) == "(D")
    {
        party = "Democratic";
        if (str.size() > 5)
        {
            state = utility::string_utility::to_upper(str.substr(3, 2));
        }
    }
}

string PersonDetector::ConvertToCamalStyle(const string& str)
{
    return utility::string_utility::to_camal_style(str);
}