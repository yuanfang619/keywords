import jieba, jieba.analyse

def text_split(text):
    return text.upper().strip().split('\n')

def extract_keywords(text, method = "tfidf", num = 10, pos = ['ns', 'n', 'vn', 'v']):
    if method == 'tfidf':
        kw = jieba.analyse.extract_tags(text, num, withWeight = True, allowPOS=pos)
    elif method == 'textrank':
        kw = jieba.analyse.textrank(text, num, withWeight = True, allowPOS=pos)
    return {w[0]: w[1] for w in kw}

def seg_text(text_list, HMM=True):
    import jieba
    seg = []
    for t in text_list:
        try:
            seg.append(" ".join(jieba.cut(t, HMM=HMM)).split())
        except:
            seg.append(" ")
    seg_list = [[w for w in s] for s in seg]
    return seg_list

def filter_words(keywords, text):
    text_list = text_split(text)
    seg_list = seg_text(text_list)
    kw_list = keywords.keys()
    return [[w for w in seg if w in kw_list] for seg in seg_list]

def words_count(word, word_list, text):
    words_count = {w: list(sum(word_list, [])).count(w) for w in word}
    for key in words_count.keys():
        if words_count[key] == 0:
            words_count[key] = text.count(key)
    return words_count

def keywords_count(keywords, filter_list, text):
    kw_list = keywords.keys()
    kw_count = words_count(kw_list, filter_list, text)
    filter_list_unique = [list(set(li)) for li in filter_list]
    kw_user = words_count(kw_list, filter_list_unique, text)
    return kw_count, kw_user

def merge_keywords(kw_weight, kw_count, kw_user):
    keywords = {}
    for key, value in kw_weight.items():
        keywords.setdefault(key, {})['weight'] = value
        keywords.setdefault(key, {})['count'] = kw_count.get(key, 0)
        keywords.setdefault(key, {})['user_num'] = kw_user.get(key, 0)
    return keywords

def generate_network(words_list):
    src = []
    dst = []
    for s in words_list:
        i = 0
        s2 = list(set(s))
        s2.sort()
        while (i < len(s2)):
            j = i + 1
            while (j < len(s2)):
                src.append(s2[i])
                dst.append(s2[j])
                j += 1
            i += 1
    vertice = {}
    for v in list(set(src + dst)):
        vertice[v] = src.count(v) + dst.count(v)
    network = {}
    i = 0
    while i < len(src):
        key = src[i] + "|" + dst[i]
        network[key] = network.get(key, 0) + 1
        i = i + 1
    return network, vertice

def text_processing(text, method='tfidf', num=10, pos=['ns', 'n', 'vn', 'v']):
    kw = extract_keywords(upper(text.strip()), method='tfidf', num=num, pos=pos)
    filter_list = filter_words(kw, text)
    kw_count, kw_user = keywords_count(kw, filter_list, text)
    keywords = merge_keywords(kw, kw_count, kw_user)
    filter_list_unique = [list(set(li)) for li in filter_list]
    network, vertice = generate_network(filter_list_unique)
    #print " ".join(keywords.keys())
    return keywords, network, vertice
