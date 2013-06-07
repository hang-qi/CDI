import sys
sys.path.append('..')
import re
import story
from preprocessing import cleansing
import codecs


def read_in_story(file_name):
    story_num = 0
    stories = []
    insert = False
    with open(file_name, 'r') as f:
        for line in f:
            line = (line[:-1]).lower()
            parts = line.split('|')
            if parts[0] == 'segstart':
                if parts[2] != 'commercial':
                    story_tmp = story.Story()
                    story_tmp.set_start_time(parts[1])
                    story_tmp.set_name(parts[2], parts[3])
                    stories.append(story_tmp)
                    insert = True
            elif parts[0] == 'segend':
                if parts[2] != 'commercial':
                    stories[story_num].set_end_time(parts[1])
                    story_num += 1
                    insert = False
            elif parts[0] == 'cco' and insert is True:
                stories[story_num].add_line(parts[2])
        #print story_num
    return stories


def add_ocr(stories, ocr_file_name):
    with open(ocr_file_name, 'r') as f:
        for line in f:
            if line[0] == '2':
                line = line[:-1]
                parts = line.split('|')
                ocr_results = parts[5].split()
                ocr_time = parts[0]
                if ocr_check(ocr_results):
                    #print parts[5] + '------check ok'
                    tmp = parts[5].lower()
                    ocr_results = tmp.split()
                    story_id = ocr_find_story(ocr_results, ocr_time, stories)
                    if story_id >= 0:
                        stories[story_id].add_ocr_line(parts[5])
                        #print parts[5]
                        #print story_id
    return stories


def ocr_check(ocr_results):
    # The criteria here works for CNN 2008-08 videos
    # Other videos not guaranteed
    for w in ocr_results:
        if not w.isupper():
            a = w[0]
            if not a.isdigit():
                return False
    return True


def ocr_find_story(ocr_results, ocr_time, stories):
    reprog = re.compile(r"""\d\d\d\d\d\d\d\d\d\d(\d\d)(\d\d).+""", re.I | re.X)
    m = reprog.match(ocr_time)
    g = m.groups()
    start_time_minute = int(g[0])
    start_time_second = int(g[1])
    time_range_left_min = max([start_time_minute - 3, 0])
    time_range_right_min = min([start_time_minute + 3, 59])
    ocr_words = cleansing.clean(ocr_results)
    ocr_words = [w for w in ocr_words if len(w) > 2]
    if len(ocr_words) < 1:
        return -1
    overlap = 0
    count = 0
    for story in stories:
        if time_overlap(time_range_left_min, time_range_right_min, start_time_second, story):
            #print count
            p = words_overlap_percentage(ocr_words, story)
            #print ocr_words[0]
            #print p
            if p > overlap:
                overlap = p
                story_id = count
                break
        count += 1
    if overlap >= 1:
        return story_id
    else:
        return -1


def time_overlap(time_range_left_min, time_range_right_min, start_time_second, story):
    left = max([time_range_left_min, story.start_time_minute])
    right = min([time_range_right_min, story.end_time_minute])
    if left <= right:
        return True
    else:
        return False


def words_overlap_percentage(ocr_words, story):
    count = 0
    for w in ocr_words:
        if w in story.line_list:
            count += 1
    #return count/len(ocr_words)
    return count


def save_ocr(stories, story_id):
    for story in stories:
        file_name = 'ocr_result/' + story.start_time_string + '_' + story.story_name + '.ocr'
        with codecs.open(file_name, "w", encoding='ISO-8859-1') as f:
            f.writelines('<story>' + story.story_name + '</story>\n')
            f.writelines('<start>' + story.start_time_string + '</start>\n')
            f.writelines('<end>' + story.end_time_string + '</end>\n')
            for line in story.ocr:
                f.writelines(line + '\n')
    return


def main():
    with open('NewsList.txt', 'r') as f:
        for line in f:
            file_name = line[:-1]
            story_id = 0
            stories = read_in_story('txt/' + file_name + '.txt')
            stories = add_ocr(stories, 'ocr/' + file_name + '.ocr.jpg.ocr')
            save_ocr(stories, story_id)
            print 'Finish ' + file_name
    return

if __name__ == '__main__':
    main()
