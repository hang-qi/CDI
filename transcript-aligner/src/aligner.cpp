// Implementation of Aligner
#include "aligner.h"
#include <assert.h>

// Returns the new caption object after alignment
const AlignmentResult Aligner::DoAlign()
{
    // reserve spaces
    captionWords_.reserve(pCaption_->GetWords().size() + 1);
    transcriptWords_.reserve(pTranscript_->GetWords().size() + 1);

    captionWords_.push_back("");
    transcriptWords_.push_back("");

    captionWords_.insert(captionWords_.end(),
        pCaption_->GetWords().begin(),
        pCaption_->GetWords().end());
    transcriptWords_.insert(transcriptWords_.end(),
        pTranscript_->GetWords().begin(),
        pTranscript_->GetWords().end());

    InitTable();

    cout << "Start comparing..." << endl;
    cout << "    # of words in caption: " << (captionWords_.size() - 1) << endl;
    cout << "    # of words in transcript: " << (transcriptWords_.size() - 1) << endl;
    cout << "    Compare score: " << Compare() << endl;

    cout << "Start reconstructing and restoring timestamps..." << endl; 
    Caption caption = ReconstructAndAlign();
    DeleteTable();
    cout << "  " << endl;
    
    cout << "Reconstruction done." << endl;
    // Print Summaries
    counter_.PrintSummary(cout);

    // Percentage of same
    double percentageOfSame = (double) counter_.num_same / (transcriptWords_.size() - 1);
    cout.precision(4);    
    cout << "    Percentage of same:  " << percentageOfSame << " (# same / # in transcript)" << endl;    
    if (percentageOfSame < 0.4)
    {
        cout << "[MATCHING ALERT] Same percentage drops off 0.4.  Caption: "
             <<  pCaption_->GetFilename() << " Transcript: " << pTranscript_->GetFilename() << endl;
    }

    AlignmentResult result;
    result.alignedCaption = caption;
    result.percentageOfSame = percentageOfSame;
    return result;
}

const Caption Aligner::ReconstructAndAlign()
{
    resultLineLengths_ = pCaption_->GetLineLengths();
    iCurrentLine_ = 0;
    if (resultLineLengths_.size() > 0)
    {
        currentLineBoundary_ = resultLineLengths_[iCurrentLine_];
        Reconstruct(captionWords_.size() -1, transcriptWords_.size() -1);
    }
    else
    {
        throw EXCEPTION_NO_FILE;
    }
    return BuildTimeAlignedCaption();
}

// Reconstruct the aligned text by recursively tracking back the table
void Aligner::Reconstruct(int i, int j)
{    
    if (table_[i][j].parent == -1){
        return;
    }

    if (table_[i][j].parent == MATCH)
    {
        Reconstruct(i-1, j-1);
        PerformMatch(i, j);
        return;
    }   
    if (table_[i][j].parent == INSERT)
    {
        Reconstruct(i, j-1);
        PerformInsert(i, j);
        return;
    }
    if (table_[i][j].parent == DELETE)
    {
        Reconstruct(i-1, j);
        PerformDelete(i, j);
        return;
    }
}

bool Aligner::isSegmentMark(const string& word)
{
    if (word == BEGIN_VIDEO_CLIP || word == END_VIDEO_CLIP 
         || word == BEGIN_VIDEOTAPE || word == END_VIDEOTAPE
         || word == BEGIN_VIDEO_TAPE || word == END_VIDEO_TAPE
         || word == BEGIN_AUDIO_CLIP || word == END_AUDIO_CLIP
         || word == COMMERCIAL_BREAK || word == COMMERCIAL_END)
    {
        return true;
    }
    else if (word[0] == '(' and word[word.size()-1] == ')')
    {
        return true;
    }
    return false;
}

