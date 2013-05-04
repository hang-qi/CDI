all:
	g++ -std=c++0x main.cpp TextAnalysis.cpp classifier.cpp utility.cpp segmenter.cpp -o TextAnalysis
	
debug:
	g++ -g -std=c++0x main.cpp TextAnalysis.cpp classifier.cpp utility.cpp segmenter.cpp -o TextAnalysis

update: all
	rsync *.cpp csa@164.67.183.179:/home/csa/CAS2/hangqi/StoryTextInfo/
	rsync *.h csa@164.67.183.179:/home/csa/CAS2/hangqi/StoryTextInfo/
	rsync Makefile csa@164.67.183.179:/home/csa/CAS2/hangqi/StoryTextInfo/