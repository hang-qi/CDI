import sys
sys.path.append('..')
import re
import story
import cleansing
import codecs
import pdb


def read_in_story(file_name):
    story_num = 0
    stories = []
    insert = False
    with open(file_name, 'r') as f:
        for line in f:
            line = (line[:-1]).lower()
            if len(line) < 1:
                continue
            if line[0] == '<':
                if line[1:6] == 'story':
                    story_tmp = story.Story()
                    story_name = line.split('>')[-2].split('<')[0]
                    story_name = story_name.replace(' / ', '__')
                    story_tmp.set_name(story_name)
                    stories.append(story_tmp)
                    insert = True
                if line[1:6] == 'start': 
                    start_time = line.split('>')[-2].split('<')[0]
                    story_tmp.set_start_time(start_time)
                if line[1:4] == 'end':
                    end_time = line.split('>')[-2].split('<')[0]
                    stories[story_num].set_end_time(end_time)
                    insert = False
                    story_num += 1
            else:
                if len(line) < 2:
                    continue
                if len(line.split(';')) == 3:
                    continue
                if insert is True:
                    stories[story_num].add_line(line)
    print story_num
    #pdb.set_trace()
    return stories


def add_ocr(stories, ocr_file_name):
    with open(ocr_file_name, 'r') as f:
        for line in f:
            if line[0] == '2':
                line = line[:-1]
                parts = line.split('|')
                #ocr_results = parts[5].split()
                ocr_time = parts[0]
                if ocr_check(parts[5], parts[4]):
                    #print parts[5] + '------check ok'
                    #pdb.set_trace()
                    tmp = parts[5].lower()
                    ocr_results = tmp.split()
                    story_id = ocr_find_story(ocr_results, ocr_time, stories)
                    if story_id >= 0:
                        stories[story_id].add_ocr_line(parts[5])
                        #print parts[5]
                        #print story_id
    return stories


def ocr_check(ocr_line, ocr_location):
    # The criteria here works for CNN 2008-08 videos
    # Captions are upper letters
    # Other videos are not guaranteed

    # word check
    ocr_line = ocr_line.strip()
    ocr_results = ocr_line.split()
    if len(ocr_results) < 2:
        return False
    for w in ocr_results:
        if not w.isupper():
            a = w[0]
            if not a.isdigit():
                return False
    # location check
    caption_location = [205.0, 600.0, 745.0, 685.0]
    ocr_location = ocr_location.strip()
    locations = ocr_location.split()
    if overlap_region_percentage(float(locations[0]), float(locations[1]), float(locations[0])+float(locations[2]), float(locations[1])+float(locations[3]), caption_location) < 0.5:
        return False
    return True


def overlap_region_percentage(x1_left, y1_left, x1_right, y1_right, region2):
    # x1: location to be checked
    # return: overlapped region / x1 region
    x2_left = region2[0]
    y2_left = region2[1]
    x2_right = region2[2]
    y2_right = region2[3]

    x_left = max(x1_left, x2_left)
    y_left = max(y1_left, y2_left)
    x_right = min(x1_right, x2_right)
    y_right = min(y1_right, y2_right)

    if (x_left < x_right) and (y_left < y_right):
        area = float(x_right-x_left)*float(y_right-y_left)
        area_x1 = float(x1_right-x1_left)*float(y1_right-y1_left)
        return float(area)/float(area_x1)
    else:
        return 0


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
    for i, story in enumerate(stories):
        if time_overlap(time_range_left_min, time_range_right_min, start_time_second, story):
            #print count
            p = words_overlap_percentage(ocr_words, story)
            #print ocr_words[0]
            #print p
            if p > overlap:
                overlap = p
                story_id = i
    if overlap >= 0.4:
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
    return float(count)/float(len(ocr_words))
    #return count


def save_ocr(stories):
    for story in stories:
        file_name = 'ocr_result/' + story.start_time_string + '_' + story.story_name + '.ocr'
        print(file_name)
        with codecs.open(file_name, "w", encoding='ISO-8859-1') as f:
            f.writelines('<story>' + story.story_name + '</story>\n')
            f.writelines('<start>' + story.start_time_string + '</start>\n')
            f.writelines('<end>' + story.end_time_string + '</end>\n')
            for line in story.ocr:
                f.writelines(line + '\n')
    return


def main():
    with open('new_data_video_list.txt', 'r') as f:
        for line in f:
            file_name = line[:-1] 
            stories = read_in_story('tpt/' + file_name + '.tpt.topic.chunk_triplets.dat')
            stories = add_ocr(stories, 'ocr/' + file_name + '.ocr.jpg.ocr')
            save_ocr(stories)
            print 'Finish ' + file_name
    return

if __name__ == '__main__':
    main()