const Caption Aligner::BuildTimeAlignedCaption()
{
    Caption tptCaption;
    tptCaption.captionLines.reserve(pCaption_->captionLines.size());

    assert(pCaption_->GetLineLengths().size() == resultLineLengths_.size());

    string currentLineContent = "";
    string postFlagLineContent = "";    // for any content after flag tags, but in the same line

    string word;
    auto itWord = resultWords_.begin();

    string previousSegType = "";
    int prev_seg_idx = -1;
    int prev_ner_idx = -1;
    int prev_clip_idx = -1;

    if (!pCaption_->isInterpolated)
    {
        // First Segmentation
        CaptionLine introSeg("SEG",
                          pCaption_->captionLines[0].timestamp,
                          "TO_BE_FILLED",
                         "Type=Intro");
        tptCaption.captionLines.push_back(introSeg);        
        prev_seg_idx = tptCaption.captionLines.size() - 1;
        // string previousSegType = "Intro";
    }

    for (int i = 0; i < resultLineLengths_.size(); i++)
    {
        // For each line in caption, we want to find aligend text.
        // However, one line may contains several sublines deliminated by
        // deliminators, such as BEGIN VEDIO CLIP, END VEDIO CLIP, COMMERCIAL BREAK.
        vector<string> sublines;
        currentLineContent = "";
        int numWordsInLine = 0;        
        while (numWordsInLine < resultLineLengths_[i])
        {
            word = *itWord;
            string name;

            if (isSegmentMark(word))
            {
                if (!currentLineContent.empty())
                {
                    sublines.push_back(currentLineContent);
                }
                currentLineContent.clear();
                sublines.push_back(word);  // segment mark as a single line
            }
            else if (personDetector_.GetSpeakerName(word, name))
            {
                if (currentLineContent !=  ">> " && currentLineContent !=  ">>> ")
                {
                    // Start a new line when a new person speaks.
                    // Add >> before names if does not exist.
                    sublines.push_back(currentLineContent);
                    currentLineContent.clear();
                    currentLineContent.append(">> ");
                }

                // create a line flaged with "SPK" for further processing into SPK line.
                string lineSPK = string("(SPK)").append(word);
                sublines.push_back(lineSPK);

                currentLineContent.append(name + ": ");
            }
            else if (word == CHEVRON_STORY)
            {
                if (currentLineContent.length() >= 3 && currentLineContent.substr(0,3) == ">> ")
                {
                    sublines.insert(sublines.end()-1, CHEVRON_STORY);
                    currentLineContent.insert(0, ">");
                }
                else
                {
                    sublines.push_back(CHEVRON_STORY);
                    currentLineContent.append(word + " ");
                }
            }
            else if (word == CHEVRON)
            {
                ; // nothing
            }
            else
            {
                currentLineContent.append(word + " ");
            }

            numWordsInLine++;
            itWord++;
        }
        if (!currentLineContent.empty())
        {
            sublines.push_back(currentLineContent);
        }
        currentLineContent = "";

        // Create caption lines
        vector<CaptionLine> linesBuffer;
        string currentTimestamp = pCaption_->captionLines[i].timestamp;
        string currentTimestamp_end = pCaption_->captionLines[i].timestamp_end;
        string previousTimestamp = i > 0 ? pCaption_->captionLines[i-1].timestamp : "";
        for (int k = 0; k < sublines.size(); k++)
        {
            if (utility::string_utility::trim(sublines[k]).empty())
            {
                continue;
            }
            else if (sublines[k].substr(0,5) == "(SPK)") //CHEVRON
            {
                if (pCaption_->isInterpolated && previousSegType == "Commercial")
                {
                    /*
                    CaptionLine line("SegEnd",
                        currentTimestamp,
                        "Type=Commercial");
                    linesBuffer.push_back(line);
                    previousSegType = "";
                    */
                }

                CaptionLine line("NER_01",
                                currentTimestamp,
                                "TO_BE_FILLED",
                                personDetector_.GetSPKString(sublines[k].substr(5)));
                linesBuffer.push_back(line);
                //tptCaption.captionLines.push_back(line);
            }
            else if (sublines[k] == CHEVRON_STORY)
            {
                /*if(previousSegType != "")
                {
                    CaptionLine segEnd("SegEnd",
                                currentTimestamp,
                                "Type=" + previousSegType);
                    linesBuffer.push_back(segEnd);
                    //tptCaption.captionLines.push_back(segEnd);
                }*/

                CaptionLine segStart("SEG",
                                currentTimestamp,
                                "TO_BE_FILLED",
                                "Type=Story");
                linesBuffer.push_back(segStart);
                //tptCaption.captionLines.push_back(segStart);
                previousSegType = "Story";
            }
            else if (sublines[k] == BEGIN_VIDEO_CLIP
                         || sublines[k] == BEGIN_VIDEOTAPE
                         || sublines[k] == END_VIDEO_TAPE)
            {
                CaptionLine line("CLIP",
                        currentTimestamp,
                        "TO_BE_FILLED",
                        "Type=Video");
                linesBuffer.push_back(line);
                //tptCaption.captionLines.push_back(line);
            }
            else if (sublines[k] == END_VIDEO_CLIP
                         || sublines[k] == END_VIDEOTAPE
                         || sublines[k] == END_VIDEO_TAPE)
            {
                /*CaptionLine line("EndClip",
                        currentTimestamp,
                        "Type=Video");
                linesBuffer.push_back(line);*/
                //tptCaption.captionLines.push_back(line);
            }
            else if (sublines[k] == BEGIN_AUDIO_CLIP)
            {
                /*CaptionLine line("StartClip",
                        currentTimestamp,
                        "Type=Audio");
                linesBuffer.push_back(line);*/
                //tptCaption.captionLines.push_back(line);
            }
            else if (sublines[k] == END_AUDIO_CLIP)
            {
                /*CaptionLine line("EndClip",
                        currentTimestamp,
                        "Type=Audio");
                linesBuffer.push_back(line);*/
                //tptCaption.captionLines.push_back(line);
            }
            else if (sublines[k] == COMMERCIAL_BREAK)
            {
                /*if(previousSegType != "")
                {
                    CaptionLine segEnd("SegEnd",
                                currentTimestamp,
                                "Type=" + previousSegType);
                    linesBuffer.push_back(segEnd);
                    //tptCaption.captionLines.push_back(segEnd);
                }*/

                CaptionLine line("SEG",
                        currentTimestamp,
                        "TO_BE_FILLED",
                        "Type=Commercial");
                linesBuffer.push_back(line);    

                if (k+1 < sublines.size() && sublines[k+1] == COMMERCIAL_END
                    && !pCaption_->isInterpolated)
                {// Adjust start time for empty commercials
                    for (int k = 0; k < linesBuffer.size(); k++)
                    {
                        linesBuffer[k].timestamp = utility::datetime_utility::timestampAdd(previousTimestamp, 1);
                    }
                }               

                previousSegType = "Commercial";
            }
            else if (sublines[k] == COMMERCIAL_END)
            {
                ;// do nothing
            }
            else
            {
                // Create separate lines for flags      
                CaptionLine line(pCaption_->captionLines[i].tag,
                            currentTimestamp,
                            currentTimestamp_end,
                            sublines[k]);
                linesBuffer.push_back(line);
                //tptCaption.captionLines.push_back(line);
            }
        }
        for (int k = 0; k < linesBuffer.size(); k++)
        {
            tptCaption.captionLines.push_back(linesBuffer[k]);
            if (linesBuffer[k].tag == "SEG")
            {
                // Terminate previous SEG, NER, CLIP
                AddEndTimeToTag(tptCaption.captionLines, prev_seg_idx, linesBuffer[k].timestamp);
                prev_seg_idx = tptCaption.captionLines.size() -1;

                AddEndTimeToTag(tptCaption.captionLines, prev_ner_idx, linesBuffer[k].timestamp);
                prev_ner_idx = -1;

                AddEndTimeToTag(tptCaption.captionLines, prev_clip_idx, linesBuffer[k].timestamp);
                prev_clip_idx = -1;
            }
            else if (linesBuffer[k].tag == "CLIP")
            {
                // terminate previous CLIP, NER
                AddEndTimeToTag(tptCaption.captionLines, prev_clip_idx, linesBuffer[k].timestamp);
                prev_clip_idx = tptCaption.captionLines.size() -1;

                AddEndTimeToTag(tptCaption.captionLines, prev_ner_idx, linesBuffer[k].timestamp);
                prev_ner_idx = -1;
            }
            else if (linesBuffer[k].tag == "NER_01")
            {
                AddEndTimeToTag(tptCaption.captionLines, prev_ner_idx, linesBuffer[k].timestamp);
                prev_ner_idx = tptCaption.captionLines.size() -1;

                if (pCaption_->isInterpolated 
                    && prev_seg_idx != -1 
                    && tptCaption.captionLines[prev_seg_idx].content == "Type=Commercial")
                {
                    AddEndTimeToTag(tptCaption.captionLines, prev_seg_idx, linesBuffer[k].timestamp);
                    prev_seg_idx = -1;
                }
            }            
        }
    }

    AddEndTimeToTag(tptCaption.captionLines, prev_seg_idx, tptCaption.captionLines.back().timestamp_end);
    AddEndTimeToTag(tptCaption.captionLines, prev_ner_idx, tptCaption.captionLines.back().timestamp_end);
    AddEndTimeToTag(tptCaption.captionLines, prev_clip_idx, tptCaption.captionLines.back().timestamp_end);

    tptCaption.headerLines = pCaption_->headerLines;
    tptCaption.endLines = pCaption_->endLines;

    // Create meta data lines into header section of the new caption
    tptCaption.headerLines.push_back("TTL|" + utility::string_utility::trim(pTranscript_->programTitle));
    tptCaption.headerLines.push_back("OBT|" + utility::string_utility::trim(pTranscript_->obtline));
    tptCaption.headerLines.push_back("RUN|" + utility::datetime_utility::currentUTCDateTime("%Y%m%d%H%M")
                                    + "|PTAG=NER_01|Source_Program=transcript-aligner|Source_Person=Hang Qi");
    tptCaption.headerLines.push_back("NER_01|" + utility::datetime_utility::currentUTCDateTime("%Y%m%d%H%M")
                                    + "|Source_Program=transcript-aligner|Source_Person=Hang Qi");
    
    return tptCaption;
}

