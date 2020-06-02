# utf-8
import sys
import multiprocessing


# 重写queue队列类
class Link():
    ''' No repeat link '''

    def __init__(self):
        self.map = {}
        self.tail = "head"
        self.map["head"] = {"stat": 0, "next": "null"}

    def __contains__(self, key):
        return key in self.map

    def __len__(self):
        return len(self.map) - 1

    def isEmpty(self):
        if self.getHead() == "null":
            return True
        else:
            return False

    def clearLink(self):
        self.map.clear()

    def getTail(self):
        return self.tail

    def getHead(self):
        return self.map["head"]["next"]

    def add(self, string):
        #      self.test_output("OrderedMapQueue")
        args = string.split('\t')
        item = args[0]
        stat = args[1]
        if item not in self.map:
            self.map[item] = {"stat": stat, "next": "null"}
            self.map[self.tail]["next"] = item
            self.tail = item

    def pop(self):
        if not self.isEmpty():
            head_task = self.map["head"]["next"]
            rt_value = "%s\t%s" % (head_task, self.map[head_task]["stat"])
            self.map["head"]["next"] = self.map[head_task]["next"]
            del self.map[head_task]
            if head_task == self.tail:
                self.tail = "head"
            return rt_value
        return None

    def test_output(self, name=""):
        print(sys.stderr, name)
        print(sys.stderr, "-" * 10 + "TEST_OUTPUT" + "-" * 10)
        print(sys.stderr, "Tail: %s\nHead: %s\nLength: %s" % (self.getTail(), self.getHead(), self.__len__()))
        head = "head"
        while head != "null":
            print(sys.stderr, "%s\t%s\t%s" % (head, self.map[head]["stat"], self.map[head]["next"]))
            head = self.map[head]["next"]
        print(sys.stderr, "-" * 31)


class OrderedMapQueue(multiprocessing.Manager().Queue()):

    def _init(self, maxsize=0):
        self.queue = Link()

    def _put(self, item):

        self.queue.add(item)

    def _get(self):
        return self.queue.pop()

    def _qsize(self):
        return self.queue.__len__()


if __name__ == "__main__":
    # mylink = Link()
    # mylink.add("task1","-1")
    # mylink.add("task2","-2")
    # mylink.add("task3","-1")
    # mylink.test_output()
    multiprocessing.freeze_support()
    myqueue = OrderedMapQueue()
    myqueue.put("task2\t-2")
    myqueue.put("task3\t-1")
    myqueue.put("task1\t-2")
    myqueue.put("task3\t-1")
    myqueue.put("task3\t-2")
    print(myqueue.get())
    print(myqueue.get())
    print(myqueue.get())
    print(myqueue.get())
    print(myqueue.get())
    print(myqueue.get())