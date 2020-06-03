w# coding=utf-8

# def parse_args():
#     import argparse
#     parser = argparse.ArgumentParser()
#     parser.add_argument('-d', '--domain', type=str, required=True, help="Target domain.")
#     parser.add_argument('-o', '--output', type=str, help="Output file.")
#     return parser.parse_args()
#
#
# def main():
#     args = parse_args()
#     print(args.accumulate(args.integers))



if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('integers', metavar='N', type=int, nargs='+',
                        help='an integer for the accumulator')
    parser.add_argument('--sum', dest='accumulate', action='store_const',
                        const=sum, default=max,
                        help='sum the integers (default: find the max)')

    args = parser.parse_args()
    print(args.accumulate(args.integers))