void Aligner::AddEndTimeToTag(vector<CaptionLine>& lines, int index, string timestamp_end)
{
    if (index != -1)
    {
        assert(lines[index].timestamp_end == "TO_BE_FILLED");
        lines[index].timestamp_end = timestamp_end;
    }
}

int Aligner::Compare()
{
    int opt[3];
    int i = 0, j = 0;
    for (i = 1; i < captionWords_.size(); ++i)
    {
        for (j = 1; j < transcriptWords_.size(); ++j)
        {
            opt[MATCH] = table_[i-1][j-1].cost
                            + MatchCost(captionWords_[i], transcriptWords_[j]);
            opt[INSERT] = table_[i][j-1].cost
                            + InsertCost(transcriptWords_[j]);
            opt[DELETE] = table_[i-1][j].cost
                            + DeleteCost(captionWords_[i], transcriptWords_[j]);

            table_[i][j].cost = opt[MATCH];
            table_[i][j].parent = MATCH;

            // DELETE
            if (opt[DELETE] < table_[i][j].cost)
            {
                table_[i][j].cost = opt[DELETE];
                table_[i][j].parent = DELETE;
            }
            // INSRT
            if (opt[INSERT] < table_[i][j].cost)
            {
                table_[i][j].cost = opt[INSERT];
                table_[i][j].parent = INSERT;
            }
        }
    }

    return GoalCellCost();
}

