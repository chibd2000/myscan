# coding=utf-8
# @Author   : zpchcbd HG team
# @blog     : https://www.cnblogs.com/zpchcbd/
# @Time     : 2021-11-20 14:07
import copy
from difflib import get_close_matches, _nlargest
from difflib import SequenceMatcher


# 自己封装了一个用于处理相似度匹配的一个类,用作于域名探测FUZZ 配合 fuff

class MyDifflib:
    @staticmethod
    def getCloseMatchContent(matched, matchList, n=1000, cutoff=0.8):
        return get_close_matches(matched, matchList, n, cutoff)

    @staticmethod
    def getCompareBeforeAfterIndex(matchA, matchB):
        def getCompareBeforeIndex(maxLen, matchA, matchB):
            for i in range(maxLen):
                if matchA[i] != matchB[i]:
                    return i

        def getCompareAfterIndex(maxLen, matchA, matchB):
            for i in range(1, maxLen):
                if matchA[-i] != matchB[-i]:
                    # 这种如果匹配到的话，那么不同的地方就是在中间部分
                    return maxLen - i + 1 + 1
            # 这种情况不同的地方就是在开头部分
            _maxLen = len(matchA) if len(matchA) > len(matchB) else len(matchB)
            return _maxLen - len(matchA)

        maxLen = len(matchB) if len(matchA) > len(matchB) else len(matchA)
        print(getCompareBeforeIndex(maxLen, matchA, matchB), getCompareAfterIndex(maxLen, matchA, matchB) - 1)
        return matchB[getCompareBeforeIndex(maxLen, matchA, matchB):getCompareAfterIndex(maxLen, matchA, matchB) - 1]

        # print([i for i in reversed(range(maxLen)) if matchA[i] != matchB[i]][0])
        # return [i for i in range(maxLen) if matchA[i] == matchB[i]][-1], \
        #        [i for i in reversed(range(maxLen)) if matchA[i] != matchB[i]][0]

    @staticmethod
    def getCloseMatchIndex(word, possibilities, n=1000, cutoff=0.8):
        # 改成get_close_matches取下标索引的
        if not n > 0:
            raise ValueError("n must be > 0: %r" % (n,))
        if not 0.0 <= cutoff <= 1.0:
            raise ValueError("cutoff must be in [0.0, 1.0]: %r" % (cutoff,))
        result = []
        s = SequenceMatcher()
        s.set_seq2(word)
        dcPossibilities = copy.deepcopy(possibilities)
        for idx, x in enumerate(dcPossibilities):
            # if x == word:
            #     possibilities.__delitem__(idx)
            #     continue
            s.set_seq1(x)
            if s.real_quick_ratio() >= cutoff and \
                    s.quick_ratio() >= cutoff and \
                    s.ratio() >= cutoff:
                result.append((s.ratio(), idx))

        # Move the best scorers to head of list
        result = _nlargest(n, result)

        # Strip scores for the best n matches
        return [x for score, x in result]


if __name__ == '__main__':
    resList = []

    domainList = [
        'www-gra.huolala.cn'
        , 'e.huolala.cn'
        , 'www.huolala.cn'
        , 'act.huolala.cn'
        , 'webapp.huolala.cn'
        , 'uappweb.huolala.cn'
        , 'charter.huolala.cn'
        , 'e-crm-oss-cn-shenzhen.huolala.cn'
        , 's-oms.huolala.cn'
        , 'static-express.huolala.cn'
        , 'oms.huolala.cn'
        , 'csc-online-stg.huolala.cn'
        , 'van-static.huolala.cn'
        , 'uba.huolala.cn'
        , 'csc-online.huolala.cn'
        , 'open.huolala.cn'
        , 'oimg.huolala.cn'
        , 'lalamc.huolala.cn'
        , 'wuliu.huolala.cn'
        , 'llsrc.huolala.cn'
        , 'ap2.huolala.cn'
        , 'csc-online-gra.huolala.cn'
        , 'latin.huolala.cn'
        , 'latin-pre.huolala.cn'
        , 'ops.huolala.cn'
        , 'ops2.huolala.cn'
        , 'oms2.huolala.cn'
        , 'e-pre.huolala.cn'
        , 'oimg-stg.huolala.cn'
        , 'www-pre.huolala.cn'
        , 'wuliu-gra.huolala.cn'
        , '1.1.1.1'
        , '11.1.1.1']

    # 这种写不出来，只能进行匹配相似度了，[FUZZ]的自己观察下
    # domainIndex = 0
    # while domainIndex <= 0:
    #     current = domainList[domainIndex]
    #     goodIndexList = MyDifflib.getCloseMatchIndex(current, domainList, n=1000, cutoff=0.6)
    #     goodContentList = MyDifflib.getCloseMatchContent(current, domainList, n=1000, cutoff=0.6)
    #     currentResultList = []
    #     for index in reversed(sorted(goodIndexList)):
    #         currentResultList.append(domainList[index])
    #         if current in domainList[index]:
    #             del domainList[index]
    #     print(currentResultList)
    #     for _ in currentResultList:
    #         if current == _:
    #             continue
    #         replaceString = MyDifflib.getCompareBeforeAfterIndex(current, _)
    #         resList.append(_.replace(replaceString, '[FUZZ]'))
    #     domainIndex += 1
    # print(list(set(resList)))
    domain = 'zjhu.edu.cn'
    domainList = [i for i in domainList if domain in i]
    domainIndex = 0
    while domainIndex < len(domainList):
        current = domainList[domainIndex]
        goodIndexList = MyDifflib.getCloseMatchIndex(current, domainList, n=10000, cutoff=0.8)
        currentResultList = []
        for index in reversed(sorted(goodIndexList)):
            currentResultList.append(domainList[index])
            # if current in domainList[index]:
            del domainList[index]
        resList.append(currentResultList)
        domainIndex += 1
    for _ in resList:
        print(_)
    # print(resList)