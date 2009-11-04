import sys
import inspect
from time import clock

all = ['begin', 'end', 'print_stats', 'bind', 'FineProfiler']

class FineGrainProfiler(object):
    timings = {}
    lines_stats   = {}
    enabled = {}

    def __init__(self):
        self.bind()

    def bind(self):
        sys.settrace(self.trace_func)

    def trace_func(self,frame,event,arg):
        code = frame.f_code
        fn = (code.co_filename, code.co_name)
        if fn in self.enabled:
            if event == 'line':
                cur = self.enabled[fn]
                if cur:
                    ln = cur[0][1]
                    if (fn, ln) not in self.lines_stats:
                        if cur[0][3]:
                            code_line = cur[0][3][cur[0][4]]
                        else:
                            code_line = 'UNKNOWN'
                        self.lines_stats.update({(fn,ln): [1,clock() - cur[1], code_line]})
                    else:
                        line_stats = self.lines_stats[(fn, ln)]
                        line_stats[0] += 1
                        line_stats[1] += clock() - cur[1]
                self.enabled[fn] = [inspect.getframeinfo(frame), clock()]
            elif event == 'return':
                del self.enabled[fn]
        return self.trace_func

    def begin(self):
        code = inspect.currentframe().f_back.f_code
        fn = (code.co_filename, code.co_name)
        if fn not in self.enabled:
            self.enabled.update({fn: None})
            self.bind()

    def end(self):
        code = inspect.currentframe().f_back.f_code
        fn = (code.co_filename, code.co_name)
        if fn in self.enabled:
            del self.enabled[fn]

    def print_stats(self):
        columns = [15,15,40]
        formater = lambda lst: ' '.join([str(lst[i]).ljust(columns[i]) for i in
                                                               range(len(lst))])
        titles = ["Time(ms)","Hits","Line"]
        print formater(titles)
        print formater(['-'*i for i in columns])
        for loc, stats in sorted(self.lines_stats.iteritems(),
                      lambda x,y: cmp(y[1][1],x[1][1]) or cmp(x[1][0],y[1][0])):
            print formater(["%15f" % (stats[1]*1000),str(stats[0]).rjust(columns[1]), "%s:%s@%d>%s" % (loc[0][0],
                                                                loc[0][1],
                                                                loc[1],
                                                            stats[2].strip())])

fgp = FineGrainProfiler()
begin = fgp.begin
end   = fgp.end
print_stats = fgp.print_stats
bind = fgp.bind

if __name__ == '__main__':
    def test():
        begin()
        [i for i in range(1000)]
        [i for i in range(10000)]
        end()
    test()
    print_stats()