int Aligner::MatchCost(const string& cap, const string& trans)
{
    string str1 = utility::string_utility::replace_and_copy(cap, "\"", "");
    string str2 = utility::string_utility::replace_and_copy(trans, "\"", "");

    if (str2 == COMMERCIAL_BREAK || str2 == CHEVRON_STORY || str2 == CHEVRON)
    {
        return 100;   // nothing can be matched with COMMERCIAL_BREAK or CHEVORON
    }

    if (str1.size() != str2.size())
    {
        return 3;   // not match: cost 3 for different length substitution. insert and delete are prefered.
    }

    for (auto c1 = str1.begin(), c2 = str2.begin(); c1 != str1.end(); ++c1, ++c2)
    {
        if (tolower(*c1) != tolower(*c2))
            return 2;   // not match: cost 2 for substitution
    }
    return 0;   // match: cost 0
}

int Aligner::InsertCost(const string& trans)
{
    if (trans == COMMERCIAL_BREAK)
        return 0;
    return 1;
}

int Aligner::DeleteCost(const string& cap, const string& trans)
{
    if (trans == COMMERCIAL_BREAK)
    {
        // Given the transcript saying (COMMERCIAL_BREAK),
        // we mark commercial text as delete.
        // In order to keep commercial text, we keep the text in PerformDelete().
        // See PerformDelete() for details.
        return 0;
    }
    if (cap == CHEVRON_STORY || cap == CHEVRON)
    {
        return 0;
    }
    return 1;
}

