all:
	g++ -std=c++0x main.cpp TextAnalysis.cpp classifier.cpp utility.cpp segmenter.cpp -o TextAnalysis
	
debug:
	g++ -g -std=c++0x main.cpp TextAnalysis.cpp classifier.cpp utility.cpp segmenter.cpp -o TextAnalysis

update: all
	rsync *.cpp csa@ca:/home/csa/CAS2/hangqi/StoryTextInfo/
	rsync *.h csa@ca:/home/csa/CAS2/hangqi/StoryTextInfo/
	rsync Makefile csa@ca:/home/csa/CAS2/hangqi/StoryTextInfo/