#ifndef _PERSON_DETECTOR_H_
#define _PERSON_DETECTOR_H_

#include <string>
#include <unordered_map>
#include <vector>
#include <set>
#include "string_utility.h"

using namespace std;

#define FLG_ON_CAMERA	"(on camera)"
#define FLG_VOICE_OVER	"(voice-over)"

class PersonDetector
{
public:
	PersonDetector() {};
	~PersonDetector() {};

	bool GetSpeakerName(string& word, string& name);
	string GetSPKString(const string& longNameStr);

private:
	bool HasParty(const string& str);
	void GetPartyAndState(const string& str, string& party, string& state);
	string ConvertToCamalStyle(const string& str);
    bool isState(const string& str);

private:
	/* Data members*/
    // person dictionary (last-name, nerString)
    unordered_map<string, string> personDictionary_;

    // Store the name of last speaker, this allows inherit for ON_CAMERA and VOICE_OVER.
    string lastSpeakerName_;
};

#endif