void Aligner::PerformMatch(int i, int j)
{
    assert(i < captionWords_.size() && j < transcriptWords_.size());
    // use the same word will not affect the timepoint offset
    if (i == currentLineBoundary_ && iCurrentLine_ != resultLineLengths_.size()-1)
    {
        iCurrentLine_++;
        currentLineBoundary_ += resultLineLengths_[iCurrentLine_];
    }

    // keep ">>" and ">>>"
    assert(captionWords_[i] != CHEVRON);
    assert(captionWords_[i] != CHEVRON_STORY);

    // always use words from transcript    
    resultWords_.push_back(transcriptWords_[j]);
    counter_.num_match++;

    if (utility::string_utility::to_lower(captionWords_[i]) == 
            utility::string_utility::to_lower(transcriptWords_[j]))
    {
        counter_.num_same++;
    }
}

void Aligner::PerformInsert(int i, int j)
{
    assert(i < captionWords_.size());
    assert(j < transcriptWords_.size());
    assert(iCurrentLine_ < resultLineLengths_.size());

    if (j != 0 && transcriptWords_[j-1] == COMMERCIAL_BREAK)
    {
        resultWords_.push_back(COMMERCIAL_END);
        resultLineLengths_[iCurrentLine_]++;
    }
    // insert one word, timepoint offset shall be increased by 1
    resultWords_.push_back(transcriptWords_[j]);
    resultLineLengths_[iCurrentLine_]++;
    counter_.num_insert++;
}

void Aligner::PerformDelete(int i, int j)
{
    assert(i < captionWords_.size() && j < transcriptWords_.size());


    if (i == currentLineBoundary_  && iCurrentLine_ != resultLineLengths_.size()-1)
    {
        iCurrentLine_++;
        currentLineBoundary_ += resultLineLengths_[iCurrentLine_];
    }

    // If current is commercial, do not delete words from commercials.
    // So use the same word will not affect the timepoint offset
    if (transcriptWords_[j] == COMMERCIAL_BREAK)
    {
        resultWords_.push_back(captionWords_[i]);
        counter_.num_keeped++;
        return;
    }

    if (captionWords_[i] == CHEVRON_STORY)
    {
        resultWords_.push_back(CHEVRON_STORY);
        counter_.num_keeped++;
        return;
    }

    // this is equivalent to delete a word from caption
    // timepoint offset shall be decrease by 1
    resultLineLengths_[iCurrentLine_]--;
    counter_.num_delete++;
    return;
}

//////////////////////////

void OutputTPTFile(const string& filename, const Caption& alignedCaption)
{
    ofstream ofile;
    ofile.open(filename.c_str());
    if (ofile.good())
    {
        alignedCaption.PrintToFile(ofile);
        ofile.close();
    }
}

