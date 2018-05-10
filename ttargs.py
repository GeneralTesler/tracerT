import argparse

banner='''                                   ___________
    ___                           |           |
 __|   |__ ____ ____ _____ _____ _|___     ___|
|         |  __|    |     |     | ` __|   |
'--|   |-;' | | | | |  ===| |___|  |  |   |
   |___| |__| |______\____|_____|__|  |___|
        "You'll never CAPTCHA me alive"
'''

''''parent parser'''
parser = argparse.ArgumentParser(prog='tracerT')
subparsers = parser.add_subparsers()

''''GHDB parser'''
parser_ghdb = subparsers.add_parser('ghdb',
                                    help='extract dorks from GHDB')
parser_ghdb.add_argument('-c', 
                         '--category',
                         type=int,
                         dest='category',
                         help='GHDB dork category. Use the --cat-list for category list',
                         required=False)
parser_ghdb.add_argument('--cat-list',
                         action='store_true',
                         dest='listbool',
                         help='show categories list',
                         required=False)
parser_ghdb.add_argument('-o', 
                         '--out-file', 
                         type=str,
                         dest='outdork',
                         help='output file for dorks (CSV)',
                         required=False)

'''CSE parser'''
parser_cse = subparsers.add_parser('cse',
                                   help='search Google for dorks')
parser_cse.add_argument('-x',
                        '--cse',
                        dest='cse', 
                        type=str, 
                        help='CSE ID',
                        required=True)
parser_cse.add_argument('-a', 
                        '--api', 
                        dest='api',
                        type=str, 
                        help='API key',
                        required=True)
parser_cse.add_argument('-i', 
                        '--ilist',
                        dest='ilist',
                        type=str,
                        help='input list of dorks',
                        required=True)
parser_cse.add_argument('-f', 
                        '--format',
                        dest='fformat',
                        type=str,
                        help='input list format (txt,csv)',
                        required=False)
parser_cse.add_argument('-t', 
                        '--target',
                        dest='target',
                        type=str,
                        help='target domain',
                        required=True)
parser_cse.add_argument('--skip-lc',
                        dest='skip',
                        action='store_true',
                        help='skip line count for input file',
                        required=False)
parser_cse.add_argument('-o', 
                         '--out-file', 
                         type=str,
                         dest='outres',
                         help='output file for search results (CSV)',
                         required=True)

''''Annotations parser'''
parser_tsv = subparsers.add_parser('tsv',
                                    help='generate a CSE config file')
parser_tsv.add_argument('-x',
                        '--cse',
                        dest='cseconf', 
                        type=str, 
                        help='CSE ID',
                        required=True)
parser_tsv.add_argument('-o', 
                         '--out-file', 
                         type=str,
                         dest='outconf',
                         help='output file for config',
                         required=True)
parser_tsv.add_argument('-i', 
                        '--itld',
                        dest='itld',
                        type=str,
                        help='comma separated TLDs',
                        required=True)