int Align(const string& captionFilename, const string& transcriptFilename)
{
    cout << "Aligner started." << endl;
    cout << ">    Caption file: " << captionFilename << endl;
    cout << "> Transcript file: " << transcriptFilename << endl;
    
    try
    {
        // Read caption file and transcript file (raw text with HTML tags eliminated)
        const Caption caption(captionFilename);
        const Transcript transcript(transcriptFilename);

        // Begin align
        Aligner aligner(&caption, &transcript);
        AlignmentResult alignmentResult = aligner.DoAlign();
        
        // Output TPT file
        string outputFilename = utility::string_utility::replace_and_copy(transcriptFilename,".rawtxt", ".tpt");
        cout << "> Output TPT file: " << outputFilename << endl;
        OutputTPTFile(outputFilename, alignmentResult.alignedCaption);
    }
    catch(int e)
    {
        if (e == EXCEPTION_NO_FILE)
        {
            cout << "ERROR: The input caption file may be empty." << endl;
            return -1;
        }
    }
    return 0;
}

int AlignBestOne(const string& transcriptFilename, const vector<string>& captionCandidates)
{
    int num_candidates = captionCandidates.size();
    cout << "Comparing against " << num_candidates << " candidates..." << endl;
    vector<AlignmentResult> alignmentResults;

    // Compare for each candidate
    for (int i = 0; i < num_candidates; i++)
    {
        cout << "Candidiate #" << i+1 << ": " << endl;
        try
        {
            const Caption caption = Caption(captionCandidates[i]);
            const Transcript transcript = Transcript(transcriptFilename);
        
            // Begin align
            Aligner aligner(&caption, &transcript);
            alignmentResults.push_back(aligner.DoAlign());
        }
        catch(int e)
        {
            if (e == EXCEPTION_NO_FILE)
            {
                cout << "  Candidate not found." << endl;
                alignmentResults.push_back(AlignmentResult());
            }
        }
    }
    cout << "Comparing finished." << endl;

    // Find the candidate with the highest percentage of same
    int bestIndex = 0;
    double bestPercentage = 0;
    for (int i = 0; i < num_candidates; i++)
    {
        if (alignmentResults[i].percentageOfSame > bestPercentage)
        {
            bestIndex = i;
            bestPercentage = alignmentResults[i].percentageOfSame;
        }
        else if (alignmentResults[i].percentageOfSame == bestPercentage && bestPercentage != 0)
        {
            cout << "  [MATCHING DUPLICATE] Candidate " << captionCandidates[i] 
                << " and " << captionCandidates[bestIndex] << endl;
        }
    }

    // Output the best match.
    if (bestPercentage == 0)
    {
        cout << "[MATCHING FAILED] Cannot find any matching caption." << endl;
    }
    else if (bestPercentage < 0.4)
    {
        cout << "[MATCHING FAILED] No candidate produces Same Percentage over 0.4." << endl;
    }
    else
    {
        cout << "[MATCHING FOUND] Best Matching " << captionCandidates[bestIndex] <<
        " with percentage " << bestPercentage << endl;
        cout << "Reconstruct best alignment." << endl;

        // Output TPT file
        string outputFilename = utility::string_utility::replace_and_copy(transcriptFilename,".rawtxt", ".tpt");
        cout << "> Output TPT file: " << outputFilename << endl;
        OutputTPTFile(outputFilename, alignmentResults[bestIndex].alignedCaption);

        return 0;
    }
    return 0;
}

int main(int argc, char* argv[])
{
    if (argc == 2 && string(argv[1]) == "debug")
    {
        string captionFilename = "../../../data/2013-04-15_1500_US_CNN_Newsroom.txt";
        string transcriptFilename = "../../../data/2013-04-15_1500_US_CNN_Newsroom.rawtxt";
        return Align(captionFilename, transcriptFilename);
    }

    if (argc < 3)
    {
        cout << "Usage 1: > ./aligner captionFilename.txt transcriptFilename.rawtxt" << endl;
        cout << "Usage 2: > ./aligner transcriptFilename.rawtxt captionFilename1.txt captionFilename2.txt ..." << endl;
        return 0;
    }
    else if(argc == 3)
    {
        string captionFilename = argv[1];
        string transcriptFilename = argv[2];
        return Align(captionFilename, transcriptFilename);
    }
    else
    {
        string transcriptFilename = argv[1];
        vector<string> captionCandidates;
        for (int i = 2; i < argc; i++)
        {
            captionCandidates.push_back(argv[i]);
        }
        return AlignBestOne(transcriptFilename, captionCandidates);
    }
    return -1;
}